#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
from core.views import MessageResponse
from config.system.models import System
from core.permissions import IsStaffOrAdmin
from core.mqbroker.topic import Topic
import os


class SystemList(APIView):
    @api_view(['GET'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin,))
    def getList(request):
        res = MessageResponse()
        res.setAttr('data', [{'id': item[0], 'name': item[1]} for item in System.STATE_CHOICES])
        return JsonResponse(res.getAttr(), safe=False)


class SystemConfig(APIView):
    """
    Get System config for third party
    """

    @api_view(['GET'])
    @permission_classes((IsAuthenticated,))
    def AdvConfig(self):
        system_config = {
            "host": os.getenv('MQTT_HOST', 'localhost'),
            "port": os.getenv('MQTT_PORT', 1883),
            "authen": {
                "mode": os.getenv('MQTT_AUTHENTICATION_MODE', 0),
                "user": os.getenv('MQTT_USER', None),
                "password": os.getenv('MQTT_PASSWORD', None),
                "secret_key": os.getenv('MQTT_SECRET_KEY', None)
            },
            "topic_request": Topic.ONEMES_REQUEST,
            "topic_listen": Topic.ONEMES_LISTEN,
        }
        return JsonResponse(system_config, safe=False)


