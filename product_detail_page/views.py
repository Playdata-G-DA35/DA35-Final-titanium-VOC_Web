from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.db.models import Avg, Sum, Count, Case, When, IntegerField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from review_basic_analysis.models import ProductDetails, ProductReview
from django.views.decorators.csrf import csrf_exempt
import json


# custom_json_response 함수 정의
def custom_json_response(data, status=200):
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        content_type='application/json',
        status=status
    )


@csrf_exempt
def product_detail_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_name = data.get('product')
            print(f"Received product name: {product_name}")  # 디버깅용
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        if not product_name:
            return JsonResponse({"error": "Product name is missing or empty"}, status=400)

        filtered_data = ProductDetails.objects.filter(product=product_name)\
            .annotate(average_grade=Avg('productreview__grade'))\
            .values('category', 'subcategory', 'product', 'product_like', 'product_price', 'average_grade')

        if not filtered_data.exists():
            return JsonResponse({"error": "No data found for the selected product"}, status=404)

        return custom_json_response(list(filtered_data))

    else:
        return render(request, 'product_detail_page.html')


@csrf_exempt
def product_details_analysis_views(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_name = data.get('product')
            print(f"Received product name: {product_name}")  # 디버깅용
        except json.JSONDecodeError:
            return custom_json_response({"error": "Invalid JSON data"}, status=400)

        if not product_name:
            return custom_json_response({"error": "Missing 'product' field"}, status=400)

        try:
            product = ProductDetails.objects.get(product=product_name)
        except ProductDetails.DoesNotExist:
            return custom_json_response({"error": "Product not found"}, status=404)

        age_groups = {
            'views_18': product.views_18,
            'views_19_23': product.views_19_23,
            'views_24_28': product.views_24_28,
            'views_29_33': product.views_29_33,
            'views_34_39': product.views_34_39,
            'views_40': product.views_40
        }

        total_views = product.views_male + product.views_female
        male_ratio = (product.views_male / total_views * 100) if total_views > 0 else 0
        female_ratio = (product.views_female / total_views * 100) if total_views > 0 else 0

        response_data = {
            'product': product.product,
            'category': product.category,
            'subcategory': product.subcategory,
            'views': product.views,
            'age_groups': age_groups,
            'gender_views': {
                'views_male': product.views_male,
                'views_female': product.views_female,
                'male_ratio': round(male_ratio, 2),
                'female_ratio': round(female_ratio, 2),
            },
        }

        return custom_json_response(response_data)
    else:
        return render(request, 'product_detail_page.html')


@csrf_exempt
def product_details_analysis_purchases(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_name = data.get('product')
            print(f"Received product name: {product_name}")  # 디버깅용
        except json.JSONDecodeError:
            return custom_json_response({"error": "Invalid JSON data"}, status=400)

        if not product_name:
            return custom_json_response({"error": "Missing 'product' field"}, status=400)

        try:
            product = ProductDetails.objects.get(product=product_name)
        except ProductDetails.DoesNotExist:
            return custom_json_response({"error": "Product not found"}, status=404)

        age_groups = {
            'purchases_18': product.purchases_18,
            'purchases_19_23': product.purchases_19_23,
            'purchases_24_28': product.purchases_24_28,
            'purchases_29_33': product.purchases_29_33,
            'purchases_34_39': product.purchases_34_39,
            'purchases_40': product.purchases_40
        }

        total_purchases = product.purchases_male + product.purchases_female
        male_ratio = (product.purchases_male / total_purchases * 100) if total_purchases > 0 else 0
        female_ratio = (product.purchases_female / total_purchases * 100) if total_purchases > 0 else 0

        response_data = {
            'product': product.product,
            'category': product.category,
            'subcategory': product.subcategory,
            'purchases': product.purchases,
            'age_groups': age_groups,
            'gender_purchases': {
                'purchases_male': product.purchases_male,
                'purchases_female': product.purchases_female,
                'male_ratio': round(male_ratio, 2),
                'female_ratio': round(female_ratio, 2),
            },
        }

        return custom_json_response(response_data)
    else:
        return render(request, 'product_detail_page.html')


@csrf_exempt
def review_count(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data.get('product')
            chart_type = data.get('chart_type', 'daily')  # 기본값을 'daily'로 설정
            if not product_name:
                return HttpResponseBadRequest("Product name is missing.")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        try:
            reviews = ProductReview.objects.filter(product_id__product=product_name)

            if chart_type == 'daily':
                reviews = reviews.annotate(period=TruncDay('date'))
            elif chart_type == 'weekly':
                reviews = reviews.annotate(period=TruncWeek('date'))
            elif chart_type == 'monthly':
                reviews = reviews.annotate(period=TruncMonth('date'))
            else:
                return HttpResponseBadRequest("Invalid chart_type value.")

            review_counts = reviews.values('period').annotate(
                review_count=Count('id')
            ).order_by('period')

            return JsonResponse(list(review_counts), safe=False)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return render(request, 'product_detail_page.html')


@csrf_exempt
def product_topic_analysis_radial(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data.get('product')
            if not product_name:
                return HttpResponseBadRequest("Product name is missing.")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        try:
            reviews = ProductReview.objects.filter(
                product_id__product=product_name
            ).select_related('product_id')

            topic_totals = {'사이즈': 0, '재질': 0, '디자인': 0, '만족도': 0, '두께감': 0}
            review_count = 0

            for review in reviews:
                try:
                    if review.topic is None:
                        continue 
                    topic_dict = json.loads(review.topic.replace("'", '"'))

                    review_count += 1
                    for key in topic_totals:
                        topic_totals[key] += topic_dict.get(key, 0)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing review {review.id}: {str(e)}")
                    continue

            topic_averages = {k: round(v / review_count, 2) if review_count > 0 else 0 for k, v in topic_totals.items()}

            result = {
                'topic_averages': topic_averages,
            }

            return custom_json_response(result)

        except Exception as e:
            return custom_json_response({"error": str(e)}, status=500)

    return custom_json_response({"error": "Method not allowed"}, status=405)


@csrf_exempt
def product_sentiment_analysis_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        product_name = data.get('product')
        if not product_name:
            return HttpResponseBadRequest("Product name is missing.")

        reviews = ProductReview.objects.filter(
            product_id__product=product_name
        )

        emotions = reviews.aggregate(
            positive_count=Sum(Case(When(emotions__iexact='positive', then=1), default=0, output_field=IntegerField())),
            negative_count=Sum(Case(When(emotions__iexact='negative', then=1), default=0, output_field=IntegerField())),
            total_count=Count('id')
        )

        positive_count = emotions['positive_count'] or 0
        negative_count = emotions['negative_count'] or 0
        total_count = emotions['total_count'] or 1  # 0으로 나누는 것을 방지하기 위해 1로 설정

        positive_ratio = positive_count / total_count
        negative_ratio = negative_count / total_count

        emotion_data = {
            'product': product_name,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio
        }

        return custom_json_response(emotion_data)
    else:
        return render(request, 'product_detail_page.html')
