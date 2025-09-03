import logging
from django.db import transaction
from django.utils.translation import gettext, ugettext_lazy as _
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
from core.views import BaseView, DefaultsMixin, MessageResponse
from modules.adversiting.models import AdvSchedule, AdvPlan, AdvContent, OneNetContent
from modules.adversiting.serializers import AdvScheduleListSerializer, AdvScheduleDetailSerializer
from modules.adversiting.serializers import AdvPlanListSerializer, AdvPlanDetailSerializer
from modules.adversiting.serializers import AdvContentListSerializer, AdvContentDetailSerializer
from modules.adversiting.serializers import OneNetContentListSerializer, OneNetContentDetailSerializer
from modules.adversiting.form import AdvContentFilter, AdvPlanFilter, AdvScheduleFilter, OneNetContentFilter
from modules.adversiting import models as advmodels
from core.permissions import IsStaffOrAdmin
from synch.modules.adv.adv_view import AdvSync
from device.models import Device
logger = logging.getLogger('django')


def json_response(devResponse=None, res=MessageResponse()):
    # Get response
    if devResponse is not None:
        if devResponse['result'] is None:
            res.success = False
        else:
            res.success = devResponse['result'].success
        res.data = {
            'data': res.data,
        }
        if len(devResponse['offlines']):
            res.data['offlines'] = list(
                Device.objects.filter(dev_ident__in=devResponse['offlines']).values_list('dev_name', flat=True))

        if len(devResponse['errors']):
            res.data['errors'] = list(
                Device.objects.filter(dev_ident__in=devResponse['errors']).values_list('dev_name', flat=True))
    else:
        res.success = False
    return res


class AdvScheduleList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = AdvSchedule.objects.all()
    serializer_class = AdvScheduleListSerializer
    filterset_class = AdvScheduleFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        res = self.create(request, *args, **kwargs)
        sync = AdvSync()
        msgResult = sync.advSyncToDev(res.data['advs_devices'], request.user)
        json_response(msgResult, res)
        return res


class AdvScheduleDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = AdvSchedule.objects.all()
    serializer_class = AdvScheduleListSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        res = self.update(request, *args, **kwargs)
        sync = AdvSync()
        # sync.sendNotice()
        msgResult = sync.advSyncToDev(res.data['lstDevsTotal'], request.user)
        json_response(msgResult, res)
        return res

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AdvPlanList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = AdvPlan.objects.all()
    serializer_class = AdvPlanListSerializer
    filterset_class = AdvPlanFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdvPlanDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = AdvPlan.objects.all()
    serializer_class = AdvPlanDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AdvContentList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = AdvContent.objects.all()
    serializer_class = AdvContentListSerializer
    filterset_class = AdvContentFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdvContentDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = AdvContent.objects.all()
    serializer_class = AdvContentDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OneNetContentList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = OneNetContent.objects.all()
    serializer_class = OneNetContentListSerializer
    filterset_class = OneNetContentFilter
    ordering_fields = ('-id', '-created',)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OneNetContentDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = OneNetContent.objects.all()
    serializer_class = OneNetContentDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AdvScheduleChoise(APIView):
    @api_view(['GET'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin,))
    def get(request):
        res = MessageResponse()
        states = [
            {
                'id': advmodels.TYPE_RELAX,
                'value': _('Relex')
            },
            {
                'id': advmodels.TYPE_ADV,
                'value': _('Advertise')
            }
        ]
        res.setAttr('results', states)
        return JsonResponse(res.getAttr(), safe=False)