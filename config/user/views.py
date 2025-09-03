from core.views import DefaultsMixin, BaseView
from .models import UserConfig
from .serializers import UserConfigSerializer
from .permissions import IsOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
# Create your views here.
class UserConfigList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = UserConfig.objects.all()
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated , IsOwner,]

    filterset_fields = {
        'uco_key': ['exact'],
    }

    def create(self, request, *args, **kwargs):
        # add config into request user
        input_data = request.data
        input_data['uco_user'] = request.user.id
        serializer = self.get_serializer(data=input_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # filter config of owner user
        return UserConfig.objects.filter(uco_user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserConfigDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = UserConfig.objects.all()
    serializer_class = UserConfigSerializer
    permission_classes = [IsAuthenticated , IsOwner,]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)