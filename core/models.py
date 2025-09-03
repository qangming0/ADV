#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from django.db import models
import hashlib
import requests

from django.conf import settings
from django.core.signing import TimestampSigner
from django.contrib.auth import get_user_model
from django.db.models import ManyToManyField, ForeignKey, OneToOneField
from django.contrib.auth.models import User
# from middleware import current_user


class CoreModel(models.Model):
    '''
        tat ca các model đều phải inherit từ đây
    '''

    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    create_uid = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="create_%(app_label)s_%(class)s_related")
    update_uid = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="update_%(app_label)s_%(class)s_related")

    def __init__(self, *args, **kwargs):
        # super(getattr(sys.modules[__name__], self._meta.object_name), self).__init__(*args, **kwargs)
        super(CoreModel, self).__init__(*args, **kwargs)
        self.original_fiels = (self.__dict__).copy()
        # try:
        #     fields = self._meta.get_fields()
        #     for field in fields:
        #         if isinstance(field, ManyToManyField):
        #             self.original_fiels[field.name] = list(getattr(self, field.name).values_list("id", flat=True))
        #         elif isinstance(field, OneToOneField):
        #             self.original_fiels[field.name] = getattr(self, field.name).id
        #         elif isinstance(field, ForeignKey):
        #             self.original_fiels[field.name] = getattr(self, field.name).id
        # except Exception as ex:
        #     print(str(ex))

    class Meta:
        abstract = True

    # def save_model(self, request, obj, form, change):
    #     if not obj.pk:
    #         obj.create_uid = request.user
    #     obj.update_uid = request.user
    #     super().save_model(request, obj, form, change)
    def save(self, *args, **kwargs):
        # user = get_user()
        super(CoreModel, self).save(*args, **kwargs)


class CoreModelManager(models.Manager):
    pass


class CoreModelQuerySet(models.query.QuerySet):
    pass
