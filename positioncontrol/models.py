from django.db import models
from core.models import CoreModel
from globalconfig.models import Building
from media.models import Media
from django.utils.translation import gettext, gettext_lazy as _
from django.conf import settings
import os


# Create your models here.

class PositionView(CoreModel):
    VIEW_ADV = 'VIEW_ADV'
    VIEW_LIGHTING = 'VIEW_LIGHTING'
    VIEW_ACC = 'VIEW_ACC'

    VIEW_CHOICES = (
        (VIEW_ADV, _('VIEW_ADV')),
        (VIEW_LIGHTING, _('VIEW_LIGHTING')),
        (VIEW_ACC, _('VIEW_ACC')),
    )

    OBJECT_FLOOR = 'FLOOR'

    OBJECT_CHOICES = (
        (OBJECT_FLOOR, _('OBJECT_FLOOR')),
    )

    pov_building = models.ForeignKey(Building, on_delete=models.CASCADE)
    pov_view_id = models.CharField(max_length=20, choices=VIEW_CHOICES)
    pov_data_object = models.CharField(max_length=20, choices=OBJECT_CHOICES)

    def __str__(self):
        return self.pov_building.bdg_name + ' - ' + self.pov_view_id

    class Meta:
        unique_together = (("pov_building", "pov_view_id"),)


class PositionItem(CoreModel):
    """
        item: {
            "id": 1,
            "top": 10,
            "left": 30
        }
    """
    poi_items = models.TextField(default='[]')
    poi_pos_view = models.ForeignKey(PositionView, on_delete=models.CASCADE, related_name='position_items')
    poi_media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='position_items', null=True, blank=True)
    poi_data_id = models.PositiveIntegerField()

    def __str__(self):
        return str(self.poi_pos_view_id) + ' - ' + str(self.poi_data_id)

    def get_abs_media_url(self, request):
        if self.poi_media:
            return self.poi_media.get_abs_url(request)
        else:
            return None
