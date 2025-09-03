from core.serializers import CoreModelSerializer
from .models import UserConfig


class UserConfigSerializer(CoreModelSerializer):
    class Meta:
        model = UserConfig
        fields = '__all__'