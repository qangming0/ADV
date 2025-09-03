from .models import Building, Zone, Floor, Door
from .serializers import ZoneListSerializer, BuildingListSerializer, FloorListSerializer
from .serializers import DoorListSerializer, DoorDetailSerializer
from core.views import DefaultsMixin, BaseView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
from globalconfig.serializers import BuildingSelectionSerializer
from globalconfig.serializers import FloorSelectionSerializer
from globalconfig.serializers import ZoneSelectionSerializer
from globalconfig.serializers import DoorSelectionSerializer
from globalconfig.serializers import FloorLightingStateSerializer
from globalconfig.form import DoorSelectFilter, DoorListFilter, ZoneExtendFilter, ZoneListFilter
from .form import FloorListFilter
from core.permissions import IsStaffOrAdmin


# Create your views here.

class BuildingList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = Building.objects.all()
    serializer_class = BuildingListSerializer

    filterset_fields = {
        'bdg_name': ['exact', 'icontains'],
        'bdg_address': ['exact', 'icontains'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BuildingDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Building.objects.all()
    serializer_class = BuildingListSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class FloorList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = Floor.objects.all()
    serializer_class = FloorListSerializer
    filterset_class = FloorListFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FloorDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Floor.objects.all()
    serializer_class = FloorListSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ZoneList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = Zone.objects.all()
    serializer_class = ZoneListSerializer
    filterset_class = ZoneListFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ZoneDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Zone.objects.all()
    serializer_class = ZoneListSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class DoorList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = Door.objects.all()
    serializer_class = DoorListSerializer
    filterset_class = DoorListFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DoorDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Door.objects.all()
    serializer_class = DoorDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class BuildingExt(APIView):
    @api_view(['GET'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin,))
    def getList(request):
        states = [{'id': x[0], 'value': x[1]} for x in Floor.STATE_CHOICE]
        response = {
            'states': states,
        }
        return JsonResponse(response, safe=False)


class BuildingSelection(DefaultsMixin, *BaseView('list')):
    serializer_class = BuildingSelectionSerializer
    queryset = Building.objects.all()
    filterset_fields = {}

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FloorSelection(DefaultsMixin, *BaseView('list')):
    serializer_class = FloorSelectionSerializer
    queryset = Floor.objects.all()
    filterset_fields = {
        'flr_building': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ZoneSelection(DefaultsMixin, *BaseView('list')):
    serializer_class = ZoneSelectionSerializer
    queryset = Zone.objects.all()
    filterset_fields = {
        'zone_floor': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DoorSelection(DefaultsMixin, *BaseView('list')):
    serializer_class = DoorSelectionSerializer
    queryset = Door.objects.all()
    filterset_class = DoorSelectFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FloorLightingState(DefaultsMixin, *BaseView('list', )):
    queryset = Floor.objects.all()
    serializer_class = FloorLightingStateSerializer

    # Disable pagination to get all floor in building
    paginate_by = None
    paginate_by_param = None
    max_paginate_by = None

    filterset_fields = {
        'flr_code': ['exact', 'icontains'],
        'flr_name': ['exact', 'icontains'],
        'flr_state': ['exact'],
        'flr_position': ['exact'],
        'flr_building': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
