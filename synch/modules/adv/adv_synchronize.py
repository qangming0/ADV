#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import uuid
from core.mqbroker.topic import Topic
from core.message import PublisMessage
from synch.modules.common import synchronize
from notify.process import NotifyWS


class AdvSynch(synchronize.BaseMqttSynDevice):
    def syncDevice(self, cmdMsg):
        count = len(cmdMsg)
        data = []
        for msg in cmdMsg:
            data.append(
                PublisMessage(
                    data=json.loads(msg['data']['datasend']),
                    fromAddr=Topic.C_APP_RECEIVE_SYNC_GW,
                    toAddr=[msg['data']['toaddr']],
                    sessionid=self.sessionid,
                )
            )
        notify = NotifyWS()
        notify.notify_update_dev_sync()

        res = self.ctrl.send(
            self.event,
            data,
            self.callbackHandler,
            params={'count': count, 'msg': cmdMsg},
            sessionid=self.sessionid,
            timeout=self.timeout,
            topic=Topic.DEVICE_RECEIVE
        )

        return res


class OneNetSynch(synchronize.BaseMqttSynDevice):
    def syncDevice(self, cmdMsg):
        count = len(cmdMsg)
        data = []
        for msg in cmdMsg:
            data.append(
                PublisMessage(
                    data=msg['data']['datasend'],
                    fromAddr=self.fromTopic,
                    toAddr=[msg['data']['toaddr']],
                    sessionid=self.sessionid,
                )
            )

        res = self.ctrl.send(
            self.event,
            data,
            self.callbackHandler,
            params={'count': count, 'msg': cmdMsg},
            sessionid=self.sessionid,
            timeout=self.timeout,
            topic=Topic.DEVICE_RECEIVE
        )

        return res