import calendar
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponse
from django.db.models import Count, Case, When, Value, CharField, FloatField, Sum
from django.db.models.functions import TruncMonth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import datetime
from review_basic_analysis.models import ProductDetails, ProductReview

def custom_json_response(data, status=200):
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        content_type='application/json',
        status=status
    )

@csrf_exempt
def sentiment_analysis_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        start_period = data.get('start_period')
        end_period = data.get('end_period')
        category = data.get('category')

        start_date = f"{start_period}-01"
        end_year, end_month = map(int, end_period.split('-'))
        last_day_of_month = calendar.monthrange(end_year, end_month)[1]
        end_date = f"{end_period}-{last_day_of_month}"

        # 필터링된 리뷰 쿼리
        reviews = ProductReview.objects.filter(
            date__range=[start_date, end_date],
            product_id__in=ProductDetails.objects.filter(category=category).values('id')
        )

        # 브랜드 그룹 설정 및 월별 데이터 그룹핑
        reviews = reviews.annotate(
            brand_group=Case(
                When(product_id__brand='무신사 스탠다드', then=Value('무신사 스탠다드')),
                When(product_id__brand__in=['에잇세컨즈', '스파오', '탑텐'], then=Value('SPA')),
                default=Value('기타'),
                output_field=CharField(),
            )
        ).annotate(
            period=TruncMonth('date')
        )

        # 긍정 및 부정 리뷰 카운트 및 비율 계산
        emotions = reviews.values('brand_group', 'product_id__category').annotate(
            positive_count=Sum(Case(When(emotions__iexact='positive', then=1))),
            negative_count=Sum(Case(When(emotions__iexact='negative', then=1))),
            positive_ratio=Sum(Case(When(emotions__iexact='positive', then=1.0), default=0.0, output_field=FloatField())) / Count('id'),
            negative_ratio=Sum(Case(When(emotions__iexact='negative', then=1.0), default=0.0, output_field=FloatField())) / Count('id')
        ).order_by('brand_group', 'product_id__category')

        # 데이터 포맷 수정
        emotion_data = []
        for emotion in emotions:
            emotion_data.append({
                'start_period': start_period,
                'end_period': end_period,
                'brand': emotion['brand_group'],
                'category': emotion['product_id__category'],
                'positive_count': emotion['positive_count'] or 0,
                'negative_count': emotion['negative_count'] or 0,
                'positive_ratio': emotion['positive_ratio'] or 0,
                'negative_ratio': emotion['negative_ratio'] or 0
            })

        return JsonResponse(emotion_data, safe=False)
    else:
        return render(request, 'review_sentiment_analysis.html')
    

