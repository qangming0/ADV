#!/usr/bin/python
# -*- coding: utf8 -*-
__author__ = 'phuongtt'

import time
import os
import logging
import json
import datetime
import threading
import asyncio
from core.db.redis.rediscontroller import RedisController
from device.models import Device
from core.fqueue import FQueue, MessageQueueFormat, JOBQ_EVT_DEVICESTATE
logger = logging.getLogger('django')

class LocalStore(object):
    dictData = {}

    def start(self, fkey):
        self.dictData.update({fkey: {}})

    def delete(self, fkey):
        if fkey in self.dictData:
            self.dictData.update({fkey: {}})

    def get(self, fkey):
        if fkey in self.dictData:
            return self.dictData[fkey].copy()
        else:
            return {}

    def set(self, fkey, lstItem):
        for key, val in lstItem.items():
            self.dictData[fkey].update({key: val})

    def delElement(self, fkey, ident):
        if fkey in self.dictData:
            if ident in self.dictData[fkey]:
                del self.dictData[fkey][ident]

    def getElement(self, fkey, ident):
        if fkey in self.dictData:
            if ident in self.dictData[fkey]:
                return self.dictData[fkey][ident]
        return None


class RedisStore(object):
    rd = None
    key = None

    def start(self, fkey):
        if self.rd is None:
            self.rd = RedisController()
            self.rd.start()
        self.key = fkey

    def isStart(self):
        return self.rd is not None

    def delete(self, fkey):
        if self.isStart():
            for key in self.rd.scan_iter(match='{}*'.format(fkey)):
                self.rd.delete(key.decode('utf-8'))

    def get(self, fkey):
        res = {}
        if self.isStart():
            for key in self.rd.scan_iter(match='{}*'.format(fkey, )):
                res[(key.decode('utf-8')).replace(fkey, '')] = self.rd.get(key.decode('utf-8'))
        return res

    def set(self, fkey, lstItem):
        for key, val in lstItem.items():
            self.rd.set('{}{}'.format(fkey, key), val)

    def delElement(self, fkey, ident):
        self.rd.delete('{}{}'.format(fkey, ident))


