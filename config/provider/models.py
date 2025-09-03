#!/usr/bin/python
# -*- coding: utf8 -*-

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext
from core.models import CoreModel


class Provider(CoreModel):
    pvd_name = models.CharField(max_length=30, unique=True)
    pvd_key = models.IntegerField(unique=True)

    def __str__(self):
        return self.pvd_name

    class Meta:
        db_table = 'provider'