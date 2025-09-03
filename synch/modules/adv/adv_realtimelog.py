#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from device.models import Device
from media.models import Media
logger = logging.getLogger('django')


def AdvLogHandle(instance):
    try:
        logger.debug('realtime log handler: adv realtime')
        # @@@FIXME: now only suport for device mode, not device interface mode ( DI )
        msgRec = instance.data.value
        dataRecv = msgRec['data']
        devIdRecv = msgRec['fromAddr']

        if dataRecv is None:
            raise Exception('Param  has be not matched')

        logger.debug('realtime log handler: access controller system %s' % (devIdRecv,))

        devs = Device.objects.filter(dev_ident=devIdRecv)
        meds = Media.objects.filter(id=dataRecv['msgData']['content']['id'])
        if devs and devs.count() == 1 and meds.count() == 1:
            dev = devs[0]
            dev.dev_diskspace = dataRecv['msgData']['space']
            dev.dev_mediaplay = meds[0]
            dev.save()

    except Exception as ex:
        logger.error(str(ex))

