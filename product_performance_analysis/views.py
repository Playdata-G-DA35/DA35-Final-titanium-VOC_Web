from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Case, When, Value, CharField, Sum, Avg, FloatField
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from django.contrib.auth.decorators import login_required
from review_basic_analysis.models import ProductDetails, ProductReview

def parse_request_body(request):
    """Request body에서 JSON 데이터를 파싱하고, 유효성을 검사"""
    try:
        data = json.loads(request.body)
        return data
    except json.JSONDecodeError:
        return None

def validate_category_and_subcategory(data):
    """카테고리와 서브카테고리 필드를 검증"""
    category = data.get('category')
    subcategories = data.get('subcategory', [])
    if not category or not subcategories:
        return None, None
    if isinstance(subcategories, list):
        subcategory_string = ", ".join(subcategories)
    else:
        subcategory_string = subcategories
    return category, subcategory_string

def get_products(category, subcategories, brand='무신사 스탠다드'):
    """카테고리와 서브카테고리로 제품을 필터링합니다."""
    return ProductDetails.objects.filter(
        category=category,
        subcategory__in=subcategories,
        brand=brand
    )

def top_products_queryset(products, field_name):
    """특정 필드의 상위 5개 제품을 가져옵니다."""
    return products.order_by(f'-{field_name}')[:5]

