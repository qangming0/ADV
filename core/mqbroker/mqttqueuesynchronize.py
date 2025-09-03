#!/usr/bin/python
# -*- coding: utf8 -*-

from core.mqbroker.mqtt.mqttcontroller import MQTTController
from core.message import MqttMsg
from core.mqbroker.fqueue.fqueuecontroller import FQueueController
from core.mqbroker.fqueue.fqueuecontroller import QueueInstance


class BaseMqttQueueSysnchorized(object):
    def __init__(self, topic=None, group=None):
        self.topic = topic
        self.group = group
        self.sessionid = None
        self.ctrl = MQTTController()
        self.fqueue = FQueueController()

        self.fqueue.start()
        self.ctrl.start()

    def send(self, event, data, callback=None, params=None, sessionid=None, topic=None, group=None, timeout=None):
        self.topic = topic
        self.group = group

        msgSend = []
        if isinstance(data, list) or isinstance(data, tuple):
            for iMsg in data:
                msgSend.append(
                    MqttMsg(
                        topic=self.topic,
                        value=iMsg.getAttr(),
                        event=event,
                    ))
        else:

            msgSend.append(
                MqttMsg(
                    topic=self.topic,
                    value=data.getAttr(),
                    event=event,
                ))
        if len(msgSend) > 0:
            handle = None
            if callback and self.fqueue.isStarted():
                handle = self.fqueue.listen(callback=callback,
                                            key=event,
                                            sessionid=sessionid,
                                            params=params,
                                            # group=group,
                                            timeout=timeout,
                                            type=QueueInstance.TYPE_MQTT)
            # else:
            #     return None

            self.ctrl.send(msgSend)

            if handle is not None:
                handle.loop_until_done()
            return handle

        else:
            return QueueInstance()

    def listen(self, callback, params=None, sessionid=None, topic=None, group=None, key=None, timeout=None):
        self.ctrl.addCallbackHandle(callback,
                                    params=params,
                                    sessionid=sessionid,
                                    topic=topic,
                                    group=group,
                                    key=key,
                                    timeout=timeout)