class GlobalDeviceStatus:
    def __new__(cls):
        if not GlobalDeviceStatus.__instance:
            GlobalDeviceStatus.__instance = GlobalDeviceStatus.__GlobalDeviceStatus()
        return GlobalDeviceStatus.__instance
    def __getattr__(self, value):
        return getattr(self.__instance, value)
    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)

    class __GlobalDeviceStatus:
        _KEY = 'DEVICE_STATUS'
        _rdis = None
        _default = {
            'id': -1,
            'system': -1,
            'ip': '',
            'mac': '',
            'time': None,
            'status': False,
        }

        EVT_KEY_UPDATE = 0x01
        EVT_KEY_UPDATE_REALTIME = 0x02
        EVT_KEY_DELETE = 0x03
        EVT_KEY_DETECT_OFFLINE = 0x04

        def __init__(self):
            # self._rdis = RedisController()
            self._rdis = LocalStore()
            # self._rdis = RedisStore()
            self._rdis.start(self._KEY)
            self.fqueue = FQueue(1, callback=self.handleQueue)
            self.fqueue.start()

        def handleQueue(self, item):
            if item.payload is not None:
                item.callback(item.payload)
            else:
                item.callback()

        def updateModel(self, lstItem):
            for key, val in lstItem.items():
                try:
                    qs = Device.objects.get(id=val['id'])
                    if qs and (qs.dev_online != val['status'] or qs.dev_ip != val['ip'] or qs.dev_mac != val['mac']):
                        qs.dev_online = val['status']
                        qs.dev_ip = val['ip']
                        qs.dev_mac = val['mac']
                        qs.save()
                        print("'id': {}, 'ip': {}, 'mac': {}, 'status': {}".format(val['id'], val['ip'], val['mac'], val['status']))
                except:
                    pass

        def delAll(self):
            self._rdis.delete(self._KEY)

        def create(self, lstData):
            self.delAll()
            self.update(lstData)

        # {'122344':
        #   {
        #       'id': 1,
        #       'system': 'LIGHTING',
        #       'ip': '192.168.8.22',
        #       'mac': '00:11:22:33:44:55',
        #       'time': '2018-09-18 18:09:00',
        #       'status': 0}
        #   }
        def getAll(self, status=None):
            lstItem = self._rdis.get(self._KEY)
            if lstItem is None:
                return {}
            lstRes = {}
            if status is not None:
                for key, val in lstItem.items():
                    if val['status'] == status:
                        lstRes[key] = val
                return lstRes
            else:
                return lstItem

        def detectStatusOffline(self):
            item = MessageQueueFormat(
                evt=self.EVT_KEY_DETECT_OFFLINE,
                callback=self.queue_detectStatusOffline
            )
            self.fqueue.publish(item)

        def queue_detectStatusOffline(self):
            # get all device online
            # lstDeviceOn = self.getAll(status=True)
            lstDeviceOn = self.getAll()
            lstItemChange = {}
            timeNow = datetime.datetime.now()
            for key, val in lstDeviceOn.items():
                time = datetime.datetime.strptime(val['time'], '%Y-%m-%d %H:%M:%S')
                timediff = timeNow - time
                seconds = timediff.total_seconds()
                if val['status'] == True and int(seconds) > 6:
                    val['status'] = False
                    # send update status of device
                    # self.updateModel(
                    #     id = val['id'],
                    #     status = val['status'],
                    #     mac = val['mac'],
                    #     ip = val['ip']
                    # )
                    lstItemChange.update({str(key): val})
            if len(lstItemChange) > 0:
                self.updateModel(lstItemChange)
                self.queue_update(lstItemChange)

        def detectStatusChange(self, lstNewItemStatus):
            lstItem = self.getAll()
            lstItemChange = {}
            for key, val in lstNewItemStatus.items():
                if key in lstItem:
                    if val['ip'] != lstItem[key]['ip'] \
                            or val['mac'] != lstItem[key]['mac'] \
                            or val['status'] != lstItem[key]['status']:
                        # update device
                        # self.updateModel(
                        #     id=val['id'],
                        #     status=val['status'],
                        #     mac=val['mac'],
                        #     ip=val['ip']
                        # )
                        lstItemChange.update({str(key): val})
            if len(lstItemChange) > 0:
                self.updateModel(lstItemChange)

        # params : {'122344': {'ip': '192.168.8.22', 'mac': '00:11:22:33:44:55', 'status': 1}, ...}
        def update(self, lstData):
            item = MessageQueueFormat(
                evt=self.EVT_KEY_UPDATE,
                callback=self.queue_update,
                payload=lstData,
            )
            self.fqueue.publish(item)

        def queue_update(self, lstData):
            lstItem = self.getAll()
            lstItemChange = {}
            for key, val in lstData.items():
                if str(key) in lstItem:
                    lstItemChange.update({str(key): {**lstItem[str(key)], **val}})
                else:
                    val['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    lstItemChange.update({str(key): val})
            self.detectStatusChange(lstItemChange)
            self._rdis.set(self._KEY, lstItemChange)


        def updateRealtime(self, lstData):
            item = MessageQueueFormat(
                evt=self.EVT_KEY_UPDATE_REALTIME,
                callback=self.queue_updateRealtime,
                payload=lstData,
            )
            self.fqueue.publish(item)

        def queue_updateRealtime(self, lstData):
            lstItem = self.getAll()
            lstItemChange = {}
            for key, val in lstData.items():
                if str(key) in lstItem:
                    val['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    lstItemChange.update({str(key): {**lstItem[str(key)], **val}})
            if len(lstItemChange) > 0:
                self.detectStatusChange(lstItemChange)
                self._rdis.set(self._KEY, lstItemChange)

        def delElement(self, ident):
            self._rdis.delElement(self._KEY, ident)

    __instance = None

