from django.urls import path
from .views import get_filtered_reviews, get_gender_distribution,review_basic, get_word_frequency_by_price_range, get_review_wordcloud

urlpatterns = [
    path('get-filtered-reviews/', get_filtered_reviews, name='get_filtered_reviews'),
    path('review_basic_analysis/', review_basic, name='review_basic'),
    path('get-gender-distribution/', get_gender_distribution, name='get_gender_distribution'),
    path('get-review-wordcloud/', get_review_wordcloud, name='get_review_wordcloud'),  
    path('get-word-frequency-by-price-range/', get_word_frequency_by_price_range, name='get_word_frequency_by_price_range'),
]

