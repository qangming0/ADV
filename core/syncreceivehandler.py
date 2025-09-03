from .dataglobal import LocalStore
from device.models import Device
from core.fqueue import FQueue, MessageQueueFormat
import datetime
from notify.process import NotifyWS

DEFAULT_TIMEOUT = 6


class SyncReceiveHandler:
    RESPONSE_TYPE_SUCCESS = 0
    RESPONSE_TYPE_FAILED = 1
    RESPONSE_TYPE_TIMEOUT = 2

    def __new__(cls):
        if not SyncReceiveHandler.__instance:
            SyncReceiveHandler.__instance = SyncReceiveHandler.__SyncReceiveHandler()
        return SyncReceiveHandler.__instance

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)

    class __SyncReceiveHandler:
        _KEY = 'SYNC_RECEIVE_HANDLER'
        _store = None
        _default = {
            'id': -1,
            'time': None,
            'timeout': DEFAULT_TIMEOUT,
        }

        EVT_KEY_UPDATE = 0x01
        EVT_KEY_UPDATE_REALTIME = 0x02
        EVT_KEY_DELETE = 0x03
        EVT_KEY_UPDATE_RESPONSE = 0x04

        def __init__(self):
            self._store = LocalStore()
            self._store.start(self._KEY)
            self.fqueue = FQueue(1, callback=self.handleQueue)
            self.fqueue.start()

        def handleQueue(self, item):
            if item.payload is not None:
                item.callback(item.payload)
            else:
                item.callback()

        def delAll(self):
            self._store.delete(self._KEY)

        def delElement(self, ident):
            self._store.delElement(self._KEY, ident)

        def getElement(self, ident):
            return self._store.getElement(self._KEY, ident)

        def create(self, lstData):
            self.delAll()
            self.update(lstData)

        def getAll(self, status=None):
            lstItem = self._store.get(self._KEY)
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
                    current_item = lstItem[str(key)]
                    val["users"] = val["users"] + current_item["users"]
                lstItemChange.update({str(key): val})
            return self._store.set(self._KEY, lstItemChange)

        def delete(self, ident):
            item = MessageQueueFormat(
                evt=self.EVT_KEY_DELETE,
                callback=self.queue_delete,
                payload=ident,
            )
            self.fqueue.publish(item)

        def queue_delete(self, ident):
            self._store.delElement(self._KEY, ident)

        def detect_timeout_request(self):
            lstRequest = self.getAll()
            timenow = datetime.datetime.now()
            for key, val in lstRequest.items():
                timediff = timenow - val['time']
                seconds = timediff.total_seconds()
                if int(seconds) > val['timeout']:
                    # remove from store
                    syncItem = self.getElement(key)
                    if syncItem is not None:
                        users = syncItem['users']
                        self.delete(key)

                        self.notify(ident=key, result=SyncReceiveHandler.RESPONSE_TYPE_TIMEOUT, users=users)

        def update_response(self, ident, result):
            item = MessageQueueFormat(
                evt=self.EVT_KEY_UPDATE_RESPONSE,
                callback=self.queue_update_reponse,
                payload={
                    "ident": ident,
                    "result": result
                },
            )
            self.fqueue.publish(item)

        def queue_update_reponse(self, payload):
            ident = payload['ident']
            result = payload['result']
            item = self.getElement(ident)
            users = None
            if item is not None:
                users = item['users']
            self.notify(ident, result, users)
            self._store.delElement(self._KEY, ident)

        def notify(self, ident, result, users):
            if users is None:
                return
            notify = NotifyWS()
            notify.notify_sync_result(ident, result, users)
    __instance = None
