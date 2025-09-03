#!/usr/bin/python
# -*- coding: utf8 -*-


import os
from django.utils.translation import gettext_lazy as _

class Topic(object):
    P_MODBUS = 'P_MODBUS'
    C_MODBUS = 'C_MODBUS'

    P_APP = 'P_APP'
    C_APP = 'C_APP'

    P_DEV = 'P_DEV'
    C_DEV = 'C_DEV'

    P_MQTT = 'P_MQTT'
    C_MQTT = 'C_MQTT'

    P_COMMON = 'P_COMMON'

    P_APP_SEND_GW = 'APPS'
    C_APP_RECEIVE_GW = 'APPID00000001{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    C_APP_RECEIVE_SYNC_GW = 'APP_SYNC{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )

    P_DEVICE_SEND_GW = 'DEVICES'


    ALL_SECLECTION = [
        (P_MODBUS,  _('Producer Modbus')),
        (C_MODBUS,  _('Consumer Modbus')),

        (P_APP,     _('Producer Application')),
        (C_APP,  _('Consumer Application')),

        (P_DEV,  _('Producer Device')),
        (C_DEV,  _('Consumer Device')),

        (P_MQTT,  _('Producer Message Queuing Telemetry Transport')),
        (C_MQTT,  _('Consumer Message Queuing Telemetry Transport')),

        (P_COMMON,  _('Producer Common')),
    ],

    REALTIME_LIGHTING = 'APP_REALTIME_LIGHTING{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    REALTIME_LIFT = 'APP_REALTIME_LIFT{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    REALTIME_PARKING = 'APP_REALTIME_PARKING{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    REALTIME_ACCESSCONTROL = 'APP_REALTIME_ACCESSCONTROL{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    REALTIME_FIREESCAPE = 'APP_REALTIME_FIREESCAPE{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    REALTIME_ADVERTIS = 'APP_REALTIME_ADVERTIS{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    KEEPALIVE = 'KEEPALIVE{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )

    DEVICE_RECEIVE = 'DEVICES{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )

    # for onemes
    ONEMES_REQUEST = 'onenet/request{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )
    ONEMES_LISTEN = 'onenet/listen{}'.format(os.getenv('TOPIC_SUFFIXES', ''), )


