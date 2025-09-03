import sys
import os
from django.apps import AppConfig

class DeviceConfig(AppConfig):
    name = 'device'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True

        disBroker = os.getenv('BROKER_ALL_DISABLE', False)
        if not disBroker:
            # update status of device when app startup
            from device.status import updateStatus
            updateStatus()

