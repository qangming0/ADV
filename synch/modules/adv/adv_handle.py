import logging
import os
from django.db import transaction, close_old_connections, reset_queries
from utils.jsonmsg import JsonMessage
from device.models import DeviceLine, Device
from django.utils.translation import gettext, gettext_lazy as _
from core.mqbroker.event import *
from core.mqbroker.topic import Topic
from modules.adversiting.models import OneNetContent
from utils.datetimeformat import str2DateTime
from core.mqbroker.mqtt.mqttcontroller import MQTTController
from django.utils.timezone import localtime, make_aware
logger = logging.getLogger('django')

def advSyncCallbackHandler(instance):
    try:
        msgSent = instance.params['msg']
        msgRec = instance.data.value

        devIdRecv = msgRec['fromAddr']
        dataRecv = msgRec['data']
        if dataRecv is None:
            raise Exception('Param  has be not matched')

        insSyn = None
        # for dev in msgSent:
        for idx, dev in enumerate(msgSent):
            if dev['data']['toaddr'] == devIdRecv and dev['ins'].advd_type == int(dataRecv['type']):
                instance.params['count'] -= 1
                insSyn = dev['ins']
                del instance.params['msg'][idx]
                break

        if insSyn is not None:
            if int(dataRecv['status']) == 1:
                insSyn.advd_synchronized = True
                insSyn.save()
                instance.devResState['success'].append(devIdRecv)
                instance.success = True
            else:
                instance.devResState['failed'].append(devIdRecv)
    except Exception as ex:
        print(str(ex))
        instance.addErr(str(ex))
    finally:
        if instance.params['count'] <= 0:
            instance.done()


def AdvUpdateScheduleHandle(instance):
    try:
        logger.info('realtime log handler: adv request update newest schedule')
        msgRec = instance.data.value
        dataRecv = msgRec['data']
        devIdRecv = msgRec['fromAddr']

        if dataRecv is None:
            raise Exception('Param  has be not matched')

        logger.debug('realtime log handler: adv system %s' % (devIdRecv,))

        evet = instance.data.event
        if evet == EVT_ADVERTIS_SEND_DEVICE_LIFT_TO_APP_UPDATE_SCHEDULE:
            logger.info('realtime log handler: adv request update newest schedule 2')

    except Exception as ex:
        logger.error(str(ex))


def AdvOneNetHandle(instance):
    try:
        reset_queries()
        close_old_connections()
        logger.info('onenet handler: notify')
        if instance.data.event == EVT_ONENET_PUSH_NOTIFY:
            dataRecv = instance.data.value['data'][0]
            if all(k in dataRecv for k in ("id", "device", 'priority', 'delay', 'content', 'duration', 'start', 'interval', 'timeout')):
                if len(dataRecv['device']) == 1 and dataRecv['device'][0] == -1:
                    devs = Device.objects.getAdvertis()
                else:
                    devs = Device.objects.getAdvertis().filter(id__in=dataRecv['device'])
                if devs and devs.count() > 0:
                    timestart = make_aware(str2DateTime(dataRecv['start']))
                    instance_list = [
                        OneNetContent(
                            onc_device=dev,
                            onc_priority = int(dataRecv['priority']),
                            onc_content_id = dataRecv['id'],
                            onc_content = dataRecv['content'],
                            onc_duration = int(dataRecv['duration']) if int(dataRecv['duration']) > 0 else OneNetContent.DEFAULT_DURATION,
                            # onc_timestart = str2DateTime(dataRecv['start']),
                            onc_timestart = timestart,
                            onc_interval = int(dataRecv['interval']),
                            onc_timeout = int(dataRecv['timeout']),
                            onc_delay = int(dataRecv['delay'])
                        ) for dev in devs
                    ]
                    OneNetContent.objects.bulk_create(instance_list)
                    logger.info('insert {} data that received from onenet'.format(len(devs), ))
                else:
                    logger.error('device {} not found'.format(dataRecv['device'], ))

        elif instance.data.event == EVT_ONENET_REQUEST_CANCEL_NOTIFY:
            logger.info('canncel message that received from onenet')

        elif instance.data.event == EVT_ONENET_REQUEST_GET_LIST_DEVICE:
            logger.info('request get list of device from onenet')
            devs = Device.objects.getAdvertis()
            dataDevInfo = []
            if devs and devs.count() > 0:
                for dev in devs:
                    dataDevInfo.append({
                        "id": dev.id,
                        "name": dev.dev_name,
                        "pos": dev.dev_position_full
                    })
            # send data to onenet
            mqttCtrl = MQTTController()
            mqttCtrl.producer.rawSend(
                topic=Topic.ONEMES_LISTEN,
                value={
                    "type": "ONENET",
                    "event": EVT_ONENET_REQUEST_GET_LIST_DEVICE,
                    "data": dataDevInfo
                }
            )
        close_old_connections()
    except Exception as ex:
        logger.error(str(ex))

