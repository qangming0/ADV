from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from channels.auth import login
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack
from notify.process import NotifyWS
from notify.models import Notify

class ChatConsumer(WebsocketConsumer):
    # groups = ["broadcast"]

    def connect(self):
        user = self.scope['user']
        self.user_room_name = 'user_channel_{}'.format(user.id)
        if user.is_anonymous:
            self.close()
        else:
            # Join room group
            self.accept()
            noti = NotifyWS()
            channelGroups = user.channelgroup.all()
            for item in channelGroups:
                noti.addEndPointGroup(
                    item.cgp_code,
                    {
                        'userid': user.id,
                        'channels': [self.channel_name]
                    }
                )
                async_to_sync(self.channel_layer.group_add)(
                    item.cgp_code,
                    self.channel_name
                )
            async_to_sync(self.channel_layer.group_add)(
                self.user_room_name,
                self.channel_name
            )

    def disconnect(self, close_code):
        # Leave room group
        user = self.scope['user']
        if user.is_anonymous:
            return
        channelGroups = user.channelgroup.all()
        noti = NotifyWS()
        for item in channelGroups:
            noti.removeEndPointGroup(
                item.cgp_code,
                {
                    'userid': user.id,
                    'channels': [self.channel_name]
                }
            )
            async_to_sync(self.channel_layer.group_discard)(
                item.cgp_code,
                self.channel_name
            )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        noti = NotifyWS()
        print(noti.getEndpoints())
        print(noti.getGroups())

        # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )
        self.send(text_data=text_data, bytes_data=bytes_data)

    # Receive message from room group
    def chat_message(self, event):
        message = event.get('message', None)
        notify_type = event.get('notify_type', Notify.TYPE_INFO)
        event = event.get('event', None)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': notify_type,
            'event': event
        }))