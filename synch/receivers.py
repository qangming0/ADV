#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from device.models import Device
from config.system.models import System
from core.mqbroker.mqtt.mqttcontroller import MQTTController
from core.mqbroker.event import *
from core.mqbroker.topic import Topic


@receiver(post_save, sender=Device)
def onenet_save_device_handle(sender, instance, created, **kwargs):
    if not created and instance.dev_system == System.TYPE_ADVERTIS:
        if instance.dev_name != instance.original_fiels['dev_name'] \
            or instance.dev_zone_id != instance.original_fiels['dev_zone_id'] \
            or instance.dev_state != instance.original_fiels['dev_state']:
                devs = Device.objects.getAdvertis()
                dataDevInfo = []
                if devs and devs.count() > 0:
                    for dev in devs:
                        dataDevInfo.append({
                            "id": dev.id,
                            "name": dev.dev_name,
                            "pos": dev.dev_position_full
                        })
                    # send data to onenet
                    mqttCtrl = MQTTController()
                    mqttCtrl.producer.rawSend(
                        topic=Topic.ONEMES_LISTEN,
                        value={
                            "type": "ONENET",
                            "event": EVT_ONENET_REQUEST_GET_LIST_DEVICE,
                            "data": dataDevInfo
                        }
                    )