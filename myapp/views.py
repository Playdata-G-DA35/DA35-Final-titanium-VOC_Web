from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login, logout
from .models import Inquiry
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

# 대시보드 페이지 (로그인 여부와 상관없이 접근 가능)
def dashboard(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')  # 로그인 후 리다이렉트할 페이지
    return render(request, 'dashboard.html')

@login_required
# 프로필 페이지 (로그인 여부와 상관없이 접근 가능)
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm()
    return render(request, 'profile.html', {'form': form})

@login_required
# 메인 페이지 (로그인 여부와 상관없이 접근 가능)
def main(request):
    return render(request, 'main.html')

@login_required
# 로그아웃 처리 및 대시보드로 리다이렉트
def logout_view(request):
    logout(request)
    return redirect('dashboard')  # 로그아웃 후 리다이렉트할 페이지

@login_required
# 문의하기 페이지 (로그인 없이 접근 가능하며 POST 요청에 대해 CSRF 예외 처리)
@csrf_exempt
def question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            brand = data.get('brand')
            email = data.get('email')
            message = data.get('message')

            if not username:
                return JsonResponse({'success': False, 'error': 'Username is required.'}, status=400)

            Inquiry.objects.create(
                username=username,
                brand=brand,
                email=email,
                message=message
            )

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            logger.error("Failed to parse JSON")
            return JsonResponse({'success': False, 'error': 'Invalid JSON format.'}, status=400)

    return render(request, 'question.html')

# 오류 페이지

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_400(request, exception):
    return render(request, '400.html', status=400)