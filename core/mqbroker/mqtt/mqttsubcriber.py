#!/usr/bin/python
# -*- coding: utf8 -*-


import logging
import threading
import queue
import uuid
import sys
import time
import six
# from multiprocessing import Pool
# import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
from abc import ABCMeta,abstractmethod
from utils.jsonmsg import JsonMessage
from core.message import FObject, MqttMsg
logger = logging.getLogger('django')

'''
    Asynchronous base consumer
'''


class ConsumInstance(FObject):
    def __init__(self, **kwargs):
        self.consumer = None
        self.callback = None
        self.params = None
        self.data = None # KafMsq
        self.pthead = None
        self.uid = None
        self.key = None
        self.sessionid = None
        self.timeout = None #minisecon
        self.stop_event = False
        self.is_connected = None
        super(ConsumInstance, self).__init__(**kwargs)

    def start(self):
        self.stop_event = False
        if self.pthead:
            self.pthead.start()

    def loop_until_done(self):
        if self.pthead:
            self.pthead.join()
            # self.consumer.close()
            # self.callback = None

    def done(self):
        print('\ndone consum handle thread')
        self.stop_event = True
        # self.consumer.close()

class ConsumHandleMsg(object):
    handle = None

    def __on_message(self, client, userdata, message):
        try: # if message.topic == 'onenet/request':
            value = JsonMessage.decode((message.payload).decode('utf8', 'ignore'))
            logger.debug("topic: {} received message ={}".format(message.topic, str(value)))

            if self.handle.sessionid:
                if 'sessionid' in value:
                    if self.handle.sessionid != value['sessionid']:
                        return
                else:
                    return

            if self.handle.key:
                if self.handle.key != value['event']:
                    return

            self.handle.data = MqttMsg(
                topic = str(message.topic),
                # partition = str(message.partition),
                timestamp = str(message.timestamp),
                value = value,
                event = value['event'] if 'event' in value else None,
                sessionid = value['sessionid'] if 'sessionid' in value else None,
            )
            self.handle.callback(self.handle)
        except Exception as ex:
            logger.error(str(ex))

    def __on_connect(self, client, data, flags, rc):
        if rc == mqtt.CONNACK_ACCEPTED:
            logging.info("===========================MQTT connected.")
            self.handle.is_connected.set()
        else:
            logging.info('MQTT connection failed: {}'.format(rc))

    def __on_disconnect(self, client, userdata, rc):
        logger.info("A subcriber is been disconneted")

    def callback(self, obj, uid, mqTopics, mqCfgs):
        self.handle = obj.gethandle(uid)
        # if self.handle:
            # connect message queue
            # while self.handle.consumer is None:
            #     try:
            #         logger.info('try create consummer({uid}) ...'.format(uid=uid))
            #         authen = mqCfgs.pop('authen')
            #         consumer = mqtt.Client(uid, clean_session=False)
            #         consumer.on_message = self.on_message
            #         consumer.on_connect = self.on_connect
            #         consumer.on_disconnect = self.on_disconnect
            #         if authen:
            #             if authen['mode'] == 0:
            #                 consumer.username_pw_set(username=authen['user'], password=authen['password'])
            #             else:
            #                 # TODO: set authen throw ssl
            #                 # consumer.tls_set("ssl")
            #                 pass
            #         consumer.connect(host=str(mqCfgs['host']), port=int(mqCfgs['port']), keepalive=int(mqCfgs['keepalive']))
            #         self.handle.consumer = consumer
            #     except Exception as ex:
            #         print(ex)
            #         logger.warning('consummer mqtt({uid}) disconnected'.format(uid=uid))
            #     if self.handle.consumer is not None:
            #         break
            #     time.sleep(2)
            # logger.info('create consummer mqtt({uid}) connected'.format(uid=uid))
            # register topic without qos

            # self.handle.consumer.subscribe(mqTopics)

            # while not self.handle.stop_event:
            #     try:
            #         self.handle.consumer.loop()  # blocks for 100ms
            #         # time.sleep(1)
            #     except Exception as ex:
            #         logger.exception(str(ex))
            #     finally:
            #         if self.handle.stop_event:
            #             self.obj.delHandleCallback(uid=uid)

            ## self.handle.consumer.loop_forever()

            # self.handle.consumer.disconnect() #disconnect
            # self.handle.consumer.loop_stop()  # stop loop
        # ==============================================
        if self.handle and not self.handle.is_connected.is_set():
            try:
                authen = mqCfgs.pop('authen')
                consumer = mqtt.Client(uid, clean_session=False)
                consumer.on_message = self.__on_message
                consumer.on_connect = self.__on_connect
                consumer.on_disconnect = self.__on_disconnect
                if authen:
                    if authen['mode'] == 0:
                        consumer.username_pw_set(username=authen['user'], password=authen['password'])
                    else:
                        # TODO: set authen throw ssl
                        # consumer.tls_set("ssl")
                        pass
                consumer.connect(host=str(mqCfgs['host']), port=int(mqCfgs['port']), keepalive=int(mqCfgs['keepalive']))
                consumer.subscribe(mqTopics)
                consumer.loop_start()

                # Wait until we've connected
                self.handle.is_connected.wait()

                logger.info('create consummer mqtt({uid}) connected'.format(uid=uid))

                self.handle.consumer = consumer

                # Wait until handle timeout
                while not self.handle.stop_event:
                    time.sleep(1)

                self.obj.delHandleCallback(uid=uid)
                self.handle.consumer.disconnect() #disconnect
                self.handle.consumer.loop_stop()  # stop loop

            except Exception as ex:
                logger.warning('consummer mqtt({uid}) disconnected'.format(uid=uid))


