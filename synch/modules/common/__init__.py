from core.mqbroker.topic import Topic
# from core.mqbroker.kafqueuesynchronize import BaseKAFQueueSysnchorized
from core.mqbroker.mqttqueuesynchronize import BaseMqttQueueSysnchorized


# class KAFQueueSysnchorized(BaseKAFQueueSysnchorized):
#     def __init__(self):
#         self.topic = Topic.P_APP_SEND_GW
#         super(KAFQueueSysnchorized, self).__init__(topic=self.topic)


class MqttQueueSysnchorized(BaseMqttQueueSysnchorized):
    def __init__(self):
        self.topic = Topic.P_APP_SEND_GW
        super(MqttQueueSysnchorized, self).__init__(topic=self.topic)