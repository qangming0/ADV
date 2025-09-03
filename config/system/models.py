#!/usr/bin/python
# -*- coding: utf8 -*-

from django.utils.translation import gettext_lazy as _, gettext
from core.models import CoreModel
from django.db import models


class System(object):
    TYPE_UNKNOWN            = 0
    TYPE_ACCESS_CONTROLLER  = 1
    TYPE_LIFT               = 2
    TYPE_PARKING            = 3
    TYPE_LIGHTING           = 4
    TYPE_ADVERTIS           = 5
    TYPE_FIRE_ESCAPE        = 6

    TYPE_CHOICES = (
        (TYPE_UNKNOWN, _('UnKnown')),
        (TYPE_ACCESS_CONTROLLER, _('Access Controller')), # quan ly vao ra
        (TYPE_LIFT, _('Lift')), # thang may
        (TYPE_PARKING, _('Car Parking')), # bai dau xe
        (TYPE_LIGHTING, _('Lighting')), # chieu sang
        (TYPE_ADVERTIS, _('advertis')), # quang cao
        (TYPE_FIRE_ESCAPE, _('Fire Escape')), # cua thoat hiem
    )

    TYPE_SELECT = [
        TYPE_ACCESS_CONTROLLER,
        TYPE_LIFT,
        TYPE_PARKING,
        TYPE_LIGHTING,
        TYPE_ADVERTIS,
        TYPE_FIRE_ESCAPE,
    ]


    ATTR_RW = 0
    ATTR_R = 1

    ATTR_CHOICES= (
        (ATTR_RW, _('All read write')),
        (ATTR_R, _('Read only')),
    )


class SystemConfig(models.Model):
    CONST_SWITCH_ON = 1
    CONST_SWITCH_OFF = 0

    cfg_key = models.CharField(max_length=255, unique=True)
    cfg_value = models.TextField()
    cfg_note = models.TextField()

    class Meta:
        db_table = 'TblF9SystemConfig'

