from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # 앱의 URL 패턴 포함
    path('review/', include('review_basic_analysis.urls')),
    path('review_sentiment_analysis/', include('review_sentiment_analysis.urls')),
    path('product_performance_analysis/', include('product_performance_analysis.urls')),
    path('product_detail/', include('product_detail_page.urls')), 
]

if settings.DEBUG is False:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from django.conf.urls import handler404, handler500, handler403, handler400

# 오류 핸들러 설정
handler404 = 'myapp.views.custom_404'
handler500 = 'myapp.views.custom_500'
handler403 = 'myapp.views.custom_403'
handler400 = 'myapp.views.custom_400'