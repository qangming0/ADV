from core.serializers import CoreModelSerializer
from .models import Media
from rest_framework import serializers


class MediaSerializer(CoreModelSerializer):
    readable_size = serializers.ReadOnlyField()
    readable_duration = serializers.ReadOnlyField()
    med_user_name = serializers.ReadOnlyField()
    med_abs_url = serializers.SerializerMethodField(read_only=True)

    def get_med_abs_url(self, obj):
        if hasattr(obj, 'med_url'):
            # if obj.med_url and obj.med_url.startswith('/'):
            #     return self.context['request'].build_absolute_uri(obj.med_url)
            # else:
            #     return obj.med_url
            return obj.med_url
        return None

    class Meta:
        model = Media
        fields = '__all__'

class ImportLinkYoutubeSerializer(serializers.Serializer):
    items = MediaSerializer(many=True)
    med_parent = serializers.PrimaryKeyRelatedField(queryset=Media.objects.filter(med_is_folder=True),required=False, allow_null=True, default=None)


