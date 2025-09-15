import json
import os
import asyncio
from redis.asyncio import Redis
import redis
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .email import generate_email_verification_token
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if username and password and email:
            if User.objects.filter(username=username).exists():
                return Response({'error':'This username is associated with another user.'}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(email=email).exists():
                return Response({'error':'This email is associated with another user'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                try:
                    generate_email_verification_token(request, user)
                    return Response({'message':'User created. Verify your email.'}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(f'Error while generating token: {e}')
                    return Response({'error':'Internal server error. Try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error':'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'error':'Internal server error. Try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None
    
    if user:
        token = default_token_generator.check_token(user, token)
        if token:
            user.is_active = True
            user.save()
            return redirect('http://localhost:5173/login')
        generate_email_verification_token(request, user)
        return Response({'error':'Token expired. Please check your email to get a new verification token.'}, status=status.htt4)
    return Response({'error':'User not found.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error':'Please provide both email and password.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, email=email)
            
        if not user.check_password(password):
            return Response({'error':'Invalid credentials were given. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
        elif not user.is_active:
            return Response({'error':'Inactive account. Activate your account before you login.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            token = RefreshToken.for_user(user)
            response = {'access':str(token.access_token), 'refresh':str(token)}
            return Response(response, status=status.HTTP_200_OK)
    except Http404:
        return Response({'error':'Invalid credentials were given. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({'error':'Unable to process your inputs. Please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def home_view(request):
    users = User.objects.exclude(pk=request.user.id)
    res = [{'name':u.username, 'id':u.pk} for u in users]
    return Response({'users':res, 'logged_user':request.user.id}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def fetch_users(request):
    q = request.GET.get('q', '')
    if q:
        users = User.objects.filter(username__icontains=q).exclude(username=request.user.username).order_by('username')
    else:
        users = User.objects.exclude(username=request.user.username)
    data = [{'name':u.username, 'id':u.pk} for u in users]
    return Response({'users':data})

@api_view(['POST'])
def logout_view(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        print('blacklisted-token', token)
        return Response({'message':'User logged out successfully.'}, status=status.HTTP_200_OK)
    except Exception:
        print('token not found')
        return Response({'message':'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def get_online_users(request):
    r = redis.from_url(os.getenv('REDIS_URL'), decode_responses=True)

    user_ids = request.data
    keys = [f"user:{uid}:online" for uid in user_ids]

    values = r.mget(keys)  
    active_users = [int(id) for id, val in zip(user_ids, values) if val is not None]

    return Response(active_users, status=status.HTTP_200_OK)