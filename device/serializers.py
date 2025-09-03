#!/usr/bin/python
# -*- coding: utf-8 -*-


from rest_framework import serializers
from core.serializers import CoreModelSerializer
from device.models import Device, DeviceLine


class DeviceSerializer(CoreModelSerializer):
    dev_system_name = serializers.CharField(source='get_dev_system_display', read_only=True)
    dev_attr_name = serializers.CharField(source='get_dev_attr_display', read_only=True)
    dev_type_name = serializers.CharField(source='get_dev_type_display', read_only=True)
    dev_state_name = serializers.CharField(source='get_dev_state_display', read_only=True)
    dev_zone_name = serializers.ReadOnlyField()
    dev_floor_name = serializers.ReadOnlyField()
    dev_floor = serializers.ReadOnlyField()
    dev_building_name = serializers.ReadOnlyField()

    # for adv
    dev_diskspace = serializers.ReadOnlyField()
    dev_mediaplay_name = serializers.ReadOnlyField(source='dev_mediaplay.med_name')

    class Meta:
        model = Device
        fields = '__all__'
        extra_kwargs = {
            'dev_access_token': {'write_only': True}
        }
        # exclude = ('dev_access_token',)

    def create(self, validated_data):
        lift = validated_data.pop('lift', None)
        device = super(DeviceSerializer, self).create(validated_data)
        if lift:
            lift.device = device
            lift.save()
        return device


class DeviceDetailSerializer(CoreModelSerializer):

    class Meta:
        model = Device
        fields = '__all__'
        # exclude = ('dev_access_token',)
    def update(self, instance, validated_data):
        lift = validated_data.pop('lift', None)
        device = super(DeviceDetailSerializer, self).update(instance, validated_data)
        if lift:
            if hasattr(instance, 'lift'):
                old_lift = instance.lift
                old_lift.device = None
                old_lift.save()
            lift.device = device
            lift.save()
        return device


class DeviceLineListSerializer(CoreModelSerializer):
    dle_dev_name = serializers.CharField(source='dle_dev.dev_name', read_only=True)
    dle_door_name = serializers.CharField(source='dle_door.door_name', read_only=True)

    class Meta:
        model = DeviceLine
        fields = '__all__'


class DeviceLineDetailSerializer(CoreModelSerializer):
    class Meta:
        model = DeviceLine
        fields = '__all__'