@csrf_exempt
def get_top_reviews(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        start_period = data.get('start_period')
        end_period = data.get('end_period')
        category = data.get('category')
        emotions = data.get('emotions')  # Positive 또는 Negative

        if not emotions or emotions.lower() not in ['positive', 'negative']:
            return HttpResponseBadRequest("Invalid or missing 'emotions' field")

        start_date = f"{start_period}-01"
        end_year, end_month = map(int, end_period.split('-'))
        last_day_of_month = calendar.monthrange(end_year, end_month)[1]
        end_date = f"{end_period}-{last_day_of_month}"

        # 필터링된 리뷰 쿼리
        reviews = ProductReview.objects.filter(
            date__range=[start_date, end_date],
            product_id__in=ProductDetails.objects.filter(category=category).values('id'),
            emotions__iexact=emotions
        )

        # 브랜드 그룹 설정
        reviews = reviews.annotate(
            brand_group=Case(
                When(product_id__brand='무신사 스탠다드', then=Value('무신사 스탠다드')),
                When(product_id__brand__in=['에잇세컨즈', '스파오', '탑텐'], then=Value('SPA')),
                default=Value('기타'),
                output_field=CharField(),
            )
        )

        # 무신사 스탠다드 상위 5개 리뷰
        musinsa_reviews = reviews.filter(brand_group='무신사 스탠다드').order_by('-helpful')[:5]
        musinsa_review_data = {
            f'musinsa_{emotions.lower()}_top{index+1}_review': {
                'review': review.review,
                'helpful': review.helpful
            }
            for index, review in enumerate(musinsa_reviews)
        }

        # SPA 상위 5개 리뷰
        spa_reviews = reviews.filter(brand_group='SPA').order_by('-helpful')[:5]
        spa_review_data = {
            f'spa_{emotions.lower()}_top{index+1}_review': {
                'review': review.review,
                'helpful': review.helpful
            }
            for index, review in enumerate(spa_reviews)
        }

        # 데이터를 합침
        review_data = {
            'start_period': start_period,
            'end_period': end_period,
            'brand': '무신사 스탠다드 & SPA',
            **musinsa_review_data,
            **spa_review_data,
        }

        return JsonResponse(review_data, safe=False)
    else:
        return render(request, 'review_sentiment_analysis.html')
    
@csrf_exempt
def get_top_topics(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_period = data.get('start_period')
            end_period = data.get('end_period')
            category = data.get('category')
            selected_topics = data.get('selected_topics', [])

            if not all([start_period, end_period, category, selected_topics]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            reviews = ProductReview.objects.filter(
                date__range=[f"{start_period}-01", f"{end_period}-31"],
                product_id__category=category
            ).select_related('product_id').annotate(
                brand_group=Case(
                    When(product_id__brand='무신사 스탠다드', then=Value('무신사 스탠다드')),
                    When(product_id__brand__in=['에잇세컨즈', '스파오', '탑텐'], then=Value('SPA')),
                    default=Value('기타'),
                    output_field=CharField(),
                )
            ).order_by('-helpful')

            result = {
                'start_period': start_period,
                'end_period': end_period,
                'category': category,
                'musinsa_reviews': [],
                'spa_reviews': []
            }

            musinsa_count = 0
            spa_count = 0

            for review in reviews:
                try:
                    topic_dict = json.loads(review.topic.replace("'", '"'))
                    highest_topic = max(topic_dict, key=topic_dict.get)
                    highest_score = topic_dict[highest_topic]

                    if highest_topic in selected_topics:
                        review_data = {
                            'id': review.id,
                            'brand': review.product_id.brand,
                            'category': review.product_id.category,
                            'review': review.review,
                            'helpful': review.helpful,
                            'topic': review.topic,
                            'highest_score': float(highest_score),
                            'highest_topic': highest_topic
                        }

                        if review.brand_group == '무신사 스탠다드' and musinsa_count < 5:
                            result['musinsa_reviews'].append(review_data)
                            musinsa_count += 1
                        elif review.brand_group == 'SPA' and spa_count < 5:
                            result['spa_reviews'].append(review_data)
                            spa_count += 1

                        if musinsa_count == 5 and spa_count == 5:
                            break

                except json.JSONDecodeError:
                    continue

            result['musinsa_reviews'] = sorted(result['musinsa_reviews'], key=lambda x: x['highest_score'], reverse=True)
            result['spa_reviews'] = sorted(result['spa_reviews'], key=lambda x: x['highest_score'], reverse=True)

            return custom_json_response(result)

        except json.JSONDecodeError:
            return custom_json_response({"error": "Invalid JSON in request"}, status=400)
        except Exception as e:
            return custom_json_response({"error": str(e)}, status=500)

    return custom_json_response({"error": "Method not allowed"}, status=405)

@csrf_exempt
def topic_analysis_radial(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_period = data.get('start_period')
            end_period = data.get('end_period')
            category = data.get('category')

            if not all([start_period, end_period, category]):
                return custom_json_response({"error": "Missing required fields"}, status=400)

            start_date = datetime.datetime.strptime(start_period, "%Y-%m").date()
            end_year, end_month = map(int, end_period.split('-'))
            end_date = datetime.date(end_year, end_month, 1) + datetime.timedelta(days=calendar.monthrange(end_year, end_month)[1] - 1)

            reviews = ProductReview.objects.filter(
                date__range=[start_date, end_date],
                product_id__category=category
            ).select_related('product_id').annotate(
                brand_group=Case(
                    When(product_id__brand='무신사 스탠다드', then=Value('무신사 스탠다드')),
                    When(product_id__brand__in=['에잇세컨즈', '스파오', '탑텐'], then=Value('SPA')),
                    default=Value('기타'),
                    output_field=CharField(),
                )
            )

            musinsa_totals = {'사이즈': 0, '재질': 0, '디자인': 0, '만족도': 0, '두께감': 0}
            spa_totals = {'사이즈': 0, '재질': 0, '디자인': 0, '만족도': 0, '두께감': 0}
            musinsa_count = 0
            spa_count = 0

            for review in reviews:
                try:
                    if review.topic is None:
                        continue  # Skip reviews with None topic
                    topic_dict = json.loads(review.topic.replace("'", '"'))

                    if review.brand_group == '무신사 스탠다드':
                        musinsa_count += 1
                        for key in musinsa_totals:
                            musinsa_totals[key] += topic_dict.get(key, 0)
                    elif review.brand_group == 'SPA':
                        spa_count += 1
                        for key in spa_totals:
                            spa_totals[key] += topic_dict.get(key, 0)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing review {review.id}: {str(e)}")
                    continue

            musinsa_averages = {k: round(v / musinsa_count, 2) if musinsa_count > 0 else 0 for k, v in musinsa_totals.items()}
            spa_averages = {k: round(v / spa_count, 2) if spa_count > 0 else 0 for k, v in spa_totals.items()}

            result = {
                'start_period': start_period,
                'end_period': end_period,
                'category': category,
                'musinsa_averages': musinsa_averages,
                'spa_averages': spa_averages,
            }

            return custom_json_response(result)

        except json.JSONDecodeError:
            return custom_json_response({"error": "Invalid JSON in request"}, status=400)
        except Exception as e:
            return custom_json_response({"error": str(e)}, status=500)

    return custom_json_response({"error": "Method not allowed"}, status=405)
