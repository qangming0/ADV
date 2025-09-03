#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.contrib import admin
from .models import Device, DeviceLine

admin.site.register(Device)
admin.site.register(DeviceLine)
