#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import uuid
import os
from core.mqbroker.topic import Topic
# from synch.modules.common import KAFQueueSysnchorized
from synch.modules.common import MqttQueueSysnchorized

# class BaseSynDevice(object):
#     def __init__(self, event, callback=None, timeout=None):
#         self.event = event
#         self.sessionid = uuid.uuid4().hex
#         self.timeout = timeout if timeout is not None else os.getenv('REQUEST_TIMEOUT_MS', 100)
#         self.callbackHandler = callback
#         self.ctrl = KAFQueueSysnchorized()
#         self.fromTopic = Topic.C_APP_RECEIVE_GW
#
#     def syncDevice(self, cmdMsg):
#         pass


class BaseMqttSynDevice(object):
    def __init__(self, event, callback=None, timeout=None):
        self.event = event
        self.sessionid = uuid.uuid4().hex
        self.timeout = timeout if timeout is not None else os.getenv('REQUEST_TIMEOUT_MS', 10000)
        self.callbackHandler = callback
        self.ctrl = MqttQueueSysnchorized()
        self.fromTopic = Topic.C_APP_RECEIVE_GW

    def syncDevice(self, cmdMsg):
        pass


