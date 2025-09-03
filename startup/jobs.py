import logging
import sys
import os
from core.dataglobal import GlobalDeviceStatus
from core.syncreceivehandler import SyncReceiveHandler
from synch.modules.adv.adv_view import AdvSync
logger = logging.getLogger('django')

def detect_device_status_change(item):
    logger.debug('==============>detect_device_status_change')
    gds = GlobalDeviceStatus()
    gds.detectStatusOffline()


def onenet_content_to_send_device(item):
    logger.debug('==============>onenet_content_to_send_device')
    sync = AdvSync()
    sync.sendNotice()

def detect_device_sync_timeout(item):
    srh = SyncReceiveHandler()
    srh.detect_timeout_request()
