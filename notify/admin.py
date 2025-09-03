#!/usr/bin/python
# -*- coding: utf8 -*-


from django.contrib import admin
from .models import Notify, UserNotify, ChannelGroup

admin.site.register(Notify)
admin.site.register(UserNotify)
admin.site.register(ChannelGroup)
