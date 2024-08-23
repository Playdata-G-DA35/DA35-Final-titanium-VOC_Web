# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('main/', views.main, name='main'),
    path('question/', views.question,name='question'),
    path('logout/', views.logout_view, name='logout'),
    # path('profile/<str:user_id>/', views.user_profile, name='user_profile'),

]    

