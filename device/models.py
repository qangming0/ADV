#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext
from core.models import CoreModel, CoreModelManager, CoreModelQuerySet
from config.provider.models import Provider
from config.system.models import System
from globalconfig.models import Door, Building, Zone
from media.models import Media


def generate_access_token():
    return uuid.uuid4().hex

class DeviceQuerySet(CoreModelQuerySet):
    def is_active(self):
        return self.filter(dev_state=Device.STATE_ACTIVE)

    def is_system(self, key):
        return self.filter(dev_system=key)


class DeviceManager(CoreModelManager):
    def get_queryset(self):
        return DeviceQuerySet(self.model, using=self._db)

    def get_active(self):
        return self.get_queryset().is_active()

    def getUnKnown(self):
        return self.get_queryset().is_system(System.TYPE_UNKNOWN)

    def getParking(self):
        return self.get_active().is_system(System.TYPE_PARKING)

    def getAccessController(self):
        return self.get_active().is_system(System.TYPE_ACCESS_CONTROLLER)

    def getLift(self):
        return self.get_active().is_system(System.TYPE_LIFT)

    def getLighting(self):
        return self.get_active().is_system(System.TYPE_LIGHTING)

    def getAdvertis(self):
        return self.get_active().is_system(System.TYPE_ADVERTIS)

    def getFireEscape(self):
        return self.get_active().is_system(System.TYPE_FIRE_ESCAPE)


class Device(CoreModel):

    TYPE_UNKNOWN     = 0
    TYPE_DEVICE      = 1
    TYPE_DI          = 2
    TYPE_GATEWAY     = 3

    TYPE_CHOICES = (
        (TYPE_UNKNOWN, _('UnKnown')),
        (TYPE_DEVICE, _('Device')), # Thiết bị
        (TYPE_DI, _('Device Interface')), # Device Interface
        (TYPE_GATEWAY, _('Gateway')), # Gateway
    )

    STATE_INACTIVE = 0
    STATE_ACTIVE = 1

    STATE_CHOICES = (
        (STATE_INACTIVE, _('InActive')), # Cấm
        (STATE_ACTIVE, _('Active')), # Kích hoạt
    )

    SYNC_STATE_DONE = 0
    SYNC_STATE_FAILED = 1
    SYNC_STATE_WAITING = 2

    SYNC_STATE_CHOICES = (
        (SYNC_STATE_DONE, _('Done')),
        (SYNC_STATE_FAILED, _('Failed')),
        (SYNC_STATE_WAITING, _('Waiting')),
    )

    dev_name = models.CharField(max_length=50, unique=True)
    dev_ip = models.CharField(max_length=50, blank = True, null = True)
    dev_mac = models.CharField(max_length=30, blank = True, null = True)
    dev_ident = models.CharField(max_length=50, unique=True, blank = True, null = True)
    dev_access_token = models.CharField(max_length=50, default=generate_access_token, unique=True)
    dev_sessionid = models.CharField(max_length=50, blank = True, null = True, unique=True)

    dev_provider = models.ForeignKey(Provider, on_delete=models.CASCADE, blank = True, null = True)
    dev_system = models.SmallIntegerField(choices=System.TYPE_CHOICES, default=System.TYPE_UNKNOWN)
    dev_attr = models.SmallIntegerField(choices=System.ATTR_CHOICES, default=System.ATTR_RW)

    dev_type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_UNKNOWN)
    dev_state = models.SmallIntegerField(choices=STATE_CHOICES, default=STATE_INACTIVE)
    dev_online = models.BooleanField(default=False)

    dev_parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    dev_info = models.CharField(max_length=100, blank = True, null = True)

    dev_building = models.ForeignKey(Building, on_delete=models.SET_NULL, blank=True, null=True)

    dev_zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, blank=True, null=True)

    dev_sync_state = models.SmallIntegerField(choices=SYNC_STATE_CHOICES, default=SYNC_STATE_DONE)

    # for adv
    dev_diskspace = models.IntegerField(blank=True, null=True)
    dev_mediaplay = models.ForeignKey(Media, on_delete=models.SET_NULL, blank=True, null=True)
    # version of software
    dev_software_version = models.CharField(max_length=10, default='0.0.0', blank=True, null=True)

    objects = DeviceManager()

    def __str__(self):
        return '{}-{}-{}'.format(self.dev_name, self.dev_mac, self.dev_info)

    class Meta:
        db_table = 'device'

    @property
    def lift_full_name(self):
        if hasattr(self, 'lift'):
            return self.lift.lift_full_name
        return ''

    @property
    def dev_building_name(self):
        if self.dev_building is not None:
            return self.dev_building.bdg_name
        return ''

    @property
    def dev_zone_name(self):
        if self.dev_zone is not None:
            return self.dev_zone.zone_name
        return ''

    @property
    def dev_floor_name(self):
        if self.dev_zone is not None:
            return self.dev_zone.zone_floor.flr_name
        return ''

    @property
    def dev_floor(self):
        if self.dev_zone is not None:
            return self.dev_zone.zone_floor.id
        return None

    @property
    def dev_position_full(self):
        try:
            if self.dev_zone:
                return '{} - {} - {}'.format(self.dev_zone_name, self.dev_floor_name, self.dev_building_name)
            else:
                return ''
        except Exception as ex:
            return ''


class DeviceLine(CoreModel):
    dle_dev = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='deviceline')
    dle_ident = models.IntegerField(blank = True, null = True)

    class Meta:
        db_table = 'device_line'
        unique_together = ('dle_dev', 'dle_ident',)

    def __str__(self):
        return '{}-{}'.format(str(self.dle_ident), self.dle_dev.dev_name)