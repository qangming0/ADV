#!/usr/bin/python
# -*- coding: utf8 -*-

from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _, gettext
from core.serializers import CoreModelSerializer
from config.provider.models import Provider


class ProviderSerializer(CoreModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

    def validate_pvd_key(self, value):
        if self.instance and self.instance.pk:
            pass
        else:
            msg = _('Key must number.')
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        pvd_key = attrs.get('pvd_key')
        if not pvd_key or not isinstance(pvd_key, int):
            msg = _('Key must number.')
            raise serializers.ValidationError(msg)
        return attrs


class ProviderDetailSerializer(CoreModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'
