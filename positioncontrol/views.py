from core.views import BaseView, DefaultsMixin
from .models import PositionView, PositionItem
from .serializers import PositionViewSerializer, AdvFloorSerializer, AdvPostSerializer
from globalconfig.models import Floor
from rest_framework import status
from rest_framework.response import Response
import json

class PositionViewList(DefaultsMixin, *BaseView('list',)):
    queryset = PositionView.objects.all()
    serializer_class = PositionViewSerializer

    filterset_fields = {
        'pov_building': ['exact'],
        'pov_view_id': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class PositionViewDetail(DefaultsMixin, *BaseView('show',)):
    queryset = PositionView.objects.all()
    serializer_class = PositionViewSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class AdvertisePositionList(DefaultsMixin, *BaseView('list',)):
    queryset = Floor.objects.all()
    serializer_class = AdvFloorSerializer

    filterset_fields = {
        'flr_building': ['exact'],
    }

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = AdvFloorSerializer(queryset, many=True)
        floor_list = serializer.data

        flr_building = request.GET.get('flr_building', None)
        if flr_building:
            pov = PositionView.objects.filter(pov_building=flr_building, pov_view_id=PositionView.VIEW_ADV).first()

            # Mapping image background and position to adv device
            if pov is not None:
                position_items = pov.position_items.all()
                for poi in position_items:
                    try:
                        items = json.loads(poi.poi_items)
                    except:
                        items = []
                    # Get image background
                    indexes = [i for i, x in enumerate(floor_list) if x.get('id', None) == poi.poi_data_id]
                    if len(indexes):
                        index = indexes[0]
                        floor_list[index]['media_src'] = poi.get_abs_media_url(request)
                        floor_list[index]['media_id'] = poi.poi_media_id

                        for item in items:
                            # get item position
                            itemIndexs = [i for i, x in enumerate(floor_list[index]['items']) if x.get('id', None) == item['id']]
                            if len(itemIndexs):
                                itemIndex = itemIndexs[0]
                                floor_list[index]['items'][itemIndex]['top'] = item['top']
                                floor_list[index]['items'][itemIndex]['left'] = item['left']
        return Response(floor_list)

    def post(self, request, *args, **kwargs):
        serializer = AdvPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pov_building = serializer.data.pop('pov_building', None)
        pov_view_id = serializer.data.pop('pov_view_id', None)
        poi_media = serializer.data.pop('poi_media', None)
        poi_data_id = serializer.data.pop('poi_data_id', None)
        items = serializer.data.pop('items', '[]')

        # get or create position view
        pov, created = PositionView.objects.get_or_create(
            pov_building_id=pov_building,
            pov_view_id=pov_view_id,
            pov_data_object=PositionView.OBJECT_FLOOR
        )

        # get or create position item
        poi, created = PositionItem.objects.get_or_create(
            poi_pos_view_id=pov.id,
            poi_data_id=poi_data_id
        )

        # save media and items position
        if poi_media:
            poi.poi_media_id = poi_media
        poi.poi_items = items
        poi.save()

        return Response(serializer.data)







