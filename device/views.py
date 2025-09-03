#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
import os
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse

from core.views import BaseViewMixin, BaseView, MessageResponse, DefaultsMixin
from config.system.models import System
from core.mqbroker.topic import Topic
from device.models import Device, DeviceLine
from device.serializers import DeviceSerializer, DeviceDetailSerializer
from device.serializers import DeviceLineListSerializer, DeviceLineDetailSerializer
from device.form import DeviceFilter
from core.permissions import IsStaffOrAdmin
from media.models import Media
from media.serializers import MediaSerializer
from modules.adversiting.models import AdvContent
from rest_framework.response import Response
from core.dataglobal import GlobalDeviceStatus



class DeviceList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = Device.objects.all().order_by('-id', "-created")
    serializer_class = DeviceSerializer
    filterset_class = DeviceFilter
    # search_fields = ('dev_name',)
    ordering_fields = ('id', 'created', 'dev_name',)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DeviceDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Device.objects.all()
    serializer_class = DeviceDetailSerializer
    filterset_class = DeviceFilter

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class DeviceExt(APIView):
    @api_view(['GET'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin))
    def list(request):
        systems = [{'id': x[0], 'value': x[1]} for x in System.TYPE_CHOICES]
        attributes = [{'id': x[0], 'value': x[1]} for x in System.ATTR_CHOICES]
        types = [{'id': x[0], 'value': x[1]} for x in Device.TYPE_CHOICES]
        states = [{'id': x[0], 'value': x[1]} for x in Device.STATE_CHOICES]
        response = {
            'systems': systems,
            'attributes': attributes,
            'types': types,
            'states': states,
        }
        return JsonResponse(response, safe=False)

