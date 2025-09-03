#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import json
import uuid
import logging
logger = logging.getLogger('django')

# from core.message import KafMsq
from core.mqbroker.fqueue.fqueuecontroller import FQueueController
from core.mqbroker.fqueue.fqueuecontroller import QueueInstance

def KafResponseHandle(instance):
    logger.info('KafResponseHandle')
    fqueue = FQueueController()
    try:
        fqueue.start()
        if fqueue.isStarted():
            resData = instance.data
            # listQueueInstance = fqueue.getQueues()
            listQueueInstance = fqueue.getQueues(type=QueueInstance.TYPE_KAFKA)
            for queueInstance in listQueueInstance:
                if resData.sessionid == queueInstance.sessionid \
                        and resData.event == queueInstance.key:
                    queueInstance.push(resData)
        else:
            return
    except Exception as ex:
        logger.exception(str(ex))


def MqttResponseHandle(instance):
    logger.info('MqttResponseHandle')
    fqueue = FQueueController()
    try:
        fqueue.start()
        if fqueue.isStarted():
            resData = instance.data
            listQueueInstance = fqueue.getQueues(type=QueueInstance.TYPE_MQTT)
            for queueInstance in listQueueInstance:
                if resData.sessionid == queueInstance.sessionid \
                        and resData.event == queueInstance.key:
                    queueInstance.push(resData)
        else:
            return
    except Exception as ex:
        logger.exception(str(ex))
