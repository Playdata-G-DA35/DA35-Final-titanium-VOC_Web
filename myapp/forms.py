# myapp/forms.py
from django import forms
from .models import UserProfile
from django.contrib.auth.forms import AuthenticationForm

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'date_of_birth']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='ID', max_length=254, widget=forms.TextInput(attrs={'class': 'mt-1 block w-full p-2 border border-gray-300 rounded'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full p-2 border border-gray-300 rounded'}))