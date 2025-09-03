#!/usr/bin/python
# -*- coding: utf8 -*-

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse

from core.views import BaseViewMixin, BaseView, MessageResponse
from config.provider.models import Provider
from config.provider.serializers import ProviderSerializer, ProviderDetailSerializer
from config.provider.form import ProviderFilter


class ProviderList(BaseViewMixin, *BaseView('create', 'list')):
    queryset = Provider.objects.all().order_by('-id', "-created")
    serializer_class = ProviderSerializer
    filterset_class = ProviderFilter
    # search_fields = ('dev_name',)
    ordering_fields = ('id', 'created', 'pvd_name',)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProviderDetail(BaseViewMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Provider.objects.all()
    serializer_class = ProviderDetailSerializer
    filterset_class = ProviderFilter

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)