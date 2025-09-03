from django.db import models
from core.models import CoreModel
from django.utils.translation import gettext, gettext_lazy as _
import json
# from modules.lighting.models import LightingZone


# Register your models here.

class Building(CoreModel):
    bdg_name = models.CharField(max_length=50)
    bdg_address = models.CharField(max_length=100)
    bdg_description = models.CharField(max_length=100)
    # example rest day and holiday format: '2018-12-28,2018-01-01'
    bdg_rest_day = models.TextField(null=True, blank=True)
    bdg_holiday = models.TextField(null=True, blank=True)
    bdg_synchronized = models.BooleanField(default=True)

    def __str__(self):
        return self.bdg_name

    @property
    def full_name(self):
        fullname = '{}'.format(self.bdg_name, )
        if self.bdg_address is not None:
            fullname += ' / {}'.format(self.bdg_address, )
        if self.bdg_description is not None:
            fullname += ' / {}'.format(self.bdg_description, )
        return fullname

    @property
    def bdg_rest_day_list(self):
        if self.bdg_rest_day:
            try:
                return json.loads(self.bdg_rest_day)
            except:
                return []
        return []

    @property
    def bdg_holiday_list(self):
        if self.bdg_holiday:
            try:
                return json.loads(self.bdg_holiday)
            except:
                return []
        return []



class Floor(CoreModel):
    ACTIVE = 1
    INACTIVE = 0
    STATE_CHOICE = (
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive')),
    )

    flr_code = models.CharField(max_length=50)
    flr_name = models.CharField(max_length=50)
    flr_state = models.PositiveSmallIntegerField(choices=STATE_CHOICE, default=ACTIVE)
    flr_position = models.SmallIntegerField(default=1)
    flr_building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')

    flr_is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = (("flr_building", "flr_position"),)

    def __str__(self):
        return self.flr_name

    @property
    def flr_building_name(self):
        if self.flr_building:
            return self.flr_building.bdg_name
        return ''

    @property
    def full_name(self):
        fullname = '{}'.format(self.flr_name, )
        if self.flr_building_name is not None:
            fullname += ' / {}'.format(self.flr_building_name, )
        return fullname


class Zone(CoreModel):
    zone_code = models.CharField(max_length=50)
    zone_name = models.CharField(max_length=50)
    zone_position = models.SmallIntegerField(null=True, blank=True)
    zone_floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='zones')

    class Meta:
        ordering = ['zone_floor__flr_building', 'zone_floor']

    def __str__(self):
        return self.zone_name

    @property
    def get_flr_zone_name(self):
        if self.zone_floor:
            return self.zone_floor.flr_name
        return ''

    @property
    def get_building_name(self):
        if self.zone_floor and self.zone_floor.flr_building:
            return self.zone_floor.flr_building.bdg_name
        return ''

    @property
    def full_name(self):
        fullname = '{}'.format(self.zone_name, )
        if self.get_flr_zone_name is not None:
            fullname += ' / {}'.format(self.get_flr_zone_name, )
        return fullname

    @property
    def zone_building(self):
        return self.zone_floor.flr_building.id

    @property
    def lighting_state(self):
        if self.lightingzone:
            return self.lightingzone.lsz_state
        return 0

    @property
    def lighting_zone_id(self):
        if self.lightingzone:
            return self.lightingzone.id
        return 0


# Create your models here.

class Door(CoreModel):
    STATE_CLOSED = 1
    STATE_OPENED = 0

    STATE_CHOICES = (
        (STATE_CLOSED, _('Closed')),  # Dong
        (STATE_OPENED, _('Opened')),  # Mo
    )

    door_name = models.CharField(max_length=50)
    door_description = models.CharField(max_length=100, null=True, blank=True)
    door_position = models.SmallIntegerField(null=True, blank=True)
    door_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True)
    door_state = models.SmallIntegerField(choices=STATE_CHOICES, default=STATE_CLOSED)

    def __str__(self):
        return self.door_name

    @property
    def get_zone_name(self):
        if self.door_zone:
            return self.door_zone.zone_name
        return ''

    @property
    def get_floor_name(self):
        if self.door_zone and self.door_zone.zone_floor:
            return self.door_zone.zone_floor.flr_name
        return ''

    @property
    def get_building_name(self):
        if self.door_zone and self.door_zone.zone_floor and self.door_zone.zone_floor.flr_building:
            return self.door_zone.zone_floor.flr_building.bdg_name
        return ''

    @property
    def full_name(self):
        fullname = '{}'.format(self.door_name, )
        if self.get_zone_name is not None:
            fullname += ' / {}'.format(self.get_zone_name, )
        return fullname
