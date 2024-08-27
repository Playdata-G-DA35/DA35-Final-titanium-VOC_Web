# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('main/', views.main, name='main'),
    path('question/', views.question, name='question'), # 문의하기
    path('logout/', views.logout_view, name='logout'),
]

