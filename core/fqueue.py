#!/usr/bin/python
# -*- coding: utf-8 -*-


import queue
import threading
from abc import ABCMeta,abstractmethod
from core.message import FObject

JOBQ_EVT_NONE = 0x0001
JOBQ_EVT_SCHEDULE = 0x0002
JOBQ_EVT_DEVICESTATE = 0x0003

class MessageQueueFormat(FObject):
    def __init__(self, **kwargs):
        self.evt = kwargs.get('evt')
        self.token = kwargs.get('token')
        self.provider = kwargs.get('provider')
        self.sender = kwargs.get('sender')
        self.payload = kwargs.get('payload')
        self.params = kwargs.get('params')
        self.callback = kwargs.get('callback')

        # super.__init__(MessageQueueFormat, **kwargs)


class FQueue(object):
    _metaclass_ = ABCMeta

    def __init__(self, threadnumb = 1, callback=None):
        self.threadnumb = threadnumb
        self.job = queue.Queue()
        self.threads = []
        self.callback = callback

    # @abstractmethod
    # def callBackHandle(self, item):
    #     pass

    def handJob(self):
        while True:
            item = self.job.get()
            if item is None or item.evt is None:
                break
            # print(item)
            if self.callback is not None:
                self.callback(item)
            self.job.task_done()

    def start(self):
        for i in range(self.threadnumb):
            print('start thread job')
            pthead = threading.Thread(target=self.handJob)
            pthead.start()
            self.threads.append(pthead)

        # block until all tasks are done
        self.job.join()

    def stop(self):
        # stop workers
        for i in range(self.threadnumb):
            self.job.put(None)

        for pthead in self.threads:
            pthead.join()

    def publish(self, item = None):
        if isinstance(item, MessageQueueFormat):
            self.job.put(item)
        else:
            raise Exception('error match format')



class FQueueJobSinger(object):
    instance = None

    class __FQueueJobSinger:
        def __init__(self, threadnumb=1):
            self.fqueue = FQueue(threadnumb)

        def start(self):
            self.fqueue.start()

        def stop(self):
            self.fqueue.stop()

        def add(self, item):
            assert isinstance(item, MessageQueueFormat)
            self.fqueue.publish(item)

    def __new__(cls, threadnumb):
        if not FQueueJobSinger.instance:
            FQueueJobSinger.instance = FQueueJobSinger.__FQueueJobSinger(threadnumb = threadnumb)
        return FQueueJobSinger.instance

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)
