# product_detail_page/urls.py

from django.urls import path
from .views import product_detail_view, product_details_analysis_views, product_details_analysis_purchases, review_count, product_topic_analysis_radial, product_sentiment_analysis_view

urlpatterns = [
    path('detail/', product_detail_view, name='product_detail'),
    path('product_details_analysis/', product_details_analysis_views, name='product_details_analysis'),
    path('product_details_analysis_purchases/', product_details_analysis_purchases, name='product_details_analysis_purchases'),
    path('review_count/', review_count, name='review_count'),
    path('product_topic_analysis_radial/', product_topic_analysis_radial, name='product_topic_analysis_radial'),
    path('product_sentiment_analysis/', product_sentiment_analysis_view, name='product_sentiment_analysis'),  # 새로운 경로 추가
]