from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    followers = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
