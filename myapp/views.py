# myapp/views.py
from django.shortcuts import render,redirect
from .forms import UserProfileForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required

@login_required# 로그인시 볼수있게함
def dashboard(request):
    return render(request, 'dashboard.html')
@login_required
def profile(request):
    return render(request, 'profile.html')
@login_required
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
def main(request):
    return render(request, 'main.html')
@login_required
def question(request):
    return render(request,'question.html')
def dashboard(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')  # 로그인 후 리다이렉트할 페이지
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('dashboard')  # 로그아웃 후 리다이렉트할 페이지

from django.shortcuts import render, get_object_or_404
from .models import UserProfile

# def user_profile(request, user_id):
#     user = get_object_or_404(UserProfile, user_id=user_id)
#     return render(request, 'profile.html', {
#         'user_id': user.user_id,
#         'password': user.password,
#     })

