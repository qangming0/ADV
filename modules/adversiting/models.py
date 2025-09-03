from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.db.models.signals import post_save
from core.models import CoreModel, CoreModelManager
from media.models import Media
from device.models import Device

TYPE_RELAX = 0
TYPE_ADV = 1
TYPE_ONEMET = 2
TYPE_CHOICES = (
    (TYPE_RELAX, _('Relex')),
    (TYPE_ADV, _('Advertise')),
)

class AdvSchedule(CoreModel):
    advs_name = models.CharField(max_length=50)
    advs_type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_RELAX)
    advs_datetart = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    advs_dateend = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    advs_devices = models.ManyToManyField(Device, related_name='advschedule')

    def __str__(self):
        return '{}-{}'.format(self.id, str(self.advs_name))

    @property
    def advs_type_name(self):
        return self.get_advs_type_display()


class AdvPlan(CoreModel):
    advp_schedule = models.ForeignKey(AdvSchedule, on_delete=models.CASCADE, related_name='advplan')
    advp_name = models.CharField(max_length=50)
    advp_durations = models.SmallIntegerField(default=0)
    advp_interval = models.SmallIntegerField(default=1)
    advp_timestart = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    advp_timeend = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)

    def __str__(self):
        return '{}-{}'.format(self.id, str(self.advp_name))


class AdvContent(CoreModel):
    advc_media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='advcontent')
    advc_plan = models.ForeignKey(AdvPlan, on_delete=models.CASCADE, blank=True, null=True, related_name='advcontent')
    advc_schedule = models.ForeignKey(AdvSchedule, on_delete=models.CASCADE, blank=True, null=True, related_name='advcontent')
    advc_descript = models.CharField(max_length=50, blank=True, null=True)
    advc_durations = models.IntegerField(default=0)


class AdvDataSynch(CoreModel):
    advd_device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, related_name='advsync')
    advd_type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_RELAX)
    advd_value = models.TextField(null=True, blank=True)
    advd_error = models.BooleanField(default=False)
    advd_synchronized = models.BooleanField(default=False)
    advd_description = models.CharField(max_length=100, blank=True, null=True)
    advd_request_remove = models.BooleanField(default=False)
    advd_durations = models.CharField(max_length=100, default='[]')

    class Meta:
        unique_together = (("advd_device", "advd_type"),)


class OneNetContent(CoreModel):
    PRIORITY_FLEXIBLE = 1
    PRIORITY_RIGID = 2
    PRIORITY_CHOICES = (
        (PRIORITY_FLEXIBLE, _('Flexible')),
        (PRIORITY_RIGID, _('Rigit')),
    )

    DEFAULT_DURATION = 5
    DEFAULT_INTERVAL = 1
    DEFAULT_TIMEOUT = 10
    DEFAULT_DELAY = 5

    onc_device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, related_name='onenetcontent')
    onc_priority = models.SmallIntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_FLEXIBLE)
    onc_content_id = models.CharField(max_length=100, blank=True)
    onc_content = models.TextField(null=True, blank=True)
    onc_duration = models.SmallIntegerField(default=DEFAULT_DURATION)
    onc_timestart = models.DateTimeField(auto_now_add=False)
    onc_interval = models.SmallIntegerField(default=DEFAULT_INTERVAL)
    onc_timeout = models.SmallIntegerField(default=DEFAULT_TIMEOUT)
    onc_delay = models.SmallIntegerField(default=DEFAULT_DELAY)
    onc_sent = models.BooleanField(default=False)





