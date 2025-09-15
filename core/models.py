from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    followers = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

class Room(models.Model):
    name = models.CharField(max_length=250)
    members = models.ManyToManyField(User, related_name='chat_rooms')

    def __str__(self):
        return self.name

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes=[models.Index(fields=['room', 'timestamp'])]

    def __str__(self):
        return self.content