class FBaseMQTTSubcriber():
    _metaclass_ = ABCMeta

    def __init__(self, **kwargs):
        self.topics = []
        self.callbacks = []
        self.threadhandles = []
        self._lock = threading.Lock()
        self.job = None
        self.stop_event = False
        self.qos = 1

        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 1883)
        self.authen = kwargs.get('authen', None)
        self.timeout_ms = kwargs.get('timeout_ms', 60)
        # self.group_id = kwargs.get('group_id', None)
        self._topics = kwargs.get('topic', None)

        if self._topics:
            if isinstance(self._topics, (list, tuple)):
                self.topics = [topic for topic in self._topics]
            else:
                self.topics.append(self._topics)

        self.configs = {
            'host': self.host,
            'port': self.port,
            'keepalive': self.timeout_ms,
            'authen': self.authen,
            # 'group_id': self.group_id,
        }

        self.message = None

    def __updateTopic(self):
        if len(self.threadhandles) > 0:
            # for handle in self.threadhandles:
            #     handle.consumer.subscribe(self.topics)
            pass

    def __isCallbackExist(self, callback=None, uid=None):
        for handle in self.threadhandles:
            if handle.callback == callback or handle.uid == uid:
                return handle
        return None

    def delHandleCallback(self, callback=None, uid=None):
        try:
            if callback or uid:
                handle = self.__isCallbackExist(callback=callback, uid=uid)
                if handle:
                    handle.pthead.join()
                    handle.consumer.close()
                    self.threadhandles.remove(handle)
            else:
                for handle in self.threadhandles:
                    self.delHandleCallback(handle.callback)
        except Exception as ex:
            print(str(ex))

    def gethandle(self, uid):
        for handle in self.threadhandles:
            if handle.uid == uid:
                return handle
        return None

    def addTopic(self, topic):
        self.topics.append(topic)
        self.__updateTopic()

    def removeTopic(self, topic):
        if topic in self.topics:
            self.topics.remove(topic)
        self.__updateTopic()

    def addListen(self, callback=None, sessionid=None, params=None, topic=None, group=None, key=None, timeout=None):
        if self.__isCallbackExist(callback) is None:
            uid = uuid.uuid4().hex
            try:
                topics = self.topics.copy()
                configs = self.configs.copy()

                if group:
                    configs['group_id'] = group
                if topic:
                    topics = [topic]

                mqttTopics = []
                for tp in topics:
                    mqttTopics.append((tp, self.qos))

                handleMsg = ConsumHandleMsg()
                pthead = threading.Thread(target=handleMsg.callback , args=(self, uid, mqttTopics, configs))

                self.callbacks.append(callback)

                cnmInstance = ConsumInstance(
                    callback = callback,
                    uid = uid,
                    key = key,
                    pthead = pthead,
                    consumer = None,
                    sessionid = sessionid,
                    params = params,
                    timeout = timeout,
                    is_connected = threading.Event()
                )

                self.threadhandles.append(cnmInstance)
                cnmInstance.start()
                return cnmInstance
            except Exception as ex:
                print(ex)

    def removeListen(self, callback):
        self.delHandleCallback(callback)

    def start(self):
        self.job = queue.Queue()
        self.stop_event = False

    def stop(self):
        self.job.put(None)
        self.stop_event = True
        self.delHandleCallback()
        # self.consumer.close()