@csrf_exempt
def product_performance_analysis_likes(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        category, subcategory_string = validate_category_and_subcategory(data)
        if not category or not subcategory_string:
            return HttpResponseBadRequest("Missing 'category' or 'subcategory' fields")

        products = get_products(category, data.get('subcategory', []))
        top_products = top_products_queryset(products, 'product_like')

        product_likes = products.annotate(
            brand_group=Value('무신사 스탠다드', output_field=CharField())
        ).values('brand_group').annotate(
            average_like=Avg('product_like')
        ).order_by('brand_group')

        performance_data = [{
            'category': category,
            'subcategory': subcategory_string,
            'brand': product['brand_group'],
            'average_like': round(product['average_like']) if product['average_like'] else 0,
            'top_products': [p.product for p in top_products]
        } for product in product_likes]

        return JsonResponse(performance_data, safe=False)
    else:
        return render(request, 'product_performance_analysis.html')


@csrf_exempt
def product_performance_analysis_grades(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        category, subcategory_string = validate_category_and_subcategory(data)
        if not category or not subcategory_string:
            return HttpResponseBadRequest("Missing 'category' or 'subcategory' fields")

        products = get_products(category, data.get('subcategory', []))
        reviews = ProductReview.objects.filter(
            product_id__in=products.values('id')
        ).order_by('-grade')

        seen_product_ids = set()
        top_products = []
        for review in reviews:
            if review.product_id not in seen_product_ids:
                top_products.append(review)
                seen_product_ids.add(review.product_id)
            if len(top_products) >= 5:
                break

        grade_averages = reviews.annotate(
            brand_group=Value('무신사 스탠다드', output_field=CharField())
        ).values('brand_group').annotate(
            average_grade=Avg('grade')
        ).order_by('brand_group')

        performance_data = [{
            'category': category,
            'subcategory': subcategory_string,
            'brand': review['brand_group'],
            'average_grade': review['average_grade'] or 0,
            'top_products': [p.product_id.product for p in top_products]
        } for review in grade_averages]

        return JsonResponse(performance_data, safe=False)
    else:
        return render(request, 'product_performance_analysis.html')


@csrf_exempt
def product_performance_analysis_views(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        category, subcategory_string = validate_category_and_subcategory(data)
        if not category or not subcategory_string:
            return HttpResponseBadRequest("Missing 'category' or 'subcategory' fields")

        products = get_products(category, data.get('subcategory', []))
        average_views = products.aggregate(average_views=Avg('views'))['average_views'] if products.exists() else 0

        top_products = top_products_queryset(products, 'views')

        age_groups = products.aggregate(
            views_18=Sum('views_18'),
            views_19_23=Sum('views_19_23'),
            views_24_28=Sum('views_24_28'),
            views_29_33=Sum('views_29_33'),
            views_34_39=Sum('views_34_39'),
            views_40=Sum('views_40')
        )

        gender_views = products.aggregate(
            views_male=Sum('views_male'),
            views_female=Sum('views_female')
        )

        total_views = (gender_views['views_male'] or 0) + (gender_views['views_female'] or 0)
        male_ratio = (gender_views['views_male'] / total_views * 100) if total_views > 0 else 0
        female_ratio = (gender_views['views_female'] / total_views * 100) if total_views > 0 else 0

        response_data = {
            'category': category,
            'subcategories': subcategory_string,
            'average_views': round(average_views) if average_views else 0,
            'top_products': [p.product for p in top_products],
            'age_groups': age_groups,
            'gender_views': {
                'views_male': gender_views['views_male'] or 0,
                'views_female': gender_views['views_female'] or 0,
                'male_ratio': round(male_ratio, 2),
                'female_ratio': round(female_ratio, 2),
            },
        }

        return JsonResponse(response_data, safe=False)
    else:
        return render(request, 'product_performance_analysis.html')


@csrf_exempt
def product_performance_analysis_purchases(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return HttpResponseBadRequest("Invalid JSON data")

        category, subcategory_string = validate_category_and_subcategory(data)
        if not category or not subcategory_string:
            return HttpResponseBadRequest("Missing 'category' or 'subcategory' fields")

        products = get_products(category, data.get('subcategory', []))
        average_purchases = products.aggregate(average_purchases=Avg('purchases'))['average_purchases'] if products.exists() else 0

        top_products = top_products_queryset(products, 'purchases')

        age_groups = products.aggregate(
            purchases_18=Sum('purchases_18'),
            purchases_19_23=Sum('purchases_19_23'),
            purchases_24_28=Sum('purchases_24_28'),
            purchases_29_33=Sum('purchases_29_33'),
            purchases_34_39=Sum('purchases_34_39'),
            purchases_40=Sum('purchases_40')
        )

        gender_purchases = products.aggregate(
            purchases_male=Sum('purchases_male'),
            purchases_female=Sum('purchases_female')
        )

        total_purchases = (gender_purchases['purchases_male'] or 0) + (gender_purchases['purchases_female'] or 0)
        male_ratio = (gender_purchases['purchases_male'] / total_purchases * 100) if total_purchases > 0 else 0
        female_ratio = (gender_purchases['purchases_female'] / total_purchases * 100) if total_purchases > 0 else 0

        response_data = {
            'category': category,
            'subcategories': subcategory_string,
            'average_purchases': round(average_purchases) if average_purchases else 0,
            'top_products': [p.product for p in top_products],
            'age_groups': age_groups,
            'gender_purchases': {
                'purchases_male': gender_purchases['purchases_male'] or 0,
                'purchases_female': gender_purchases['purchases_female'] or 0,
                'male_ratio': round(male_ratio, 2),
                'female_ratio': round(female_ratio, 2),
            },
        }

        return JsonResponse(response_data, safe=False)
    else:
        return render(request, 'product_performance_analysis.html')


@csrf_exempt
def purchase_reviews_by_category(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        category = data.get('category')
        reviewtags = data.get('reviewtags', [])

        if not category or not reviewtags:
            return JsonResponse({"error": "Missing 'category' or 'reviewtags' field"}, status=400)

        reviews = ProductReview.objects.filter(
            product_id__category=category
        )

        results = {}
        for tag in reviewtags:
            field_name = f'reviewtag_{tag}'
            if field_name not in [f.name for f in ProductReview._meta.get_fields()]:
                continue

            review_tag_score = reviews.aggregate(
                score=Avg(Case(
                    When(**{f"{field_name}__icontains": '커요', "then": 1}),
                    When(**{f"{field_name}__icontains": '밝아요', "then": 1}),
                    When(**{f"{field_name}__icontains": '선명해요', "then": 1}),
                    When(**{f"{field_name}__icontains": '두꺼워요', "then": 1}),
                    When(**{f"{field_name}__icontains": '따뜻해요', "then": 1}),
                    When(**{f"{field_name}__icontains": '무거워요', "then": 1}),
                    When(**{f"{field_name}__icontains": '빨라요', "then": 1}),
                    When(**{f"{field_name}__icontains": '꼼꼼해요', "then": 1}),
                    When(**{f"{field_name}__icontains": '작아요', "then": -1}),
                    When(**{f"{field_name}__icontains": '어두워요', "then": -1}),
                    When(**{f"{field_name}__icontains": '흐려요', "then": -1}),
                    When(**{f"{field_name}__icontains": '얇아요', "then": -1}),
                    When(**{f"{field_name}__icontains": '약해요', "then": -1}),
                    When(**{f"{field_name}__icontains": '가벼워요', "then": -1}),
                    When(**{f"{field_name}__icontains": '아쉬워요', "then": -1}),
                    default=0,
                    output_field=FloatField()
                ))
            )
            results[tag] = review_tag_score['score']

        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
def product_performance_analysis(request):
    return render(request, 'product_performance_analysis.html')
