import schedule
import threading
import time
from core.fqueue import FQueue, MessageQueueFormat, JOBQ_EVT_SCHEDULE

class FScheduleJob(object):
    '''
        running schdule job by thread without celery
    '''
    instance = None

    class FScheduleJob:
        pthead = None
        fqueue = None
        def __init__(self):
            pass

        def handJob(self, trigger):
            while not trigger.is_set():
                schedule.run_pending()
                time.sleep(1)

        def executeJob(self, item):
            item.callback(item)

        def startQueue(self):
            if self.fqueue is None:
                self.fqueue = FQueue(2, callback=self.executeJob)
                self.fqueue.start()

        def stopQueue(self):
            if self.fqueue is not None:
                self.fqueue.stop()

        def start(self):
            if self.pthead is None:
                self.trigger = threading.Event()
                self.pthead = threading.Thread(target=self.handJob, args=(self.trigger, ))
                self.pthead.start()
                self.startQueue()

        def restart(self):
            if self.pthead is not None:
                self.trigger.set()
                # self.trigger.wait()
                # self.pthead.join()
                self.stopQueue()
            self.pthead = None
            self.start()

        def stop(self):
            if self.pthead is not None:
                self.trigger.set()
        '''
            unit = 
            0: seconds, 1:minutes, 2:hours, 3:day
        '''
        # def add(self, callback, args, interval=1, unit=0):
        #     if self.pthead is not None:
                # schedule.every(interval).seconds.do(callback, **args)
        # def add(self, interval=1):
        #     return schedule.every(interval)

        def everySeconds(self, callback, interval=1):
            if self.pthead is not None and self.fqueue is not None:
                item = MessageQueueFormat(
                    evt = JOBQ_EVT_SCHEDULE,
                    callback = callback,
                    sender = schedule,
                )
                schedule.every(interval).seconds.do(self.fqueue.publish, item)

    def __new__(cls):
        if not FScheduleJob.instance:
            FScheduleJob.instance = FScheduleJob.FScheduleJob()
        return FScheduleJob.instance

    def __getattr__(self, value):
        return getattr(self.__instance, value)

    def __setattr__(self, key, value):
        return setattr(self.__instance, key, value)
