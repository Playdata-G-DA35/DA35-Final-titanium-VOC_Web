import calendar
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Count, Case, When, Value, CharField, FloatField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from .models import ProductDetails, ProductReview
from django.contrib.auth.decorators import login_required
import os
import base64
@csrf_exempt
def get_filtered_reviews(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        start_period = data.get('start_period')
        end_period = data.get('end_period')
        category = data.get('category')
        chart_type = data.get('chart_type')

        start_date = f"{start_period}-01"
        end_year, end_month = map(int, end_period.split('-'))
        last_day_of_month = calendar.monthrange(end_year, end_month)[1]
        end_date = f"{end_period}-{last_day_of_month}"

        
        category = category[0]
        # 필터링된 리뷰 쿼리
        reviews = ProductReview.objects.filter(
            date__range=[start_date, end_date],
            product_id__in=ProductDetails.objects.filter(category=category).values('id')
        )

        # 브랜드 그룹 및 카테고리 설정
        reviews = reviews.annotate(
            brand_group=Case(
                When(product_id__brand='무신사 스탠다드', then=Value('무신사 스탠다드')),
                When(product_id__brand__in=['에잇세컨즈', '스파오', '탑텐'], then=Value('SPA')),
                default=Value('기타'),
                output_field=CharField(),
            ),
            category=Case(
                When(product_id__category=category, then=Value(category)),
                default=Value('Unknown'),
                output_field=CharField(),
            )
        )

        # 차트 타입에 따른 그룹핑
        if chart_type == 'daily':
            reviews = reviews.annotate(period=TruncDay('date'))
        elif chart_type == 'weekly':
            reviews = reviews.annotate(period=TruncWeek('date'))
        elif chart_type == 'monthly':
            reviews = reviews.annotate(period=TruncMonth('date'))

        # 리뷰 카운트
        review_counts = reviews.values('period', 'brand_group', 'category').annotate(
            review_count=Count('id')
        ).order_by('period', 'brand_group', 'category')

        return JsonResponse(list(review_counts), safe=False)
    else:
        return render(request, 'review_basic_analysis.html')


@csrf_exempt
def get_gender_distribution(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        start_period = data.get('start_period')
        end_period = data.get('end_period')
        category = data.get('category')

        # 날짜 포맷 변경 (YYYY-MM -> YYYY-MM-DD)
        start_date = f"{start_period}-01"
        end_year, end_month = map(int, end_period.split('-'))
        last_day_of_month = calendar.monthrange(end_year, end_month)[1]
        end_date = f"{end_period}-{last_day_of_month}"

        category = category[0]
        # 필터링된 리뷰 쿼리
        reviews = ProductReview.objects.filter(
            date__range=[start_date, end_date],
            product_id__in=ProductDetails.objects.filter(category=category).values('id')
        )

        # 브랜드 그룹 설정
        reviews = reviews.annotate(
            brand_group=Case(
                When(product_id__brand='무신사 스탠다드', then=Value('무신사 스탠다드')),
                When(product_id__brand__in=['에잇세컨즈', '스파오', '탑텐'], then=Value('SPA')),
                default=Value('기타'),
                output_field=CharField(),
            ),
            category=Case(
                When(product_id__category__isnull=False, then=Value(category)),
                default=Value('Unknown'),
                output_field=CharField(),
            )
        )

        # 성별 컬럼 값의 카운트
        gender_counts = reviews.values('brand_group', 'category', 'sex').annotate(count=Count('id'))
        
        # 브랜드 그룹별 성별 카운트 집계
        result = {}
        for entry in gender_counts:
            brand_group = entry['brand_group']
            category = entry['category']
            sex = entry['sex']
            count = entry['count']

            if (brand_group, category) not in result:
                result[(brand_group, category)] = {'Female_count': 0, 'Male_count': 0}

            if sex == 0:
                result[(brand_group, category)]['Female_count'] += count
            elif sex == 1:
                result[(brand_group, category)]['Male_count'] += count
        
        # 비율 계산
        final_result = []
        for (brand_group, category), counts in result.items():
            total_count = counts['Female_count'] + counts['Male_count']
            if total_count > 0:
                female_ratio = round((counts['Female_count'] / total_count) * 100, 2)
                male_ratio = round((counts['Male_count'] / total_count) * 100, 2)
            else:
                female_ratio = 0
                male_ratio = 0

            final_result.append({
                'brand_group': brand_group,
                'category': category,
                'Female_count': counts['Female_count'],
                'Male_count': counts['Male_count'],
                'Female_ratio': f"{female_ratio}%",
                'Male_ratio': f"{male_ratio}%"
            })

        # JSON 응답 반환
        return JsonResponse(final_result, safe=False)
    else:
        return HttpResponseBadRequest("Invalid request method")



@login_required
def review_basic(request):
    return render(request, 'review_basic_analysis.html')


@csrf_exempt
def get_review_wordcloud(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")

        start_period = data.get('start_period')  # 예: "2024-01"
        end_period = data.get('end_period')      # 예: "2024-08"
        category = data.get('category')          # 예: "하의"
        brand = data.get('brand')                # 예: "무신사 스탠다드"

        # 브랜드를 적절한 식별자로 매핑
        brand_map = {
            '무신사 스탠다드': 'musinsa',
            'SPA': 'spa'
        }
        brand_id = brand_map.get(brand, 'default')

        # 카테고리를 적절한 식별자로 매핑
        category_map = {
            '상의': 'top',
            '바지': 'bottom',
            '아우터': 'outter'
        }
        category_id = category_map.get(category, 'default')

        # 시작 월과 종료 월 설정
        start_year, start_month = map(int, start_period.split('-'))
        end_year, end_month = map(int, end_period.split('-'))

        # 월별 워드클라우드 파일들을 가져오기
        images = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                    continue

                # 파일명 생성
                filename = f"{brand_id}_{category_id}_{month}_wordcloud.png"
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'wordcloud', filename)

                # 이미지 파일이 존재하면 리스트에 추가
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')  # base64 인코딩
                        images.append({
                            'filename': filename,
                            'image': encoded_string
                        })

        if images:
            return JsonResponse({'images': images}, safe=False)
        else:
            return HttpResponseBadRequest("No images found for the specified period")

    return HttpResponseBadRequest("Invalid request method")

from collections import Counter
import pandas as pd
from .models import ProductDetails, ProductReview  # 모델 임포트


@csrf_exempt
def get_word_frequency_by_price_range(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data")


        try:
            start_period = data.get('start_period')
            end_period = data.get('end_period')
            category = data.get('category')

            start_date = f"{start_period}-01"
            end_year, end_month = map(int, end_period.split('-'))
            last_day_of_month = calendar.monthrange(end_year, end_month)[1]
            end_date = f"{end_period}-{last_day_of_month}"

            price_ranges = ['1~2만원대', '3~4만원대', '5만원대 이상']
            result = {}
            
            for price_range in price_ranges:
                musinsa_reviews = ProductReview.objects.filter(
                    date__range=[start_date, end_date],
                    product_id__in=ProductDetails.objects.filter(
                        category=category,
                        brand='무신사 스탠다드',
                        price_range=price_range
                    ).values('id')
                )

                spa_reviews = ProductReview.objects.filter(
                    date__range=[start_date, end_date],
                    product_id__in=ProductDetails.objects.filter(
                        category=category,
                        brand__in=['에잇세컨즈', '스파오', '탑텐'],
                        price_range=price_range
                    ).values('id')
                )

                if not musinsa_reviews.exists() and not spa_reviews.exists():
                    continue

                musinsa_tokens = " ".join([review.review_tokens for review in musinsa_reviews if review.review_tokens]).split(',')
                spa_tokens = " ".join([review.review_tokens for review in spa_reviews if review.review_tokens]).split(',')

                musinsa_counter = Counter(musinsa_tokens)
                spa_counter = Counter(spa_tokens)

                musinsa_common = musinsa_counter.most_common(5)
                spa_common = spa_counter.most_common(5)

                musinsa_df = pd.DataFrame(musinsa_common, columns=["단어명", "빈도수"])
                spa_df = pd.DataFrame(spa_common, columns=["단어명", "빈도수"])

                result[price_range] = {
                    "musinsa": musinsa_df.to_dict(orient='records'),
                    "spa": spa_df.to_dict(orient='records')
                }

            return JsonResponse(result, safe=False)

        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {str(e)}")

    return HttpResponseBadRequest("Invalid request method")

