from django.urls import path
from .views import (
    product_performance_analysis_likes,
    product_performance_analysis_grades,
    product_performance_analysis_views,
    product_performance_analysis_purchases,
    purchase_reviews_by_category,
    product_performance_analysis,
)

urlpatterns = [
    path('product-performance-analysis/', product_performance_analysis, name='product_performance_analysis'),
    path('product-performance-analysis/likes/', product_performance_analysis_likes, name='product_performance_analysis_likes'),
    path('product-performance-analysis/grades/', product_performance_analysis_grades, name='product_performance_analysis_grades'),
    path('product-performance-analysis/views/', product_performance_analysis_views, name='product_performance_analysis_views'),
    path('product-performance-analysis/purchases/', product_performance_analysis_purchases, name='product_performance_analysis_purchases'),
    path('product-performance-analysis/purchase-reviews/', purchase_reviews_by_category, name='purchase_reviews_by_category'),
]