class DeviceBaseFilter(DefaultsMixin, *BaseView('list')):
    serializer_class = DeviceSerializer

    filterset_fields = {
        'dev_name': ['exact', 'icontains'],
        'dev_ip': ['exact', 'icontains'],
        'dev_mac': ['exact', 'icontains'],
        'dev_type': ['exact'],
        'dev_state': ['exact'],
        'dev_attr': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class UnknownDeviceList(DeviceBaseFilter):
    queryset = Device.objects.getUnKnown()

class AccessControlDeviceList(DeviceBaseFilter):
    queryset = Device.objects.getAccessController()

class LiftDeviceList(DeviceBaseFilter):
    queryset = Device.objects.getLift()

class ParkingDeviceList(DeviceBaseFilter):
    queryset = Device.objects.getParking()

class LightingDeviceList(DeviceBaseFilter):
    queryset = Device.objects.getLighting()

class AdvertisDeviceList(DeviceBaseFilter):
    queryset = Device.objects.getAdvertis()

class EscapeDeviceList(DeviceBaseFilter):
    queryset = Device.objects.getFireEscape()

class SynchrozingDevice(DeviceBaseFilter):
    # Disable pagination
    paginate_by = None
    paginate_by_param = None
    max_paginate_by = None
    queryset = Device.objects.filter(dev_online=True, dev_sync_state=Device.SYNC_STATE_WAITING)


class DeviceManagement(APIView):
    @api_view(['POST'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin, ))
    def register(request):
        res = MessageResponse()

        try:
            accessToken = request.data.get("accesstoken", None)
            ipAddress = request.data.get("ipaddr", request.META.get('REMOTE_ADDR'))
            macAddress = request.data.get("macaddr", None)
            info = request.data.get("info", None)
            parentDevId = request.data.get("parentid", None)
            isDevice = request.data.get("isdevice", False)
            version = request.data.get("version", None)

            httpcookie = request.META.get("HTTP_COOKIE", 'csrftoken=; sessionid=').split('; ')

            if macAddress is not None:
                devs = Device.objects.filter(Q(dev_access_token=accessToken) | Q(dev_mac=macAddress.upper()))
            else:
                devs = Device.objects.filter(Q(dev_access_token=accessToken))

            if devs.count() >= 1:
                updated = False
                dev = devs[0]
                if macAddress:
                    dev.dev_ip = ipAddress
                    updated = True
                if ipAddress:
                    dev.dev_mac = macAddress
                    updated = True
                if info:
                    dev.dev_info = info
                    updated = True
                if version:
                    dev.dev_software_version = version
                    updated = True
                if updated:
                    dev.save()
                res.setAttr('accesstoken', dev.dev_access_token)

            else:
                sessionid = httpcookie[1].replace('sessionid=', '')
                dev = Device()
                dev.dev_sessionid = sessionid if sessionid is not None and len(sessionid) > 0 else None
                dev.dev_access_token = uuid.uuid4().hex
                dev.dev_ip = ipAddress
                dev.dev_mac = macAddress.upper()
                dev.dev_info = info

                DIs = Device.objects.filter(dev_ident=parentDevId)\
                    .exclude(dev_ident__isnull=True).exclude(dev_ident__exact='')
                dev.dev_parent = DIs[0] if DIs.count() > 0 else None

                if not isDevice and not dev.dev_parent:
                    dev.dev_name = 'NEW DI %06s' % (dev.dev_access_token[-6:])
                else:
                    dev.dev_name = 'NEW DEV %06s' % (dev.dev_access_token[-6:])

                dev.save()

                res.setAttr('accesstoken', dev.dev_access_token)
                res.setAttr('success', True)
                res.setAttr('message', _("%s registing successfull" % (dev.dev_name,)))

        except Exception as ex:
            print(str(ex))
            res.setAttr('success', False)
            res.setAttr('message', _("Device registration failed: %s" % (str(ex),)))

        finally:
            return JsonResponse(res.getAttr(), safe=False)

    @api_view(['POST'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin, ))
    def getId(request):
        accessToken = request.data.get("accesstoken", "")

        res = MessageResponse()
        devs = Device.objects.filter(dev_access_token=accessToken)
        if devs.count() == 1:
            res.setAttr('devid', devs[0].dev_ident)
            res.setAttr('accesstoken', devs[0].dev_access_token)
        else:
            res.setAttr('success', False)
            res.setAttr('message', _("Device is existed"))
        return JsonResponse(res.getAttr(), safe=False)

    @api_view(['POST'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin, ))
    def active(request, pk):
        res = MessageResponse()
        try:
            dev = Device.objects.get(pk=pk)
            if not dev.dev_ident and dev.dev_state != Device.STATE_ACTIVE:
                if dev.dev_system is not None and dev.dev_provider:
                    devid = "{0:04b}".format(dev.dev_system) + "{0:04b}".format(
                        dev.dev_provider.pvd_key) + "{0:08b}".format(pk) + "{}".format((uuid.uuid4().hex)[:4])
                    dev.dev_ident = devid
                    dev.dev_state = Device.STATE_ACTIVE
                    dev.save()

                    # update device to list check online
                    lstDevStatus = {}
                    lstDevStatus[dev.dev_ident] = {
                        "id": dev.id,
                        "ip": dev.dev_ip,
                        "mac": dev.dev_mac,
                        "system": dev.dev_system,
                        "status": False,
                    }
                    gds = GlobalDeviceStatus()
                    gds.update(lstDevStatus)

                    res.setAttr('data', {
                        'devid': dev.dev_ident,
                        'accesstoken': dev.dev_access_token,
                    })
                    res.setAttr('message', _("Device is actived successfull"))
                else:
                    res.setAttr('success', False)
                    res.setAttr('message', _("Your must fill enough device's infos: %s"))
            else:
                res.setAttr('data', {
                    'devid': dev.dev_ident,
                    'accesstoken': dev.dev_access_token,
                })
                dev.dev_state = not dev.dev_state
                dev.save()
                res.setAttr('message', _("Device is changed state successfull"))

        except Exception as ex:
            print(str(ex))
            res.setAttr('success', False)
            res.setAttr('message', _("Device activation failed: %s" % (str(ex),)))

        finally:
            return JsonResponse(res.getAttr(), safe=False)

    @api_view(['POST'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin))
    def getInfo(request):
        accessToken = request.data.get("accesstoken", None)
        devid = request.data.get("devid", None)
        option = request.data.get("option", None)

        res = MessageResponse()
        try:
            if devid and accessToken:
                arrOption = option.split('|')
                if not isinstance(arrOption, list) or not option or option == '':
                    res.setAttr('success', False)
                    res.setAttr('message', _("Your are not get any option"))
                else:
                    devs = Device.objects.filter(dev_access_token=accessToken, dev_ident=devid)
                    if devs.count() == 1:
                        dev = devs[0]
                        res.setAttr('devid', dev.dev_ident)
                        res.setAttr('accesstoken', dev.dev_access_token)

                        data = {
                            'info': {},
                            # 'protocol' : {},
                            # 'kafka' : {},
                            # 'icp' : {},
                            # 'childs' : {},
                            # 'db' : {},
                            # 'apps' : {},
                            # 'socket' : {}
                        }

                        if 'PROTOCOL' in arrOption:
                            data['protocol'] = {}

                        if 'KAFKA' in arrOption:
                            if dev.dev_type in [Device.TYPE_DEVICE, Device.TYPE_DI]:
                                data['kafka'] = [
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'APP_CONSUMER',
                                        'topic': '',
                                        'partition': 0,
                                        'timestamp_ms': 0,
                                        'providerKey': 'C_APP',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'APP_PRODUCER',
                                        'topic': 'APPS',
                                        'partition': 0,
                                        'timestamp_ms': 0,
                                        'providerKey': 'P_APP',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'DEV_PRODUCER',
                                        'topic': 'DEVICES',
                                        'partition': 0,
                                        'timestamp_ms': 0,
                                        'providerKey': 'P_DEV',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'DEV_CONSUMER',
                                        'topic': '',
                                        'partition': 0,
                                        'timestamp_ms': 0,
                                        'providerKey': 'C_DEV',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'Gateway_consumer_app',
                                        'topic': 'APPS',
                                        'partition': 0,
                                        'timestamp_ms': 100,
                                        'providerKey': 'C_APP',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'Gateway_consumer_device',
                                        'topic': 'DEVICES',
                                        'partition': 0,
                                        'timestamp_ms': 100,
                                        'providerKey': 'C_DEV',
                                    }
                                ]

                            elif dev.dev_type in [Device.TYPE_GATEWAY]:
                                data['kafka'] = [
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'Gateway_consumer_app',
                                        'topic': 'APPS',
                                        'partition': 0,
                                        'timestamp_ms': 100,
                                        'providerKey': 'C_APP',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'Gateway_consumer_device',
                                        'topic': 'DEVICES',
                                        'partition': 0,
                                        'timestamp_ms': 100,
                                        'providerKey': 'C_DEV',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'Gateway_consumer_mqtt',
                                        'topic': 'MQTT',
                                        'partition': 0,
                                        'timestamp_ms': 100,
                                        'providerKey': 'C_MQTT',
                                    },
                                    {
                                        'host': os.getenv('KAFKA_HOST', 'localhost'),
                                        'port': os.getenv('KAFKA_PORT', 9092),
                                        'providerName': 'Gateway_provider_common',
                                        'topic': '',
                                        'partition': 0,
                                        'timestamp_ms': 100,
                                        'providerKey': 'P_COMMON',
                                    },
                                ]

                            else:
                                data['kafka'] = []

                        if 'ICP' in arrOption:
                            data['devicelist'] = {}

                        if 'DEVICELIST' in arrOption:
                            data['devicelist'] = {}

                        if 'DB' in arrOption:
                            data['db'] = {}

                        if 'KEEPALIVE' in arrOption:
                            data['keepalive'] = Topic.KEEPALIVE

                        devType = dev.dev_type

                        if 'APPS' in arrOption:
                            if devType in [Device.TYPE_GATEWAY]:
                                data['apps'] = Topic.C_APP_RECEIVE_GW
                            else:
                                devSystem = dev.dev_system
                                if devSystem in [System.TYPE_PARKING]:
                                    data['apps'] = Topic.REALTIME_PARKING
                                elif devSystem in [System.TYPE_ADVERTIS]:
                                    data['apps'] = Topic.REALTIME_ADVERTIS
                                elif devSystem in [System.TYPE_ACCESS_CONTROLLER]:
                                    data['apps'] = Topic.REALTIME_ACCESSCONTROL
                                elif devSystem in [System.TYPE_LIFT]:
                                    data['apps'] = Topic.REALTIME_LIFT
                                elif devSystem in [System.TYPE_FIRE_ESCAPE]:
                                    data['apps'] = Topic.REALTIME_FIREESCAPE
                                elif devSystem in [System.TYPE_LIGHTING]:
                                    data['apps'] = Topic.REALTIME_LIGHTING
                                else:
                                    data['apps'] = Topic.C_APP_RECEIVE_GW

                        if 'MQTT' in arrOption:
                            data['mqtt'] = {
                                'host': os.getenv('MQTT_HOST', 'localhost'),
                                'port': os.getenv('MQTT_PORT', 1883),
                                'authen': {
                                    'mode': 0,  # 0 --> user/password, 1 --> ssl
                                    'user': os.getenv('MQTT_USER', ''),
                                    'password': os.getenv('MQTT_PASSWORD', ''),
                                    # encode HS256
                                    'secret_key': 'qkm3duu)^$%!l%nu8-%%cj&v#cmg8k_-ytn#=9+qz-%+&qtbe&'
                                },
                                'topic_realtime': Topic.REALTIME_ADVERTIS,
                                'topic_keepalive': Topic.KEEPALIVE,
                                'topic_request': Topic.C_APP_RECEIVE_GW,
                                'topic_listen': '{}/{}'.format(Topic.DEVICE_RECEIVE, dev.dev_ident),
                            }

                        res.setAttr('data', data)

                    else:
                        res.setAttr('success', False)
                        res.setAttr('message', _("Device not existed"))
            else:
                res.setAttr('success', False)
                res.setAttr('message', _("Device not existed"))

        except Exception as ex:
            print(str(ex))
            res.setAttr('success', False)
            res.setAttr('message', _("Get Device's Info failed: %s" % (str(ex),)))

        finally:
            return JsonResponse(res.getAttr(), safe=False)


class DeviceLineList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = DeviceLine.objects.all()
    serializer_class = DeviceLineListSerializer

    filterset_fields = {
        'dle_dev': ['exact'],
        'dle_door': ['exact'],
        'dle_ident': ['exact'],
        'dle_type': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DeviceLineDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = DeviceLine.objects.all()
    serializer_class = DeviceLineDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class DeviceAdvMedia(DefaultsMixin, *BaseView('show',)):
    queryset = Device.objects.filter(dev_system=System.TYPE_ADVERTIS)
    serializer_class = MediaSerializer

    def get(self, request, *args, **kwargs):
        device = self.get_object()
        schedules = device.advschedule.all().values_list('id', flat=True)
        media_id = AdvContent.objects.filter(advc_schedule__in=schedules).values_list('advc_media_id', flat=True)
        queryset = Media.objects.filter(id__in=media_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
