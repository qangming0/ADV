import logging

logger = logging.getLogger('django')
from core.mqbroker.event import *
from device.models import Device
from core.syncreceivehandler import SyncReceiveHandler


def synchronize_handle(instance):
    try:
        msgRec = instance.data.value

        devIdRecv = msgRec['fromAddr']
        dataRecv = msgRec['data']['status']
        sync_type = msgRec['data']['type']
        ident_key = '{}_{}_'.format(devIdRecv, sync_type)
        if dataRecv is None:
            raise Exception('Param  has be not matched')

        insSyn = None
        srh = SyncReceiveHandler()
        syncItem = srh.getElement(ident_key)

        if syncItem is not None:
            insSyn = syncItem['ins']

        if insSyn is not None:
            device = insSyn.advd_device
            if int(dataRecv) == 1:
                insSyn.advd_synchronized = True
                insSyn.save()
                device.dev_sync_state = Device.SYNC_STATE_DONE
                srh.update_response(ident=ident_key, result=SyncReceiveHandler.RESPONSE_TYPE_SUCCESS)
            else:
                device.dev_sync_state = Device.SYNC_STATE_FAILED
                srh.update_response(ident=ident_key, result=SyncReceiveHandler.RESPONSE_TYPE_FAILED)

            device.save()


    except Exception as ex:
        logger.error(str(ex))
