#!/usr/bin/python
# -*- coding: utf8 -*-

from core.mqbroker.mqtt.mqttcontroller import MQTTController
from core.message import MqttMsg

class BasMqttSysnchorized(object):
    def __init__(self, topic=None, group=None):
        self.ctrl = MQTTController()
        self.topic = topic
        self.group = group
        self.sessionid = None

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
            return self.ctrl.sendMsg(msgSend, callback,
                                     params=params,
                                     sessionid=sessionid,
                                     topic=self.topic,
                                     group=self.group,
                                     timeout=timeout)
        else:
            return False

    def listen(self, callback, params=None, sessionid=None, topic=None, group=None, key=None, timeout=None):
        self.ctrl.addCallbackHandle(callback,
                                    params=params,
                                    sessionid=sessionid,
                                    topic=topic,
                                    group=group,
                                    key=key,
                                    timeout=timeout)
