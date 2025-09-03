import threading
import queue
import uuid
import sys
import asyncio
import random
from core.message import FObject

class QueueInstance(FObject):
    TYPE_KAFKA = 0
    TYPE_MQTT = 1
    TYPE_WEBSOCKET = 2

    def __init__(self, **kwargs):
        self.errors = []
        self.devResState = {
            'success': [],
            'failed': [],
            'offlines': [],
        }
        self.queueIns = None
        self.callback = None
        self.params = None
        self.data = None # KafMsq
        self.pthead = None
        self.uid = None
        self.key = None
        self.sessionid = None
        self.timeout = None #minisecon
        self.stop_event = False
        self.tasks = None
        self.success = False
        self.totalItemReceived = 0
        self.dataRes = None
        self.type = self.TYPE_KAFKA

        super(QueueInstance, self).__init__(**kwargs)

    def start(self):
        self.stop_event = False
        if self.pthead:
            self.pthead.start()

    def done(self):
        print('done queue handle thread')
        self.stop_event = True
        if self.queueIns:
            self.queueIns.put(None)
        if self.tasks is not None:
            for task in self.tasks:
                if not task.cancelled():
                    task.cancel()

    def loop_until_done(self):
        if self.pthead:
            # block until all tasks are done
            self.pthead.join()
            self.queueIns.join()
            self.done()

    def push(self, item):
        if self.queueIns:
            # self.queueIns.put(item)
            self.queueIns.put_nowait(item)
        else:
            print('Queue Instance is not found')

    def hasError(self):
        if len(self.errors) > 0:
            return True
        else:
            return False

    def getErrMsg(self):
        return self.errors

    def addErr(self, msg):
        self.errors.append(msg)


class FQueueController(object):
    instance = None

    class __FQueueController:
        def __init__(self, **kwargs):
            self.running = False
            self.threadhandles = []

        def start(self):
            if not self.running:
                self.running = True
            else:
                pass

        def isStarted(self):
            return self.running

        def stop(self):
            self.running = False

        def __isExist(self, callback=None, uid=None):
            for handle in self.threadhandles:
                if handle.callback == callback or handle.uid == uid:
                    return handle
            return None

        def __delHandle(self, callback=None, uid=None):
            try:
                if callback or uid:
                    handle = self.__isExist(callback=callback, uid=uid)
                    if handle:
                        # if handle.pthead:
                        #     handle.pthead.join()
                        self.threadhandles.remove(handle)
                else:
                    for handle in self.threadhandles:
                        self.__delHandle(handle.callback)
            except Exception as ex:
                print(str(ex))

        def __getHandleByUid(self, uid):
            for handle in self.threadhandles:
                if handle.uid == uid:
                    return handle
            return None

        async def waitingOvertime(self, handle):
            while True:
                if handle.stop_event:
                    break
                if handle.timeout is not None:
                    if handle.timeout <= 0:
                        print('WaitingOvertime complete ')
                        handle.done()
                    else:
                        handle.timeout -= 1
                        print("\rwaiting_overtime .. " + str(handle.timeout), end='', flush=True)
                await asyncio.sleep(0.1)

        async def loopUntilDone(self, handle):
            count = handle.timeout
            while not handle.stop_event:
                # wait for an item
                item = await handle.queueIns.get()
                if item is None:
                    break
                # print('consuming item {}...'.format(item))
                handle.timeout = count
                handle.data = item
                handle.callback(handle)

                # simulate i/o operation using sleep
                # await asyncio.sleep(1)

        def handleMsg(self, uid):
            handle = self.__getHandleByUid(uid)
            if handle:
                asyncio.set_event_loop(asyncio.new_event_loop())
                loop = asyncio.get_event_loop()

                handle.queueIns = asyncio.Queue(loop=loop)

                tasks = [
                    asyncio.ensure_future(self.loopUntilDone(handle)),
                    asyncio.ensure_future(self.waitingOvertime(handle)),
                ]

                handle.tasks = tasks

                loop.run_until_complete(asyncio.wait(tasks))
                loop.close()
                self.__delHandle(uid=uid)
            else:
                pass

        def listen(self, callback=None, sessionid=None, params=None, key=None, timeout=None, type=QueueInstance.TYPE_KAFKA):
            uid = uuid.uuid4().hex
            handle = None
            try:

                pthead = threading.Thread(target=self.handleMsg, args=(uid,))

                handle = QueueInstance(
                    callback=callback,
                    uid=uid,
                    key=key,
                    pthead=pthead,
                    sessionid=sessionid,
                    params=params,
                    timeout=timeout,
                    type=type
                )

                self.threadhandles.append(handle)
                handle.start()

            except Exception as ex:
                print(ex)

            finally:
                return handle

        def getQueues(self, type=QueueInstance.TYPE_KAFKA):
            lstQueues = []
            for handle in self.threadhandles:
                if handle.type == type:
                    lstQueues.append(handle)
            return lstQueues

    def __new__(cls, **kwargs):
        if not FQueueController.instance:
            FQueueController.instance = FQueueController.__FQueueController(**kwargs)
        return FQueueController.instance

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)
