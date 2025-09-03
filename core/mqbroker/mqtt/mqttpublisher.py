#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import time
import queue
import threading
import uuid
import logging
import string
import random
# from mqtt import mqttpublisher
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from abc import ABCMeta,abstractmethod
from utils.jsonmsg import JsonMessage, id_generator
logger = logging.getLogger('django')

class FBaseMQTTPublisher():
    _metaclass_ = ABCMeta

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 9092)
        self.timeout_ms = kwargs.get('timeout_ms', 60)
        self.authen = kwargs.get('authen', None)
        self.qos = 1
        self.topic = None
        self.publisher = None
        self.message = None

    def handJob(self):
        self.reconnect()

    def __on_publish(mqttc, obj, mid):
        print("===================mid: " + str(mid))

    def __on_connect(self, client, data, flags, rc):
        if rc == mqtt.CONNACK_ACCEPTED:
            logger.info('A publiser is connected ')
            if self.publisher:
                self.publisher.is_connected.set()
        else:
            logging.info('MQTT connection failed: {}'.format(rc))

    def __on_disconnect(self, client, userdata, rc):
        logger.info("A publiser is been disconneted")

    def reconnect(self):
        mqCfgs = {
            'host': self.host,
            'port': self.port,
            'keepalive': self.timeout_ms,
            'authen': self.authen,
        }

        try:
            logger.info('publisher is trying connect mqtt ...')
            publisher = mqtt.Client(uuid.uuid4().hex)
            publisher.on_connect = self.__on_connect
            publisher.on_disconnect = self.__on_disconnect
            publisher.on_publish = self.__on_publish
            publisher.is_connected = threading.Event()
            self.publisher = publisher

            authen = mqCfgs.pop('authen')
            if authen:
                if authen['mode'] == 0:
                    self.publisher.username_pw_set(username=authen['user'], password=authen['password'])
                else:
                    pass
                    # TODO: set authen throw ssl
                    # consumer.tls_set("ssl")
            self.publisher.connect(host=str(mqCfgs['host']), port=int(mqCfgs['port']), keepalive=int(mqCfgs['keepalive']))
            self.publisher.loop_start()

            # Wait until we've connected
            self.publisher.is_connected.wait()
        except Exception as ex:
            logger.warning('publisher disconnected')

    def start(self):
        try:
            self.pthead = threading.Thread(target=self.handJob)
            self.pthead.start()
        except Exception as ex:
            print(ex)

    def setTopicDefault(self, topic):
        self.topic = topic

    def rawSend(self, topic, value):
        try:
            logger.info('publisher send to topic: {}'.format(topic, ))
            result, mid = self.publisher.publish(topic, JsonMessage.encode(value), qos=1)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logging.info("Message {} queued successfully.".format(mid))
                return True
            else:
                logging.error("Failed to publish message. Error: {}".format(result))
        except Exception as ex:
            logger.error(str(ex))

        return False

    @abstractmethod
    def send(self, value, key, topic=None, partition=0, timestamp_ms=60):
        logger.info('mqtt publisher begin send to topic device')
        if not topic:
            if self.topic:
                topic = self.topic
            else:
                logger.info('Has not anytopic to send')
                return False
        try:
            devid = value['toAddr'][0]
            value['event'] = key
            sendTopic = '{}/{}'.format(topic, devid)
            res = self.rawSend(sendTopic, value)
            logger.info('mqtt publisher send to topic: {} of device: {} is {}'.format(sendTopic, devid, res))
            return res
        except Exception as ex:
            logger.error(str(ex))
            return False

    def stop(self):
        self.pthead.join()
        logger.info("mqttpublisher stop")