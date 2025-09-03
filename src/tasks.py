from __future__ import absolute_import, unicode_literals
import logging
import os
import sys
from datetime import timedelta
from celery import Celery
from celery import task
from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from core.dataglobal import GlobalDeviceStatus
from device.models import Device
from synch.modules.adv.adv_view import AdvSync
logger = logging.getLogger('django')

app = Celery('ADVX')

@periodic_task(
    run_every=timedelta(seconds=2),
    name="task_detect_device_status_change",
    # ignore_result=True
)
def detectDeviceStatusChange():
    logger.debug('==============>detectDeviceStatusChange')
    gds = GlobalDeviceStatus()
    gds.detectStatusOffline()


@periodic_task(
    run_every=timedelta(seconds=os.getenv('ONENET_TIMEOUT', 5)),
    name="task_onenet_content_to_send_device",
)
def onenet_content_to_send_device():
    logger.info('==============>onenet_content_to_send_device')
    sync = AdvSync()
    sync.sendNotice()





