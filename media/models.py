from django.db import models
from core.models import CoreModel
from django.template.defaultfilters import filesizeformat
from authen.models import User
import os
import datetime

# Create your models here.

class Media(CoreModel):

    DEFAULT_DURATION = 5

    TYPE_VIDEO = 'video'
    TYPE_AUDIO = 'audio'
    TYPE_IMAGE = 'image'
    TYPE_YOUTUBE = 'youtube'
    TYPE_UNKNOWN = 'unknown'
    TYPE_STREAM_RTMP = 'rtmp'
    TYPE_STREAM_RTSP = 'rtsp'
    TYPE_STREAM_UDP = 'udp'

    med_name = models.CharField(max_length=50)
    med_real_name = models.CharField(max_length=50, null=True, blank=True)
    med_type = models.CharField(max_length=15, null=True, blank=True)
    med_content_type = models.CharField(max_length=50, null=True, blank=True)
    med_size = models.IntegerField(blank=True, null=True)
    med_path = models.CharField(max_length=200, blank=True, null=True)
    med_url = models.CharField(max_length=100, blank=True, null=True)
    med_extension = models.CharField(max_length=10, blank=True, null=True)
    med_md5checksum = models.CharField(max_length=50, blank=True, null=True)

    med_parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='media')
    med_description = models.CharField(max_length=200, null=True, blank=True)
    med_start_date = models.DateField(null=True, blank=True)
    med_end_date = models.DateField(null=True, blank=True)
    med_duration = models.IntegerField(null=True, blank=True)
    med_youtube_id = models.CharField(max_length=20, null=True, blank=True)

    med_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media', null=True, blank=True)
    med_is_folder = models.BooleanField(default=False)

    def __str__(self):
        return self.med_name

    def delete(self, using=None, keep_parents=False):
        try:
            if not self.med_is_folder:
                os.remove(str(self.med_path))
        except OSError:
            pass
        return super(Media, self).delete(using, keep_parents)

    @property
    def readable_size(self):
        if not self.med_is_folder:
            return filesizeformat(self.med_size)
        else:
            return '--'

    @property
    def readable_duration(self):
        if (self.med_duration):
            return str(datetime.timedelta(seconds=self.med_duration))
        else:
            return '--'

    @property
    def med_user_name(self):
        if self.med_user:
            return self.med_user.username
        else:
            return ''

    def get_abs_url(self, request):
        # if self.med_url.startswith('/'):
        #     # return request.build_absolute_uri(self.med_url)
        # else:
        #     return self.med_url
        return self.med_url
