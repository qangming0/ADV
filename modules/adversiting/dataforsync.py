import logging
import json
from django.utils.translation import gettext, ugettext_lazy as _
from datetime import datetime, date, time, timedelta
from rest_framework import serializers
from core.serializers import CoreModelSerializer
from device.models import Device
from modules.adversiting.models import (
    AdvDataSynch, AdvSchedule, AdvPlan,
    AdvContent, OneNetContent, TYPE_RELAX, TYPE_ADV
)
from django.contrib.sites.models import Site
from utils.urls import get_media_url
logger = logging.getLogger('django')


class AdvSyncContentReLexListSerializer(CoreModelSerializer):
    duration = serializers.ReadOnlyField(source='advc_durations')
    # url = serializers.ReadOnlyField(source='advc_media.med_url')
    url = serializers.SerializerMethodField()
    type = serializers.ReadOnlyField(source='advc_media.med_type')
    name = serializers.ReadOnlyField(source='advc_media.med_name')
    md5 = serializers.ReadOnlyField(source='advc_media.med_md5checksum')
    id = serializers.ReadOnlyField(source='advc_media.id')

    class Meta:
        model = AdvContent
        fields = ('duration', 'url', 'type', 'name', 'id', 'md5')

    def get_url(self, obj):
        media = obj.advc_media
        try:
            return get_media_url(media.med_url)
        except Exception as ex:
            return ''


class AdvSyncContentListSerializer(CoreModelSerializer):
    duration = serializers.ReadOnlyField(source='advc_durations')
    url = serializers.SerializerMethodField()
    type = serializers.ReadOnlyField(source='advc_media.med_type')
    name = serializers.ReadOnlyField(source='advc_media.med_name')
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    md5 = serializers.ReadOnlyField(source='advc_media.med_md5checksum')
    id = serializers.ReadOnlyField(source='advc_media.id')

    class Meta:
        model = AdvContent
        fields = ('duration', 'url', 'type', 'name', 'start', 'end', 'id', 'md5')

    def get_url(self, obj):
        media = obj.advc_media
        try:
            return get_media_url(media.med_url)
        except Exception as ex:
            return ''

    def get_start(self, obj):
        media = obj.advc_media
        try:
            if media.med_start_date is None or media.med_start_date == '':
                if obj.advc_plan is not None:
                    return obj.advc_plan.advp_schedule.advs_datetart
                else:
                    return obj.advc_schedule.advs_datetart
            else:
                return media.med_start_date
        except Exception as ex:
            return ''

    def get_end(self, obj):
        media = obj.advc_media
        try:
            if media.med_end_date is None or media.med_end_date == '':
                if obj.advc_plan is not None:
                    return obj.advc_plan.advp_schedule.advs_dateend
                else:
                    return obj.advc_schedule.advs_dateend
            else:
                return media.med_start_date
        except Exception as ex:
            return ''


class AdvSyncPlanListSerializer(CoreModelSerializer):
    content = AdvSyncContentListSerializer(source='advcontent', many=True)
    start = serializers.ReadOnlyField(source='advp_timestart')
    end = serializers.ReadOnlyField(source='advp_timeend')

    class Meta:
        model = AdvPlan
        fields = ('content', 'start', 'end')


class AdvSyncScheduleListSerializer(CoreModelSerializer):
    data = serializers.SerializerMethodField()
    start = serializers.ReadOnlyField(source='advs_datetart')
    end = serializers.ReadOnlyField(source='advs_dateend')
    type = serializers.ReadOnlyField(source='advs_type')

    class Meta:
        model = AdvSchedule
        fields = ('data', 'type', 'start', 'end' )

    def get_data(self, obj):
        if obj.advs_type == TYPE_ADV:
            return AdvSyncPlanListSerializer(obj.advplan, many=True).data
        else:
            return AdvSyncContentReLexListSerializer(obj.advcontent, many=True).data


class AdvSyncDevice(CoreModelSerializer):
    advschedule = serializers.SerializerMethodField()
    class Meta:
        model = Device
        fields = ('advschedule', 'id', 'dev_ident')

    def get_advschedule(self, obj):
        qs = obj.advschedule.filter(advs_dateend__gte=datetime.now().date()).order_by('-id')
        return AdvSyncScheduleListSerializer(qs, many=True).data


