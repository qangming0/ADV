from device.models import Device
from core.dataglobal import GlobalDeviceStatus
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

def updateStatus():
    # update device state
    devs = Device.objects.get_active().values('id', 'dev_ip', 'dev_mac', 'dev_ident', 'dev_system', 'dev_online')
    lstDevStatus = {}
    for dev in devs:
        lstDevStatus[dev['dev_ident']] = {
            "id": dev['id'],
            "ip": dev['dev_ip'],
            "mac": dev['dev_mac'],
            "system": dev['dev_system'],
            "status": dev['dev_online'],
        }
    if len(lstDevStatus) > 0:
        gds = GlobalDeviceStatus()
        gds.create(lstDevStatus)


# @receiver(post_save, sender=Device)
# def update_redis_device_status(sender, instance, created, **kwargs):
#     if created:
#         if sender == Device:
#             if instance.dev_ident is not None and len(instance.dev_ident) > 0:
#                 lstDevStatus = {}
#                 lstDevStatus[instance.dev_ident] = {
#                     "id": instance.id,
#                     "ip": instance.dev_ip,
#                     "mac": instance.dev_mac,
#                     "system": instance.dev_system,
#                     "status": False,
#                 }
#                 gds = GlobalDeviceStatus()
#                 gds.update(lstDevStatus)
#     else:
#         if sender == Device:
#             if instance.dev_ident is not None and len(instance.dev_ident) > 0:
#                 lstDevStatus = {}
#                 lstDevStatus[instance.dev_ident] = {
#                     "id": instance.id,
#                     "ip": instance.dev_ip,
#                     "mac": instance.dev_mac,
#                     "system": instance.dev_system,
#                     "status": False,
#                 }
#                 gds = GlobalDeviceStatus()
#                 gds.update(lstDevStatus)
#
#     if instance.dev_state == Device.STATE_ACTIVE and instance.dev_system == System.TYPE_PARKING:
#         personnels = Personnel.objects.all()
#         for person in personnels:
#             sync_data = PersonSynSerializer(person, read_only=True).data
#             data_syn_to_device(person, None, sync_data, [instance])


@receiver(pre_delete, sender=Device)
def pre_delete_model_handle(sender, instance, using, **kwargs):
    if sender == Device:
        if instance.dev_ident is not None and len(instance.dev_ident) > 0:
            gds = GlobalDeviceStatus()
            gds.delElement(instance.dev_ident)