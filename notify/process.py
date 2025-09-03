import time
import os
import logging
import json
import datetime
import threading
import asyncio
import collections
from collections import namedtuple, deque
from collections import defaultdict
from collections import Counter
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notify.models import Notify
from device.models import Device
from django.utils.translation import gettext_lazy, gettext as _
from modules.adversiting import models
from authen.models import User


logger = logging.getLogger('django')


class NotifyWS:

    EVENT_SYNC_RESULT = 'SYNC_RESULT'

    def __new__(cls):
        if not NotifyWS.__instance:
            NotifyWS.__instance = NotifyWS.__NotifyWS()
        return NotifyWS.__instance
    def __getattr__(self, value):
        return getattr(self.__instance, value)
    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)

    class __NotifyWS:
        def __init__(self):
            self._endpoint = defaultdict()
            self._group_count = Counter()
            self._group = defaultdict(Counter)
            self._endpoint_default = {
                'userid': -1,
                'channels': []
            }

        # { 'userid': 1, 'channels': ['chanel_1', 'chanel_2', 'chanel_3', ...] }
        # channel ~ group_code
        def addEndPoint(self, endpoint):
            userid = str(endpoint.get('userid'))
            channels = endpoint.get('channels', [])
            if userid in self._endpoint:
                for chal in channels:
                    if chal not in self._endpoint[userid]['channels']:
                        self._endpoint[userid]['channels'].append(chal)
            else:
                self._endpoint[userid] = {
                    'channels': endpoint.get('channels', [])
                }

        # [1,2,3]
        def hardDelEndPoint(self, userid):
            if isinstance(userid, list) or isinstance(userid, tuple):
                for item in userid:
                    self.hardDelEndPoint(item)
            else:
                if str(userid) in self._endpoint:
                    del self._endpoint[str(userid)]

        def removeEndPoint(self, endpoint):
            userid = str(endpoint.get('userid'))
            channels = endpoint.get('channels', [])
            if userid in self._endpoint:
                for chal in channels:
                    if chal in self._endpoint[userid]['channels']:
                        del self._endpoint[userid]['channels'][chal]
                if len(self._endpoint[userid]['channels']) == 0:
                    del self._endpoint[userid]

        # endpoint : [{ 'userid': 1, 'channels': ['chanel_1', 'chanel_2', 'chanel_3', ...] }]
        def addEndPointGroup(self, channel, endpoint):
            if isinstance(channel, list) or isinstance(channel, tuple):
                for eChannel in channel:
                    self.addEndPointGroup(eChannel, endpoint)
            else:
                if isinstance(endpoint, list) or isinstance(endpoint, tuple):
                    for enp in endpoint:
                        self.addEndPointGroup(channel, enp)
                else:
                    userid = str(endpoint.get('userid'))
                    self.addEndPoint(endpoint)
                    self._group[channel][userid] += 1
                    self._group_count[channel] += 1

        def removeEndPointGroup(self, channel, endpoint):
            if isinstance(channel, list) or isinstance(channel, tuple):
                for eChannel in channel:
                    self.removeEndPointGroup(eChannel, endpoint)
            else:
                if isinstance(endpoint, list) or isinstance(endpoint, tuple):
                    for enp in endpoint:
                        self.removeEndPointGroup(channel, enp)
                else:
                    userid = str(endpoint.get('userid'))
                    self.removeEndPoint(endpoint)
                    self._group[channel][userid] -= 1
                    if self._group[channel][userid] <= 0:
                        del self._group[channel][userid]

                    self._group_count[channel] -= 1
                    if self._group_count[channel] <= 0:
                        del self._group_count[channel]

        def getEndpoints(self, userid=None):
            if userid is None:
                return self._endpoint
            else:
                if userid in  self._endpoint:
                    return self._endpoint[userid]
                else:
                    return None

        def getGroups(self, channel=None):
            if channel is None:
                return self._group
            else:
                if channel in self._group:
                    return self._group[channel]
                else:
                    return None

        def send(self, user):
            channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)('{}'.format('chat_1234'),
            #                                         {'type': 'chat_message', 'message': '12333'})
            # async_to_sync(channel_layer.send)('{}'.format('specific.vemUZtny!BnoJqrqeOTNX'),
            #                                   {'type': 'chat_message', 'message': '5555'})

        def sendGroup(self):
            channel_layer = get_channel_layer()

        def get_sync_type_display(self, sync_type):
            if sync_type == models.TYPE_ADV:
                return _('Advertise')
            elif sync_type == models.TYPE_RELAX:
                return _('Relax')
            elif sync_type == models.TYPE_ONEMET:
                return _('Onemes')
            else:
                return None

        def notify_sync_result(self, ident, result, users):
            from core.syncreceivehandler import SyncReceiveHandler
            unique_users = list(set(users))
            channel_layer = get_channel_layer()
            notify_type = Notify.TYPE_ERROR
            status = _('Error')
            sync_type_str = None
            if ident.endswith('_'):
                key = ident[:-3]
                try:
                    sync_type = int(ident[-2:-1])
                    sync_type_str = self.get_sync_type_display(sync_type)
                except:
                    pass
            else:
                key = ident

            device = Device.objects.filter(dev_ident=key).first()
            if device is None:
                return

            if result == SyncReceiveHandler.RESPONSE_TYPE_SUCCESS:
                notify_type = Notify.TYPE_SUCCESS
                status = _('Success')
            elif result == SyncReceiveHandler.RESPONSE_TYPE_TIMEOUT:
                status = _('Timeout')
                device.dev_sync_state = Device.SYNC_STATE_FAILED
                device.save()
            if sync_type_str is not None:
                message = _('Synchronize {} to device {} {}').format(sync_type_str, device.dev_name, status)
            else:
                message = _('Synchronize to device {} {}').format(device.dev_name, status)

            for userId in unique_users:
                group_name = 'user_channel_{}'.format(userId)
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'notify_type': notify_type,
                        'event': NotifyWS.EVENT_SYNC_RESULT
                    }
                )

        def notify_update_dev_sync(self):
            channel_layer = get_channel_layer()
            admin_users = User.objects.filter(is_superuser=True).values_list('id', flat=True)
            for user_id in list(admin_users):
                group_name = 'user_channel_{}'.format(user_id)
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'chat_message',
                        'event': NotifyWS.EVENT_SYNC_RESULT
                    }
                )

    __instance = None