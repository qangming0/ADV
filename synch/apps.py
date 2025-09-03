import os
import sys
from django.apps import AppConfig


class SynchConfig(AppConfig):
    name = 'synch'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True

        import synch.receivers

        disBroker = os.getenv('BROKER_ALL_DISABLE', False)
        if not disBroker:
            from synch.startapp import startApp
            startApp()


