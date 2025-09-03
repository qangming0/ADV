#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import json
import uuid
import logging
from datetime import datetime
from django.db import transaction
from core.dataglobal import GlobalDeviceStatus
from core.mqbroker.event import *
logger = logging.getLogger('django')


def DevKeepAliveHandle(instance):
    try:
        msgRec = instance.data.value
        dataRecv = msgRec['data']
        devIdRecv = msgRec['fromAddr']

        if dataRecv is None:
            logger.error('Param  has be not matched')

        logger.debug('realtime log handler: device keepalive %s' % (devIdRecv, ))

        evet = instance.data.event
        if evet == EVT_REQUEST_DEVICE_STATUS:
            # update device status
            logger.debug('update device status %s' % (devIdRecv,))
            gds = GlobalDeviceStatus()
            logger.debug(gds.getAll(status=True))
            gds.updateRealtime({
                str(devIdRecv) : {
                    'ip': dataRecv['msgData']['ipAddress'],
                    'mac': dataRecv['msgData']['macAddress'],
                    'status': True
                }
            })
            logger.debug(gds.getAll(status=True))

        elif evet == EVT_SEND_DEVICE_ACC_TO_APP_DOOR_STATUS:
            # update door status
            logger.debug('update door status %s' % (devIdRecv,))

        else:
            pass

    except Exception as ex:
        logger.error(str(ex))


def AdvDevKeepAliveHandle(instance):
    try:
        msgRec = instance.data.value
        dataRecv = msgRec['data']
        devIdRecv = msgRec['fromAddr']

        if dataRecv is None:
            logger.error('Param  has be not matched')

        logger.debug('realtime log handler: device keepalive %s' % (devIdRecv, ))

        evet = instance.data.event
        if evet == EVT_REQUEST_DEVICE_STATUS:
            # update device status
            logger.debug('update device status %s' % (devIdRecv,))
            gds = GlobalDeviceStatus()
            logger.debug(gds.getAll(status=True))
            gds.updateRealtime({
                str(devIdRecv) : {
                    'ip': dataRecv['msgData']['ipAddress'],
                    'mac': dataRecv['msgData']['macAddress'],
                    'status': True
                }
            })
            logger.debug(gds.getAll(status=True))

    except Exception as ex:
        logger.error(str(ex))