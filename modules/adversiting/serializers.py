import datetime
import logging
from django.utils.translation import gettext, ugettext_lazy as _
from rest_framework import serializers
from core.serializers import CoreModelSerializer
from modules.adversiting.models import AdvSchedule, AdvPlan, AdvContent, OneNetContent, TYPE_RELAX, TYPE_ADV
from .dataforsync import parseDataForSync
from django.db import transaction
logger = logging.getLogger('django')


class AdvScheduleContentListSerializer(CoreModelSerializer):
    advc_media_name = serializers.ReadOnlyField(source='advc_media.med_name')
    advc_media_datestart = serializers.ReadOnlyField(source='advc_media.med_start_date')
    advc_media_dateend = serializers.ReadOnlyField(source='advc_media.med_end_date')
    advc_media_duration = serializers.ReadOnlyField(source='advc_media.med_duration')
    advc_media_readable_duration = serializers.ReadOnlyField(source='advc_media.readable_duration')
    id = serializers.IntegerField(required=False)

    class Meta:
        model = AdvContent
        fields = ('advc_media_name', 'advc_media_datestart', 'advc_media_dateend', 'advc_media_duration', 'advc_media'
                  , 'advc_descript', 'advc_durations', 'id', 'advc_media_readable_duration')
        extra_kwargs = {'id': {'read_only': False}}


