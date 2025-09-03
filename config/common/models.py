#!/usr/bin/python
# -*- coding: utf8 -*-

from django.utils.translation import gettext_lazy as _, gettext
from core.models import CoreModel
from django.db import models


class SystemParam(CoreModel):
    spm_key = models.CharField(max_length=50, unique=True)
    spm_value = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.spm_key, self.spm_value)
