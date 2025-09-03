#!/usr/bin/python
# -*- coding: utf8 -*-
import os
import logging
import json
from django.http import JsonResponse
from datetime import datetime, date, time, timedelta
from django.utils.translation import gettext_lazy as _
from core.views import MessageResponse, BaseViewMixin, BaseView
from device.models import Device
from core.mqbroker.event import *
from synch.modules.adv import adv_handle, adv_synchronize
from utils.jsonmsg import JsonMessage
from utils.datetimeformat import date2str
from core.mqbroker.fqueue.fqueuecontroller import QueueInstance
from synch.common.response_helper import syncResponse
from config.system.models import System
from modules.adversiting.models import AdvDataSynch, OneNetContent, TYPE_ONEMET
from django.utils.timezone import localtime, make_aware
from core.syncreceivehandler import SyncReceiveHandler
logger = logging.getLogger('django')


class AdvSync(BaseViewMixin, *BaseView('post')):
    def advSyncToDev(self, devIds, user=None):
        synState = {
            'result': None,
            'offlines': [],
            'errors': [],
            'success': [],
            'msgerror': []
        }
        try:
            advSyncs =  AdvDataSynch.objects.filter(advd_device_id__in=devIds, advd_synchronized=False)
            if advSyncs.count() > 0:
                dataToSend = []
                timeout = int(os.getenv('SYNC_TIMEOUT', 10))

                srh = SyncReceiveHandler()

                for advSync in advSyncs:
                    dev = advSync.advd_device
                    if dev.dev_online == False or dev.dev_ident is None:
                        synState['offlines'].append(dev.dev_ident)
                    else:
                        # change sync state of device to waiting
                        dev.dev_sync_state = Device.SYNC_STATE_WAITING
                        dev.save()
                        key = '{}_{}_'.format(dev.dev_ident, advSync.advd_type)
                        srh.update({
                            key: {
                                "id": dev.id,
                                "time": datetime.now(),
                                "timeout": timeout,
                                "ins": advSync,
                                "users": [user.id]
                            }
                        })

                        dataToSend.append({
                            'ins': advSync,
                            'data': {
                                'toaddr': dev.dev_ident,
                                'datasend': advSync.advd_value
                            }
                        })
                    # dataToSend.append({
                    #     'ins': advSync,
                    #     'data': {
                    #         'toaddr': dev.dev_ident,
                    #         'datasend': advSync.advd_value
                    #     }
                    # })


                # instance = adv_synchronize.AdvSynch(EVT_ADVERTIS_REQUEST_APP_TO_DEVICE_SYNCHRONIZED,
                #                                     callback=adv_handle.advSyncCallbackHandler, timeout=100)

                instance = adv_synchronize.AdvSynch(EVT_ADVERTIS_REQUEST_APP_TO_DEVICE_SYNCHRONIZED,
                                                    callback=None, timeout=100)
                synState['result'] = instance.syncDevice(dataToSend)
                # synState['errors'] = synState['result'].devResState['failed']
                # synState['success'] = synState['result'].devResState['success']
        except Exception as ex:
            logger.error(str(ex))
            synState['msgerror'].append(str(ex))
        finally:
            return synState

    def sendNotice(self):
        # OneNetContent
        end_date = make_aware(datetime.now())
        # start_date =  end_date - timedelta(seconds=int(os.getenv('ONENET_TIMEOUT', 5)))
        start_date =  end_date - timedelta(minutes=5)
        contentObj = OneNetContent.objects.filter(onc_timestart__range=(start_date, end_date), onc_sent=False)
        if contentObj and contentObj.count() > 0:
            logger.info(_('sendNotice content count= {}'.format(contentObj.count(), )))
            for content in contentObj:
                try:
                    dev = content.onc_device
                    if dev.dev_online == True and dev.dev_ident and dev.dev_ident != '':
                        instance = adv_synchronize.OneNetSynch(EVT_ADVERTIS_REQUEST_APP_TO_DEVICE_SYNCHRONIZED)
                        instance.syncDevice([
                            {
                                "ins": content,
                                "data": {
                                    "toaddr": dev.dev_ident,
                                    "datasend": {
                                        "type": TYPE_ONEMET,
                                        "data": [
                                            {
                                                "id": content.id,
                                                "device": dev.dev_name,
                                                "priority": content.onc_priority,
                                                "delay": content.onc_delay,
                                                "content": content.onc_content,
                                                "duration": content.onc_duration,
                                                "start": date2str(localtime(content.onc_timestart), format='%Y-%m-%d %H:%M:%S'),
                                                "interval": content.onc_interval,
                                                "timeout": content.onc_timeout,
                                            }
                                        ]
                                    }
                                }
                            }
                        ])
                        content.onc_sent=True
                        content.save()
                        logger.info(_('Sent notice to device {}'.format(dev.dev_name, )))
                    else:
                        logger.warning(_('Device {} is offline or inactive'.format(dev.dev_name,)))
                except Exception as ex:
                    logger.error(str(ex))

    def post(self, request, *args, **kwargs):
        res = MessageResponse()
        devIds = request.data.get('devices')
        synState = self.advSyncToDev(devIds, user=request.user)

        return JsonResponse(res.getAttr(), safe=False)
