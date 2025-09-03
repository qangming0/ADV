#!/usr/bin/python
# -*- coding: utf8 -*-

from django.utils.translation import ugettext_lazy as _, gettext


class FMacro(object):
    PEOPLE_TYPE_VARIED = 0  # Vang lai
    PEOPLE_TYPE_PACKAGE = 1  # Thue bao
    PEOPLE_TYPE_SPECIAL = 2  # Dac biet

    PEOPLE_TYPE_CHOICES = (
        (PEOPLE_TYPE_VARIED, _('Varied')),
        (PEOPLE_TYPE_PACKAGE, _('Package')),
        (PEOPLE_TYPE_SPECIAL, _('Special')),
    )

    CARD_PEOPLE_TYPE_CHOICES = (
        (PEOPLE_TYPE_VARIED, _('Varied')),
        (PEOPLE_TYPE_PACKAGE, _('Package')),
    )

    LIFECYCLE_LEV_UNKNOWN = 0
    LIFECYCLE_LEV_WEEK = 1
    LIFECYCLE_LEV_MONTH = 2
    LIFECYCLE_LEV_QUATER = 3
    LIFECYCLE_LEV_YEAR = 4

    LIFECYCLE_CHOICES = (
        (LIFECYCLE_LEV_UNKNOWN, _('UnKnown')),
        (LIFECYCLE_LEV_WEEK, _('Week')),
        (LIFECYCLE_LEV_MONTH, _('Month')),
        (LIFECYCLE_LEV_QUATER, _('Quater')),
        (LIFECYCLE_LEV_YEAR, _('year')),
    )

    DATE_TYPE_NORMAL = 0
    DATE_TYPE_HOLIDAY = 1
    DATE_TYPE_RESTED = 2

    DATE_TYPE_CHOICES = (
        # (None, 'Your String For Display'),
        (DATE_TYPE_NORMAL, _('Normal')),
        (DATE_TYPE_HOLIDAY, _('Holiday')),
        (DATE_TYPE_RESTED, _('Rested')),
    )

