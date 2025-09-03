#!/usr/bin/python
# -*- coding: utf8 -*-


from django.contrib import admin
from .models import User, Permission, UserPermission, Group

admin.site.register((User, Permission, UserPermission))
