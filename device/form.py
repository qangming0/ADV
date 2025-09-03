#!/usr/bin/python
# -*- coding: utf-8 -*-


from core.filterset import CoreFilterSet, NumberInFilter, IdInFilter
from device.models import Device


class DeviceFilter(CoreFilterSet):
    dev_system__in = NumberInFilter(field_name='dev_system', lookup_expr='in')
    id__in = NumberInFilter(field_name='id', lookup_expr='in')
    id__notin = NumberInFilter(field_name='id', method='field_notin_filter')
    online = NumberInFilter(field_name='dev_online', method='check_online')

    class Meta:
        model = Device
        fields = {
            'dev_name': ['exact', 'icontains'],
            'dev_ip': ['exact', 'icontains'],
            'dev_mac': ['exact', 'icontains'],
            'dev_info': ['exact', 'icontains'],
            'dev_ident': ['exact', 'icontains'],
            'dev_sync_state': ['exact'],
            'dev_state': ['exact'],
            'dev_system': ['exact'],
            'dev_attr': ['exact'],
        }
        # exclude = ['dev_access_token']

    def field_notin_filter(self, queryset, name, value):
        return queryset.exclude(id__in=value)

    def check_online(self, queryset, name, value):
        if len(value) > 0:
            if value[0] == 1:
                return queryset.filter(dev_online=True)
            elif value[0] == 2:
                return queryset.filter(dev_online=False)
            else:
                return queryset
        else:
            return queryset