#!/usr/bin/python
# -*- coding: utf8 -*-
from django.db.models import Q

from core.filterset import CoreFilterSet, NumberInFilter, IdInFilter
from django_filters import rest_framework as filters
from globalconfig.models import Door, Zone, Floor, Building


class DoorSelectFilter(CoreFilterSet):
    zone_in = filters.ModelMultipleChoiceFilter(field_name='door_zone',
                                                lookup_expr='in',
                                                queryset=Zone.objects.all())
    floor_in = filters.ModelMultipleChoiceFilter(field_name='door_zone__zone_floor',
                                                 lookup_expr='in',
                                                 queryset=Floor.objects.all())
    building_in = filters.ModelMultipleChoiceFilter(field_name='door_zone__zone_floor__flr_building',
                                                    lookup_expr='in',
                                                    queryset=Building.objects.all())

    class Meta:
        model = Door
        fields = {
            'id': ['exact'],
            'door_zone': ['exact'],
            'door_name': ['icontains'],
        }


class DoorListFilter(CoreFilterSet):
    # { id__in : '1,2,3'}
    id__in = NumberInFilter(field_name='id', lookup_expr='in')
    id__notin = NumberInFilter(field_name='id', method='field_notin_filter')
    zone_in = filters.ModelMultipleChoiceFilter(field_name='door_zone',
                                                lookup_expr='in',
                                                queryset=Zone.objects.all())
    floor_in = filters.ModelMultipleChoiceFilter(field_name='door_zone__zone_floor',
                                                 lookup_expr='in',
                                                 queryset=Floor.objects.all())
    building_in = filters.ModelMultipleChoiceFilter(field_name='door_zone__zone_floor__flr_building',
                                                    lookup_expr='in',
                                                    queryset=Building.objects.all())

    class Meta:
        model = Door
        fields = {
            'id': ['exact'],
            'door_name': ['exact', 'icontains'],
            'door_description': ['exact', 'icontains'],
            'door_position': ['exact'],
            'door_zone': ['exact'],
        }

    def field_notin_filter(self, queryset, name, value):
        return queryset.exclude(id__in=value)


class ZoneExtendFilter(CoreFilterSet):
    id__in = IdInFilter(field_name='id', queryset=Zone.objects.all())
    zone_building = filters.NumberFilter(field_name='zone_floor__flr_building', lookup_expr='exact')

    # def filter_id__in(self, queryset, name, value):
    #     id_list = [item.id for item in value]
    #     return queryset.filter(id__in=id_list)

    class Meta:
        model = Zone
        fields = {
            'zone_code': ['exact', 'icontains'],
            'zone_name': ['exact', 'icontains'],
            'zone_position': ['exact'],
            'zone_floor': ['exact'],
        }


class ZoneListFilter(CoreFilterSet):

    no_devline = filters.BooleanFilter(method='filter_devline')

    def filter_devline(self, queryset, name, value):
        if value:
            return queryset.filter(lightingzone__lightingdevline__isnull=True)
        return queryset

    class Meta:
        model = Zone
        fields = {
            'zone_code': ['exact', 'icontains'],
            'zone_name': ['exact', 'icontains'],
            'zone_position': ['exact'],
            'zone_floor': ['exact'],
        }



class FloorListFilter(CoreFilterSet):

    dev_id = filters.NumberFilter(method='filter_devline')

    need_config_lighting = filters.BooleanFilter(method='filter_for_lighting')

    def filter_devline(self, queryset, name, value):
        return queryset

    def filter_for_lighting(self, qs, name, value):
        if value:
            no_devline_zones = Zone.objects.filter(lightingzone__lightingdevline__isnull=True).values_list('zone_floor_id', flat=True).distinct()
            return qs.filter(id__in=list(no_devline_zones))
        else:
            return qs

    class Meta:
        model = Floor
        fields = {
        'flr_code': ['exact', 'icontains'],
        'flr_name': ['exact', 'icontains'],
        'flr_state': ['exact'],
        'flr_position': ['exact'],
        'flr_building': ['exact'],
    }
