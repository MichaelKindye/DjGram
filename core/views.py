from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .email import generate_email_verification_token
import json

User = get_user_model()


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
                    try:
                        generate_email_verification_token(request, user)
                        return redirect('verify-email-message-page')
                    except Exception as e:
                        print(f'Error while generating token: {e}')
                        messages.error(request, 'Internal server error. Try again.')
            else:
                messages.error(request, 'Please enter valid inputs. All fields are required.')
        except Exception as e:
            print(e)
            messages.error(request, 'Internal server errors. Please try again.')
    return render(request, 'register/register.html')


def verify_email_notification_view(request):
    return render(request, 'accounts/verify-email.html')


def verify_email_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None
    
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('login-page')
    messages.error(request, 'Invalid token, user not found.')
    return redirect('login-page')


def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            if not username or not password:
                messages.error(request, 'Please provide both username and password.')
                return redirect('login-page')
            
            user = get_object_or_404(User, username=username)
                
            if not user.check_password(password):
                messages.error(request, 'Invalid credentials were given. Please try again.')
                return redirect('login-page')
            elif not user.is_active:
                messages.error(request, 'Inactive account. Activate your account before you login.')
                return redirect('login-page')
            else:
                login(request, user)
                return redirect('home-page')
        except Http404:
            messages.error(request, 'Invalid credentials were given. Please try again.')
            return redirect('login-page')
        except Exception:
            messages.error(request, 'Unable to process your inputs. Please try again')
            return redirect('login-page')
    return render(request, 'login/login.html')


@login_required
def home_view(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'home/home.html', {'users': users, 'user':request.user})
    
@login_required
def fetch_users(request):
    q = request.GET.get('q', '')
    if q:
        users = User.objects.filter(username__icontains=q).exclude(username=request.user.username).order_by('username')
    else:
        users = User.objects.exclude(username=request.user.username)
    data = JsonResponse([{'username':u.username} for u in users], safe=False)
    return data

@login_required
def logout_view(request):
    logout(request)
    return redirect('login-page')