class AdvSchedulePlanListSerializer(CoreModelSerializer):
    advcontent = AdvScheduleContentListSerializer(many=True, required=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = AdvPlan
        fields = ('advcontent', 'advp_name', 'advp_durations', 'advp_interval', 'advp_timestart', 'advp_timeend', 'id')
        extra_kwargs = {'id': {'read_only': False}}


class AdvScheduleListSerializer(CoreModelSerializer):
    advs_type_name = serializers.ReadOnlyField()
    advs_devices_count = serializers.SerializerMethodField()
    advplan = AdvSchedulePlanListSerializer(many=True, required=False)
    advcontent = AdvScheduleContentListSerializer(many=True, required=False)
    lstDevsTotal = serializers.ReadOnlyField(default=[])

    class Meta:
        model = AdvSchedule
        fields = '__all__'

    def get_advs_devices_count(self, obj):
        return obj.advs_devices.count()

    def create_or_update_content(self, inputs, oldIds=[]):
        id = inputs.pop('id', 0)
        if id > 0:
            if id in oldIds:
                oldIds.remove(int(id))
            lstIns = AdvContent.objects.filter(id=id)
            lstIns.update(**inputs)
            ins = lstIns[0]
        else:
            ins = AdvContent(**inputs)
            ins.save()
        return ins

    def create_or_update_plan(self, inputs, oldIds=[]):
        id = inputs.pop('id', 0)
        if id > 0:
            if id in oldIds:
                oldIds.remove(int(id))
            lstIns = AdvPlan.objects.filter(id=id)
            lstIns.update(**inputs)
            ins = lstIns[0]
        else:
            ins = AdvPlan(**inputs)
            ins.save()
        return ins


    def create(self, validated_data):
        try:
            with transaction.atomic():
                contents = validated_data.pop('advcontent', [])
                plans = validated_data.pop('advplan', [])
                devices = validated_data.pop('advs_devices', [])
                instance = AdvSchedule(**validated_data)
                instance.save()
                instance.advs_devices.set(devices)
                if validated_data['advs_type'] == TYPE_RELAX:
                    # update content list
                    orgContents = list(instance.advcontent.values_list("id", flat=True))
                    for content in  contents:
                        content['advc_schedule'] = instance
                        self.create_or_update_content(content, orgContents)
                    # delete content not need
                    AdvContent.objects.filter(id__in=orgContents).delete()
                else:
                    # TYPE_ADV
                    orgPlans = list(instance.advplan.values_list("id", flat=True))
                    for plan in plans:
                        contents = plan.pop('advcontent', [])
                        plan['advp_schedule'] = instance
                        ins = self.create_or_update_plan(plan, orgPlans)
                        # update content list
                        orgContents = list(ins.advcontent.values_list("id", flat=True))
                        for content in contents:
                            content['advc_plan'] = ins
                            self.create_or_update_content(content, orgContents)
                        # delete content not need
                        AdvContent.objects.filter(id__in=orgContents).delete()
                    # delete plan not need
                    AdvPlan.objects.filter(id__in=orgPlans).delete()
                instance.save()
        except Exception as ex:
            logger.error(_("Error: %s" %(str(ex),)))
            raise serializers.ValidationError(_("Error: %s" %(str(ex),)))
        # for sync
        parseDataForSync(instance.advs_devices.all(), instance.advs_type)
        return instance


    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                contents = validated_data.pop('advcontent', [])
                plans = validated_data.pop('advplan', [])
                if validated_data['advs_type'] == TYPE_RELAX:
                    # update content list
                    orgContents = list(instance.advcontent.values_list("id", flat=True))
                    for content in contents:
                        content['advc_schedule'] = instance
                        self.create_or_update_content(content, orgContents)
                    # delete content not need
                    AdvContent.objects.filter(id__in=orgContents).delete()
                else:
                    # TYPE_ADV
                    orgPlans = list(instance.advplan.values_list("id", flat=True))
                    for plan in plans:
                        contents = plan.pop('advcontent', [])
                        plan['advp_schedule'] = instance
                        ins = self.create_or_update_plan(plan, orgPlans)
                        # update content list
                        orgContents = list(ins.advcontent.values_list("id", flat=True))
                        for content in contents:
                            content['advc_plan'] = ins
                            self.create_or_update_content(content, orgContents)
                        # delete content not need
                        AdvContent.objects.filter(id__in=orgContents).delete()
                    # delete plan not need
                    AdvPlan.objects.filter(id__in=orgPlans).delete()
                # lstIns = AdvSchedule.objects.filter(id=instance.id)
                # lstIns.update(**validated_data)
                instance.advs_name = validated_data.get('advs_name', instance.advs_name)
                instance.advs_type = validated_data.get('advs_type', instance.advs_type)
                instance.advs_datetart = validated_data.get('advs_datetart', instance.advs_datetart)
                instance.advs_dateend = validated_data.get('advs_dateend', instance.advs_dateend)
                # get list device be removed
                lstNewDevs = validated_data.get('advs_devices', None)
                lstDevsTotal = lstNewDevs.copy()
                for dev in instance.advs_devices.all():
                    if dev not in lstDevsTotal:
                        lstDevsTotal.append(dev)
                if lstNewDevs:
                    instance.advs_devices.set(lstNewDevs)
                instance.save()
        except Exception as ex:
            logger.error(_("Error: %s" % (str(ex),)))
            raise serializers.ValidationError(_("Error: %s" % (str(ex),)))
        # for sync
        parseDataForSync(lstDevsTotal, instance.advs_type)
        instance.lstDevsTotal = [dev.id for dev in lstDevsTotal]
        return instance


class AdvScheduleDetailSerializer(CoreModelSerializer):
    class Meta:
        model = AdvSchedule
        fields = '__all__'


class AdvPlanListSerializer(CoreModelSerializer):
    class Meta:
        model = AdvPlan
        fields = '__all__'


class AdvPlanDetailSerializer(CoreModelSerializer):
    class Meta:
        model = AdvPlan
        fields = '__all__'


class AdvContentListSerializer(CoreModelSerializer):
    advc_media_name = serializers.ReadOnlyField(source='advc_media.med_name')
    advc_media_datestart = serializers.ReadOnlyField(source='advc_media.med_start_date')
    advc_media_dateend = serializers.ReadOnlyField(source='advc_media.med_end_date')
    advc_media_duration = serializers.ReadOnlyField(source='advc_media.med_duration')

    class Meta:
        model = AdvContent
        fields = '__all__'


class AdvContentDetailSerializer(CoreModelSerializer):
    class Meta:
        model = AdvContent
        fields = '__all__'


class OneNetContentListSerializer(CoreModelSerializer):
    onc_priority_name = serializers.ReadOnlyField(source='get_onc_priority_display')
    onc_device_name = serializers.ReadOnlyField(source='onc_device.__str__')

    class Meta:
        model = OneNetContent
        fields = '__all__'

class OneNetContentDetailSerializer(CoreModelSerializer):
    onc_priority_name = serializers.ReadOnlyField(source='get_onc_priority_display')
    onc_device_name = serializers.ReadOnlyField(source='onc_device.__str__')

    class Meta:
        model = OneNetContent
        fields = '__all__'





