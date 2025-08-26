import os
from dotenv import load_dotenv
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

load_dotenv()

def generate_email_verification_token(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64':uid, 'token':token})
        )
    
    print('sending mail...')
    send_mail(
        recipient_list=[user.email],
        subject='Verify email',
        message=f'Please click this link to verify your email {verify_url}',
        from_email=str(os.getenv('EMAIL_HOST_USER'))
    )
    print('sent mail.')