#!/usr/bin/python
# -*- coding: utf8 -*-


from core.filterset import CoreFilterSet
from config.provider.models import Provider


class ProviderFilter(CoreFilterSet):
    class Meta:
        model = Provider
        fields = {
            'pvd_name': ['exact', 'icontains'],
            'pvd_key': ['exact'],
        }

