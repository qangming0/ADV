from core.serializers import CoreModelSerializer
from .models import PositionView, PositionItem
from globalconfig.models import Building
from rest_framework import serializers
from globalconfig.models import Floor, Zone
from media.models import Media
from device.models import Device
from django.conf import settings
from config.system.models import System
import os


class PositionItemSerializer(CoreModelSerializer):
    media_src = serializers.SerializerMethodField()

    def get_media_src(self, obj):
        if obj.poi_media:
            # return obj.poi_media.get_abs_url(self.context['request'])
            return ""
        else:
            default_media = os.path.join(settings.MEDIA_URL, 'templates', 'default-background.png')
            return self.context['request'].build_absolute_uri(default_media)

    class Meta:
        model = PositionItem
        exclude = [
            'poi_pos_view'
        ]


class PositionViewSerializer(CoreModelSerializer):
    data = PositionItemSerializer(source='position_items', many=True, read_only=True)

    class Meta:
        model = PositionView
        fields = '__all__'


class AdvDeviceSerializer(CoreModelSerializer):
    state = serializers.SerializerMethodField(read_only=True)
    dev_zone_name = serializers.ReadOnlyField()

    dev_diskspace = serializers.ReadOnlyField()
    dev_mediaplay_name = serializers.ReadOnlyField(source='dev_mediaplay.med_name')

    def get_state(self, obj):
        if obj.dev_online:
            return 'ON'
        else:
            return 'OFF'

    class Meta:
        model = Device
        fields = '__all__'


class AdvFloorSerializer(CoreModelSerializer):
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        zone_ids = obj.zones.all().values_list('id', flat=True)
        devices = Device.objects.filter(dev_zone__in=zone_ids, dev_system=System.TYPE_ADVERTIS)
        serializer = AdvDeviceSerializer(devices, many=True)
        return serializer.data

    class Meta:
        model = Floor
        fields = ['id', 'flr_state', 'flr_name', 'items']


class AdvPostSerializer(serializers.Serializer):
    pov_view_id = serializers.ChoiceField(choices=PositionView.VIEW_CHOICES)
    pov_building = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all())
    poi_data_id = serializers.IntegerField(min_value=1)
    poi_media = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False, allow_null=True,
                                                   default=None)
    items = serializers.CharField()
