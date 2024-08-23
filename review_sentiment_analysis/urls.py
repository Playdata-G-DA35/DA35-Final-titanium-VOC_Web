from django.urls import path
from .views import sentiment_analysis_view, get_top_reviews,topic_analysis_radial,get_top_topics

urlpatterns = [
    path('sentiment-analysis/', sentiment_analysis_view, name='sentiment_analysis'),
    path('get-top-reviews/', get_top_reviews, name='get_top_reviews'),
    path('get-top-topics/', get_top_topics, name='get_top_topics'),
    path('topic-analysis-radial/', topic_analysis_radial, name='topic_analysis_radial'),
]