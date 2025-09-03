#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from django.apps import AppConfig
from core.db.redis.rediscontroller import RedisController
from core.fqueue import FQueueJobSinger
from core.fchedulejob import FScheduleJob


class StartupConfig(AppConfig):
    name = 'startup'


    # def testJob(self, item):
    #     print(item)

    def ready(self):
        if 'runserver' not in sys.argv:
            return True

        # run receiver of modules

        # Thực hiện check start app mỗi khi khởi tạo thiết bị
        print('auto startup ..')

        # Start QueueJob
        # fqueue = FQueueJobSinger(threadnumb=5)
        # fqueue.start()
        rdis = RedisController()
        rdis.start()

        # start schedule job
        fjob = FScheduleJob()
        fjob.start()
        # fjob.everySeconds(self.testJob, interval=1)
        from .jobs import detect_device_status_change, onenet_content_to_send_device, detect_device_sync_timeout
        fjob.everySeconds(detect_device_status_change, interval=2)
        fjob.everySeconds(onenet_content_to_send_device, interval=int(os.getenv('ONENET_TIMEOUT', 5)))
        fjob.everySeconds(detect_device_sync_timeout, interval=3)
