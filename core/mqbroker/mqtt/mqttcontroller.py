#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import logging
# import context
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from core.message import FObject, MqttMsg
from utils.jsonmsg import JsonMessage
from core.mqbroker.mqtt import mqttsubcriber, mqttpublisher
logger = logging.getLogger('django')

# class MQTTClient(mqtt.Client):
#     rc = 0
#     keepalive = 60
#     port = 1883
#     host = 'localhost'
#     def on_connect(self, mqttc, obj, flags, rc):
#         print("rc: " + str(rc))
#
#     def on_message(self, mqttc, obj, msg):
#         print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
#
#     def on_publish(self, mqttc, obj, mid):
#         print("mid: " + str(mid))
#
#     def on_subscribe(self, mqttc, obj, mid, granted_qos):
#         print("Subscribed: " + str(mid) + " " + str(granted_qos))
#
#     def on_log(self, mqttc, obj, level, string):
#         print(string)
#
#     def start(self):
#         self.connect(self.host, self.port, self.keepalive)
#     #     self.subscribe("$SYS/#", 0)
#     #
#     #     while self.rc == 0:
#     #         self.rc = self.loop()



class MQTTController(object):
    instance = None

    class __MQTTController:
        def __init__(self, **kwargs):
            # self.mqttc = MQTTClient()
            self.consumer = mqttsubcriber.FBaseMQTTSubcriber(**kwargs)
            self.producer = mqttpublisher.FBaseMQTTPublisher(**kwargs)
            self.running = False

        def start(self):
            if not self.running:
                # self.mqttc.start()
                self.consumer.start()
                self.producer.start()
                self.running = True
            else:
                pass

        def addTopicListen(self, topic):
            self.consumer.addTopic(topic)

        def removeTopicListen(self, topic):
            self.consumer.removeTopic(topic)

        def setTopicDefaultToSend(self, topics):
            self.producer.setTopicDefault(topics)

        def addCallbackHandle(self, callback, params=None, sessionid=None, topic=None, group=None, key=None, timeout=None):
            return self.consumer.addListen(callback, params=params, sessionid=sessionid, topic=topic, group=group,
                                           key=key, timeout=timeout)

        def send(self, msg):
            if isinstance(msg, list) or isinstance(msg, tuple):
                for iMsg in msg:
                    self.sendMsg(iMsg)
            else:
                if not isinstance(msg, MqttMsg):
                    logger.info('Message Format not match')
                    return None

                return self.producer.send(
                    topic=msg.topic,
                    value=msg.value,
                    # value=JsonMessage.dic2Byte(msg.value),
                    key=msg.event,
                    # key=JsonMessage.dic2Byte(msg.event),
                )

        def sendMsg(self, msg, callback=None, sessionid=None, params=None, topic=None, group=None, timeout=None):
            handle = None
            if callback:
                handle = self.consumer.addListen(callback=callback,
                                                 params=params,
                                                 sessionid=sessionid,
                                                 topic=topic,
                                                 group=group,
                                                 timeout=timeout)
            self.send(msg)

            if handle:
                handle.loop_until_done()
            return handle

        def stop(self):
            self.running = False

        def add(self, item):
            pass

    def __new__(cls, **kwargs):
        if not MQTTController.instance:
            MQTTController.instance = MQTTController.__MQTTController(**kwargs)
        return MQTTController.instance

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)
