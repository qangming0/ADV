from __future__ import absolute_import, unicode_literals
#!/usr/bin/python
# -*- coding: utf8 -*-
__author__ = 'phuongtt'

import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ADVX.settings')

# app = Celery('proj', include=['test_celery.tasks'])
app = Celery('ADVX', include=['startup.tasks'])

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks(['ADVX.startup'], force=True)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    beat_scheduler='django_celery_beat.schedulers.DatabaseScheduler',
)

