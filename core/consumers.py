import asyncio
import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from redis.asyncio import Redis
from .models import Room, Message


User = get_user_model()

class GlobalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            await self.accept()
            self.user_id = self.scope['user'].id
            await self.channel_layer.group_add('global', self.channel_name)
            await self.channel_layer.group_send(
                'global',
                {
                    'type':'online_status_dispatcher',
                    'user_id':self.scope['user'].id,
                    'is_online':True
                }
            )
          #  await self.mark_user_online_status(self.scope['user'], True)

    
    async def disconnect(self, code):
        if self.user_id is not None:
            await self.channel_layer.group_send(
                'global',
                {
                    'type':'online_status_dispatcher',
                    'user_id':self.user_id,
                    'is_online':False
                }
            )
        await self.channel_layer.group_discard('global', self.channel_name)
       # await self.mark_user_online_status_by_id(self.scope['user'].id, False)

    async def online_status_dispatcher(self, event):
        await self.send(json.dumps({
            'type':'online_status',
            'user_id':event['user_id'],
            'is_online':event['is_online']
        }))

    @database_sync_to_async
    def mark_user_online_status(self, user, status):
        user.is_online = status
        user.save()

    @database_sync_to_async
    def mark_user_online_status_by_id(self, user_id, status):
        try:
            user = User.objects.get(id=user_id)
            user.is_online = status
            user.save()
        except User.DoesNotExist:
            print(f'user with id {user_id} is not found')
            

class MessageConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.sender = self.scope['url_route']['kwargs']['sender']
        self.receiver = self.scope['url_route']['kwargs']['receiver']
        self.sender_user = self.scope['user']
        sorted_room_name = sorted([self.sender, self.receiver])
        self.room_name = f'private_{sorted_room_name[0]}_{sorted_room_name[1]}'

        try:
            self.receiver_user = await self.get_user_by_id(self.receiver)
        except Exception:
            self.receiver_user = None

        if self.sender_user is None or self.sender_user.is_anonymous:
            await self.send(text_data=json.dumps({'error':'unknown user or invalid token'}))
            await self.close()
            return
        
        if self.receiver_user is None or self.receiver_user.is_anonymous:
            await self.send(text_data=json.dumps({'error':'unknown pair user'}))
            await self.close()
            return
        
        await self.send(text_data=json.dumps({'message':'connection established'}))

        self.redis = await Redis.from_url(os.getenv("REDIS_URL"))
        self.heartbeat_task = asyncio.create_task(self.heartbeat())

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':'dispatch_event',
                'user':self.sender_user.pk,
                'action':'went_online'
            }
        )

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        if self.receiver_user:
            messages = await self.fetch_messages(self.sender_user, self.receiver_user)
            for m in messages:
                await self.send(text_data=json.dumps({
                    'sender':m['sender'],
                    'message':m['message'],
                    'message_id':m['message_id']
                }))
                
    async def receive(self, text_data=None):
        data = json.loads(text_data)
        if self.receiver_user is None or self.receiver_user.is_anonymous:
            await self.send(text_data=json.dumps({'error':'invalid pair user'}))
            await self.close()
            return
        
        if data.get('action') == 'delete_message'.lower():
            await self.delete_message(data.get('message_id'))
            await self.send(text_data=json.dumps({'message':'message deleted'}))
            return


        if data.get('action') == 'typing'.lower():
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type':'dispatch_event',
                    'action':'typing',
                    'user':self.sender_user.username
                }
            )
            return
        
        if data.get('action') == 'typing_stop'.lower():
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type':'dispatch_event',
                    'action':'typing_stop',
                    'user':self.sender_user.username
                }
            )
            return
        
        message = data.get('message')
        chat_room = await self.get_or_create_room(self.sender_user, self.receiver_user)
        msg = await self.save_message(message, chat_room)

        
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type' : 'dispatch_message',
                'message_id' : msg.id,
                'message' : message,
                'sender' : self.sender_user.username
            }
        )
        
    async def heartbeat(self):
        try:
            while True:
                await self.redis.set(f'user:{self.sender_user.pk}:online', '1', ex=10)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass
    async def disconnect(self, code):

        try:
            if hasattr(self, 'room_name'):
                await self.channel_layer.group_discard(
                    self.room_name,
                    self.channel_name
                )

            if hasattr(self, 'heartbeat_task'):
                self.heartbeat_task.cancel()
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type':'dispatch_event',
                        'user':self.sender_user.pk,
                        'action':'went_offline'
                    }
                )

            if hasattr(self, 'redis') and hasattr(self, 'sender_user'):
                await self.redis.delete(f'user:{self.sender_user.pk}:online')

        except Exception as e:
            print(f'Error while disconnecting: {e}')


    async def dispatch_message(self, event):
        await self.send(text_data=json.dumps({
            'message_id':event['message_id'],
            'sender':event['sender'],
            'message':event['message']
        }))

    async def dispatch_event(self, event):
        if event['user'] == self.sender_user.username:
            return
        
        await self.send(text_data=json.dumps({
            'action':event['action'],
            'user':event['user']
        }))

    @database_sync_to_async
    def get_user_by_id(self, pk):
        try:
            return User.objects.get(pk=pk)

        except User.DoesNotExist:
            user = None
        print('fetched user by username', user)
        return user
        
    @database_sync_to_async
    def fetch_messages(self, sender, receiver):
        room = Room.objects.filter(members=sender).filter(members=receiver).first()
        if room:
            messages = Message.objects.filter(room=room).select_related('sender')
            return [{'sender':m.sender.username, 'message':m.content, 'message_id':m.pk} for m in messages]
        return []
    
    @database_sync_to_async
    def save_message(self, message, chat_room):
       return Message.objects.create(sender=self.sender_user, room=chat_room, content=message)

    @database_sync_to_async
    def get_or_create_room(self, sender, receiver):
        room = Room.objects.filter(members__username=sender.username).filter(members__username=receiver.username).first()
        if not room:
            room = Room.objects.create(name=self.room_name)
            room.members.add(sender, receiver)
        return room
    
    @database_sync_to_async
    def delete_message(self, id):
        try:
            message = Message.objects.get(id=id)
        except Message.DoesNotExist:
            message = None
            print('not found', id)
        
        if message:
            message.delete()

    async def force_disconnect(self, event):
        await self.close(code=4001)