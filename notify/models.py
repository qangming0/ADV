#!/usr/bin/python
# -*- coding: utf8 -*-

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext
from core.models import CoreModel, CoreModelManager, CoreModelQuerySet
from authen.models import User


class NotifyQuerySet(CoreModelQuerySet):
    pass


class NotifyManager(CoreModelManager):
    def get_queryset(self):
        return NotifyQuerySet(self.model, using=self._db)


class Notify(CoreModel):
    TYPE_SUCCESS = 'success'
    TYPE_INFO = 'info'
    TYPE_WARNING = 'warning'
    TYPE_ERROR = 'error'

    TYPE_CHOICES = (
        (TYPE_SUCCESS, _('Success')),
        (TYPE_INFO, _('Info')),
        (TYPE_WARNING, _('Warning')),
        (TYPE_ERROR, _('Error'))
    )

    LEVEL_NORMAL = 0
    LEVEL_MEDIUM = 1
    LEVEL_GRAVITY = 2
    LEVEL_DANGEROUS = 3

    LEVEL_CHOICES = (
        (LEVEL_NORMAL, _('Normal')),
        (LEVEL_MEDIUM, _('Medium')),
        (LEVEL_GRAVITY, _('Gravity')),
        (LEVEL_DANGEROUS, _('Dangerous'))
    )

    ntf_name = models.CharField(max_length=50, unique=True)
    # ntf_system = models.SmallIntegerField(choices=System.TYPE_CHOICES, default=System.TYPE_UNKNOWN)
    ntf_type = models.CharField(choices=TYPE_CHOICES, default=TYPE_INFO,max_length=15)
    ntf_level = models.SmallIntegerField(choices=LEVEL_CHOICES, default=LEVEL_NORMAL)
    ntf_message = models.TextField(max_length=3000)
    ntf_message_html = models.TextField()
    ntf_users = models.ManyToManyField(User, through='usernotify', through_fields=('uny_notify', 'uny_user'), blank=True, related_name='notify')

    objects = NotifyManager()

    def __str__(self):
        return '{}-{}-{}'.format(self.ntf_name, self.get_ntf_type_display(), self.get_ntf_level_display())


class UserNotify(CoreModel):
    uny_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usernotify')
    uny_notify = models.ForeignKey(Notify, on_delete=models.CASCADE, related_name='usernotify')
    uny_viewed = models.BooleanField(default=False)

    class Meta:
        unique_together = (("uny_user", "uny_notify"),)


class ChannelGroup(CoreModel):
    cgp_name = models.CharField(max_length=50)
    cgp_code = models.CharField(max_length=50, unique=True)
    cgp_users = models.ManyToManyField(User, blank=True, related_name='channelgroup')