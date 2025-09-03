#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.filterset import CoreFilterSet
from django_filters import rest_framework as filters
from .models import AdvSchedule, AdvPlan, AdvContent, OneNetContent

class AdvScheduleFilter(CoreFilterSet):
    class Meta:
        model = AdvSchedule
        fields = {
            'advs_name': ['exact', 'icontains'],
            'advs_type': ['exact'],
            'advs_datetart': ['exact'],
            'advs_dateend': ['exact']
        }


class AdvPlanFilter(CoreFilterSet):
    class Meta:
        model = AdvPlan
        fields = {}


class AdvContentFilter(CoreFilterSet):
    class Meta:
        model = AdvContent
        fields = {}


class OneNetContentFilter(CoreFilterSet):
    class Meta:
        model = OneNetContent
        fields = {}


