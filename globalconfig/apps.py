from django.apps import AppConfig


class GlobalConfig(AppConfig):
    name = 'globalconfig'

    def ready(self):
        import globalconfig.receivers