def orderTimePeriod(lstTimePeriods, sort='ASC'):
    __len = len(lstTimePeriods)
    for i in range(__len - 1):
        for j in range(i + 1, __len):
            start_i = lstTimePeriods[i]['start']
            start_j = lstTimePeriods[j]['start']
            if sort=='ASC':
                if start_i > start_j:
                    temp = lstTimePeriods[i]
                    lstTimePeriods[i] = lstTimePeriods[j]
                    lstTimePeriods[j] = temp
            else: # DESC
                if start_i < start_j:
                    temp = lstTimePeriods[i]
                    lstTimePeriods[i] = lstTimePeriods[j]
                    lstTimePeriods[j] = temp
    return lstTimePeriods

def mergeSchedule(currentSlots, slot):
    newSlotes = [
        {
            'start': slot['start'],
            'end': slot['end'],
            'data': slot['data'],
            # 'type': slot['type']
        }
    ]
    for slot in currentSlots:
        # slot----------[Ts//////////////////////////Te]-------------------------[Ts////////////////Te]-----
        # 0--------------------[//////////////]-------------------------------------------------------------
        # 1----[......]-------------------------------------------------------------------------------------
        # 2-------[.....)/////////]-------------------------------------------------------------------------
        # 3------[......)//////////////////////////////(....]-----------------------------------------------
        # 4-----------------------------------[////////(...........]----------------------------------------
        # 5-------------------------------------------------[.............]---------------------------------
        slotTemps = []
        for newslot in newSlotes:
            if (newslot['start'] < slot['start'] and newslot['end'] <= slot['start']) \
                    or (newslot['start'] >= slot['end'] and newslot['end'] > slot['end']):
                if newslot['start'] == slot['end']:
                    newslot['start'] += timedelta(days=1)
                if newslot['end'] == slot['start']:
                    newslot['end'] -= timedelta(days=1)
                slotTemps.append(newslot)

            elif newslot['start'] < slot['start'] and newslot['end'] > slot['start'] and newslot['end'] <= slot['end']:
                slotTemps.append({
                    'start': newslot['start'],
                    'end': slot['start'] - timedelta(days=1),
                    'data': newslot['data'],
                    # 'type': newslot['type']
                })

            elif newslot['start'] < slot['start'] and newslot['end'] > slot['end']:
                slotTemps.append({
                    'start': newslot['start'],
                    'end': slot['start'] - timedelta(days=1),
                    'data': newslot['data'],
                    # 'type': newslot['type']
                })
                slotTemps.append({
                    'start': slot['end'] + timedelta(days=1),
                    'end': newslot['end'],
                    'data': newslot['data'],
                    # 'type': newslot['type']
                })

            elif newslot['start'] >= slot['start'] and newslot['start'] <= slot['end'] and newslot['end'] > slot['end']:
                slotTemps.append({
                    'start': slot['end'] + timedelta(days=1),
                    'end': newslot['end'],
                    'data': newslot['data'],
                    # 'type': newslot['type']
                })

            else:
                # throw away newslot['start'] >= slot['start'] and newslot['end'] <= slot['end']
                pass
        newSlotes = slotTemps.copy()
    currentSlots = currentSlots + newSlotes
    return currentSlots

def datetimeconverter(o):
    if isinstance(o, (datetime, date, time)):
        return o.__str__()

def create_or_update_datasynch(devid, type, data):
    objs = AdvDataSynch.objects.filter(advd_device_id=devid, advd_type=type)
    if objs and objs.count() > 0:
        #update
        obj = objs[0]
    else:
        #create
        obj = AdvDataSynch()
    obj.advd_device_id = devid
    obj.advd_value = json.dumps(data, default=datetimeconverter)
    obj.advd_type = type
    obj.advd_synchronized = False
    obj.save()

def parseDataForSync(devObjs, msgType=TYPE_ADV):
    results = AdvSyncDevice(devObjs, many=True).data
    for devData in results:
        lstScheduleMatch = []
        for schedule in devData['advschedule']:
            if schedule['type'] == msgType:
                lstScheduleMatch.append(schedule)
        lstNewSchedule = []
        for schedule in lstScheduleMatch:
            lstNewSchedule = mergeSchedule(lstNewSchedule, schedule)

        lstNewSchedule = orderTimePeriod(lstNewSchedule, sort='DESC')
        # update device for sync
        if len(lstNewSchedule) >= 0:
            create_or_update_datasynch(devData['id'], msgType, {
                'type': msgType,
                'schedule': lstNewSchedule
            })
