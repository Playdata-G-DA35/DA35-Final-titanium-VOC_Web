from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # 앱의 URL 패턴 포함
    path('review/', include('review_basic_analysis.urls')),
    path('review_sentiment_analysis/', include('review_sentiment_analysis.urls')),
    path('product_performance_analysis/', include('product_performance_analysis.urls')),
    path('product_detail/', include('product_detail_page.urls')), 
]