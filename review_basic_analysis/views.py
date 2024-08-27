import calendar
import json
import os
import base64
from collections import Counter
import pandas as pd
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Count, Case, When, Value, CharField, FloatField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ProductDetails, ProductReview


# Helper Functions
def parse_request_body(request):
    """Request body에서 JSON 데이터를 파싱"""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None


def get_date_range(data):
    """시작과 종료 날짜를 계산"""
    start_period = data.get('start_period')
    end_period = data.get('end_period')

    start_date = f"{start_period}-01"
    end_year, end_month = map(int, end_period.split('-'))
    last_day_of_month = calendar.monthrange(end_year, end_month)[1]
    end_date = f"{end_period}-{last_day_of_month}"

    return start_date, end_date


def filter_reviews_by_date_and_category(start_date, end_date, category):
    """주어진 날짜 범위와 카테고리로 리뷰를 필터링"""
    return ProductReview.objects.filter(
        date__range=[start_date, end_date],
        product_id__in=ProductDetails.objects.filter(category=category).values('id')
    )


def annotate_reviews(reviews, category):
    """리뷰에 브랜드 그룹과 카테고리 필드를 주석으로 추가"""
    return reviews.annotate(
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


def calculate_gender_distribution(gender_counts):
    """성별 분포를 계산"""
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

    return final_result


# Views
@csrf_exempt
def get_filtered_reviews(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        start_date, end_date = get_date_range(data)
        category = data.get('category')[0]

        reviews = filter_reviews_by_date_and_category(start_date, end_date, category)
        reviews = annotate_reviews(reviews, category)

        chart_type = data.get('chart_type')
        if chart_type == 'daily':
            reviews = reviews.annotate(period=TruncDay('date'))
        elif chart_type == 'weekly':
            reviews = reviews.annotate(period=TruncWeek('date'))
        elif chart_type == 'monthly':
            reviews = reviews.annotate(period=TruncMonth('date'))

        review_counts = reviews.values('period', 'brand_group', 'category').annotate(
            review_count=Count('id')
        ).order_by('period', 'brand_group', 'category')

        return JsonResponse(list(review_counts), safe=False)
    else:
        return render(request, 'review_basic_analysis.html')


@csrf_exempt
def get_gender_distribution(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        start_date, end_date = get_date_range(data)
        category = data.get('category')[0]

        reviews = filter_reviews_by_date_and_category(start_date, end_date, category)
        reviews = annotate_reviews(reviews, category)

        gender_counts = reviews.values('brand_group', 'category', 'sex').annotate(count=Count('id'))
        final_result = calculate_gender_distribution(gender_counts)

        return JsonResponse(final_result, safe=False)
    else:
        return HttpResponseBadRequest("Invalid request method")


@login_required
def review_basic(request):
    return render(request, 'review_basic_analysis.html')


@csrf_exempt
def get_review_wordcloud(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        start_period = data.get('start_period')
        end_period = data.get('end_period')
        category = data.get('category')
        brand = data.get('brand')

        brand_map = {'무신사 스탠다드': 'musinsa', 'SPA': 'spa'}
        category_map = {'상의': 'top', '바지': 'bottom', '아우터': 'outter'}
        brand_id = brand_map.get(brand, 'default')
        category_id = category_map.get(category, 'default')

        start_year, start_month = map(int, start_period.split('-'))
        end_year, end_month = map(int, end_period.split('-'))

        images = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                    continue

                filename = f"{brand_id}_{category_id}_{month}_wordcloud.png"
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'wordcloud', filename)

                if os.path.exists(image_path):
                    with open(image_path, 'rb') as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        images.append({'filename': filename, 'image': encoded_string})

        if images:
            return JsonResponse({'images': images}, safe=False)
        else:
            return HttpResponseBadRequest("No images found for the specified period")

    return HttpResponseBadRequest("Invalid request method")


@csrf_exempt
def get_word_frequency_by_price_range(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        try:
            start_date, end_date = get_date_range(data)
            category = data.get('category')

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
