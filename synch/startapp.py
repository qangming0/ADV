import os
# from core.mqbroker.kafsynchronize import BaseKAFSysnchorized
from core.mqbroker.mqttsynchronize import BasMqttSysnchorized
from synch.modules.device import dev_keepalive
from synch.modules.adv import adv_realtimelog, adv_handle
from synch import sync_handle
from core.mqbroker.event import *
from core.mqbroker.topic import Topic
from core.mqbroker.fqueue.fqueuecontroller import FQueueController
from synch.modules.common.responsehandle import KafResponseHandle
from synch.modules.common.responsehandle import MqttResponseHandle
from core.db.mongo.mongocontroller import MongoController
# from core.mqbroker.kafka.kafcontroller import KAFController
from core.mqbroker.mqtt.mqttcontroller import MQTTController


def startApp():
    # Start Queue Handle
    # fqueue = fqueuecontroller()
    # fqueue.start()
    fqueue = FQueueController()
    fqueue.start()

    mongodb = MongoController()
    mongodb.start()


    # for MQTT
    mqttCtrl = MQTTController(
        host=os.getenv('MQTT_HOST', 'localhost'),
        port=os.getenv('MQTT_PORT', 1883),
        authen={
            'mode': 0,  # 0 --> user/password, 1 --> ssl
            'user': os.getenv('MQTT_USER', None),
            'password': os.getenv('MQTT_PASSWORD', None),
            # encode HS256
            'secret_key': os.getenv('MQTT_SECRET_KEY', None)
        }
    )
    mqttCtrl.addTopicListen(Topic.C_APP_RECEIVE_GW)
    mqttCtrl.setTopicDefaultToSend(Topic.C_APP_RECEIVE_GW)
    mqttCtrl.start()

    mqttCtrl = BasMqttSysnchorized()

    mqttCtrl.listen(MqttResponseHandle)

    mqttCtrl.listen(dev_keepalive.AdvDevKeepAliveHandle,
                key=EVT_REQUEST_DEVICE_STATUS,
                topic=Topic.KEEPALIVE)

    mqttCtrl.listen(adv_realtimelog.AdvLogHandle,
                key=EVT_ADVERTIS_SEND_DEVICE_LIFT_TO_APP_REALTIMELOG,
                topic=Topic.REALTIME_ADVERTIS,)

    mqttCtrl.listen(adv_handle.AdvUpdateScheduleHandle,
                    key=EVT_ADVERTIS_SEND_DEVICE_LIFT_TO_APP_UPDATE_SCHEDULE,
                    topic=Topic.C_APP_RECEIVE_GW)

    mqttCtrl.listen(adv_handle.AdvOneNetHandle,
                    topic=Topic.ONEMES_REQUEST)

    mqttCtrl.listen(sync_handle.synchronize_handle,
                    topic=Topic.C_APP_RECEIVE_SYNC_GW)

