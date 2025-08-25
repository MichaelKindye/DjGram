from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home-page')
            messages.error(request, 'Invalid credentials were given. Please try again.')
            return redirect('login-page')
        except:
            messages.error(request, 'Unable to process your inputs. Please try again.')
    return render(request, 'login/login.html')

def home_view(request):
    return render(request, 'home/home.html')
    
def register_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            if username and password and email:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'This username is associated with another user. Try again.')
                elif User.objects.filter(email=email).exists():
                    messages.error(request, 'This email is associated with another user.')
                else:
                    user = User.objects.create_user(username=username, password=password, email=email)
                    login(request, user)
                    return redirect('home-page')
            messages.error(request, 'Please enter valid inputs.')
        except:
            messages.error(request, 'Internal server errors. Please try again.')
    return render(request, 'register/register.html')
