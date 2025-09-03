from core.serializers import CoreModelSerializer
from rest_framework import serializers
from .models import Building, Floor, Zone, Door


class BuildingListSerializer(CoreModelSerializer):
    full_name = serializers.ReadOnlyField()
    bdg_rest_day_list = serializers.ReadOnlyField()
    bdg_holiday_list = serializers.ReadOnlyField()

    class Meta:
        model = Building
        fields = '__all__'

    def create(self, validated_data):
        if validated_data.get('bdg_rest_day') or validated_data.get('bdg_holiay'):
            validated_data['bdg_synchronized'] = False
        return super(BuildingListSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('bdg_rest_day') != instance.original_fiels['bdg_rest_day'] or \
                validated_data.get('bdg_holiday') != instance.original_fiels['bdg_holiday']:
            validated_data['bdg_synchronized'] = False
        return super(BuildingListSerializer, self).update(instance, validated_data)


class FloorListSerializer(CoreModelSerializer):
    flr_state_name = serializers.ReadOnlyField(source='get_flr_state_display')
    flr_building_name = serializers.ReadOnlyField()

    class Meta:
        model = Floor
        fields = '__all__'


class ZoneListSerializer(CoreModelSerializer):
    flr_zone_name = serializers.ReadOnlyField(source='get_flr_zone_name')
    zone_building_name = serializers.ReadOnlyField(source='get_building_name')
    zone_building = serializers.ReadOnlyField()
    lighting_zone_id = serializers.ReadOnlyField()

    class Meta:
        model = Zone
        fields = '__all__'


class DoorListSerializer(CoreModelSerializer):
    floor_name = serializers.ReadOnlyField(source='get_floor_name')
    zone_name = serializers.ReadOnlyField(source='get_zone_name')
    building_name = serializers.ReadOnlyField(source='get_building_name')
    device_name = serializers.SerializerMethodField()
    control_state = serializers.SerializerMethodField()
    control_mode = serializers.SerializerMethodField()
    control_sync = serializers.SerializerMethodField()

    class Meta:
        model = Door
        fields = '__all__'

    def get_device_name(self, obj):
        devices = None
        if not devices or len(devices) == 0:
            return ''
        else:
            res = list()
            for dev in devices:
                if dev['dev_name'] not in res:
                    res.append(dev['dev_name'])
            return ', '.join(res)

    def get_control_state(self, obj):
        ins = getattr(obj, 'accdoorscheduledatasynch', None)
        if ins:
            return ins.adsd_state
        else:
            return 1

    def get_control_mode(self, obj):
        ins = getattr(obj, 'accdoorscheduledatasynch', None)
        if ins:
            return ins.adsd_mode
        else:
            return 1

    def get_control_sync(self, obj):
        ins = getattr(obj, 'accdoorscheduledatasynch', None)
        if ins:
            return ins.adsd_synchronized
        else:
            return None


class DoorDetailSerializer(CoreModelSerializer):
    class Meta:
        model = Door
        fields = '__all__'


class BuildingSelectionSerializer(CoreModelSerializer):
    name = serializers.ReadOnlyField(source='bdg_name')
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Building
        fields = ('id', 'name', 'full_name')


class FloorSelectionSerializer(CoreModelSerializer):
    name = serializers.ReadOnlyField(source='flr_name')
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Floor
        fields = ('id', 'name', 'full_name')


class ZoneSelectionSerializer(CoreModelSerializer):
    name = serializers.ReadOnlyField(source='zone_name')
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Zone
        fields = ('id', 'name', 'full_name')


class DoorSelectionSerializer(CoreModelSerializer):
    name = serializers.ReadOnlyField(source='door_name')
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Door
        fields = ('id', 'name', 'full_name')


class ZoneLightingStateSerializer(CoreModelSerializer):
    class Meta:
        model = Zone
        fields = ['lighting_state']


class FloorLightingStateSerializer(CoreModelSerializer):
    zones = ZoneLightingStateSerializer(many=True, required=False)

    class Meta:
        model = Floor
        fields = '__all__'
