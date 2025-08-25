import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = 'test_room'
        
        await self.channel_layer.group_add(
            self.room,
            self.channel_name
        )
        await self.accept()

        await self.channel_layer.group_send(
            self.room,
            {
                'type' : 'dispatch_message',
                'message' : 'test message',
                'user' : 'mock user'
            }
        )

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        message = data.get('message')
        await self.channel_layer.group_send(
            self.room,
            {
                'type' : 'dispatch_message',
                'message' : message,
                'user' : 'mock user'
            }
        )
        print('message sent: ', message)
    
    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room,
            self.channel_name
        )

    async def dispatch_message(self, event):
        await self.send(text_data=json.dumps({
            'sender':event['user'],
            'message':event['message']
        }))