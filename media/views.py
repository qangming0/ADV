import hashlib
import os
import time
from datetime import datetime
from django.conf import settings
import subprocess
import uuid
from core.views import DefaultsMixin, BaseView
from .models import Media
from .serializers import MediaSerializer, ImportLinkYoutubeSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
import logging
from core.permissions import IsStaffOrAdmin
# Create your views here.


def getMediaType(content_type):
    if 'video' in content_type:
        type = Media.TYPE_VIDEO
    elif 'audio' in content_type:
        type = Media.TYPE_AUDIO
    elif 'image' in content_type:
        type = Media.TYPE_IMAGE
    else:
        type = Media.TYPE_UNKNOWN

    return type

def getVideoDuration(filename):
    try:
        command = 'ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'.format(filename)
        result = subprocess.Popen(command,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        output = result.communicate()
        duration = round(float(output[0]))
    except:
        duration = Media.DEFAULT_DURATION
    return duration

def handle_upload_image(file_obj, med_parent, request):
    res = {
        'success': True,
        'name': ''
    }
    file_path = None
    try:
        max_size_1gb = 1024 * 1024 * 1024
        res['name'] = file_obj.name
        if file_obj.size > max_size_1gb:
            res['success'] = False
            return res

        upload_date = datetime.now()
        media_url = settings.MEDIA_URL
        if media_url.endswith('/'):
            # fix wrong format media url, double '/' after media url
            # remove last '/' in media url
            media_url = media_url[:-1]
        directory = '%s/%d/%02d' % (media_url, upload_date.year, upload_date.month)

        # uploadFolder = settings.MEDIA_PATH
        uploadFolder = os.path.join(settings.MEDIA_PATH, str(upload_date.year), '%02d' % (upload_date.month))
        if not os.path.exists(uploadFolder):
            os.makedirs(uploadFolder)
        filename, extension = os.path.splitext(file_obj.name)
        file_name = upload_date.strftime('%Y%m%d_%H%M%S%f_') + uuid.uuid4().hex[:10] + str(extension.lower())
        md5 = hashlib.md5()

        with open(os.path.join(uploadFolder, file_name), 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
                md5.update(chunk)
        md5 = md5.hexdigest()

        media_type = getMediaType(file_obj.content_type)
        file_path = os.path.join(uploadFolder, file_name)
        if media_type == 'video' or media_type == 'audio':
            duration = getVideoDuration(file_path)
        else:
            duration = Media.DEFAULT_DURATION
        # fix wrong format url, replace '\' by '/'
        med_url = '{}/{}'.format(directory, file_name)
        Media.objects.create(
            med_name=file_obj.name[:50],
            med_real_name=file_name,
            med_type=media_type,
            med_content_type=file_obj.content_type[:50],
            med_size=file_obj.size,
            med_path=file_path,
            med_url=med_url,
            med_extension=extension.lower(),
            med_duration=duration,
            med_md5checksum=md5,
            med_user=request.user,
            med_parent_id=med_parent
        )
        res['success'] = True
    except Exception as ex:
        logging.error(ex, exc_info=True)
        res['success'] = False

        try:
            # try to remove file on error
            if file_path is not None:
                os.remove(str(file_path))
        except:
            pass
    finally:
        return res



class UploadMediaFile(APIView):
    @api_view(['POST'])
    @permission_classes((IsAuthenticated, IsStaffOrAdmin, ))
    def upload(request):

        file_list = request.FILES.getlist('file')
        if 'med_parent' in request.data:
            try:
                med_parent = int(request.data['med_parent'])
            except:
                med_parent = None
        else:
            med_parent = None

        final_result = {
            'success': [],
            'error': []
        }

        for file_obj in file_list:
            upload_result = handle_upload_image(file_obj, med_parent, request)

            if upload_result['success']:
                final_result['success'].append(upload_result['name'])
            else:
                final_result['error'].append(upload_result['name'])
        return JsonResponse(final_result, safe=False)

class FolderPath(DefaultsMixin, *BaseView('show',)):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        res = []
        while instance:
            res.append({
                'id': instance.id,
                'name': instance.med_name
            })
            instance = instance.med_parent
        return JsonResponse(res, safe=False)


class MediaList(DefaultsMixin, *BaseView('create', 'list')):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    ordering = ('-med_is_folder',)

    filterset_fields = {
        'med_name': ['exact', 'icontains', 'iexact'],
        'med_type': ['exact', 'icontains'],
        'med_extension': ['exact', 'icontains'],
        'med_user': ['exact'],
        'created': ['gte', 'lte']
    }

    def get_child_media(self, qs):
        lst_folder = parent_folder = list(qs.filter(med_is_folder=True).values_list('id', flat=True))
        while len(parent_folder) > 0:
            parent_folder = list(Media.objects.filter(med_is_folder=True, med_parent__in=parent_folder).exclude(id__in=lst_folder).values_list('id', flat=True))
            if len(parent_folder) > 0:
                lst_folder = lst_folder + parent_folder
        return Media.objects.filter(med_parent__in=lst_folder)
    
    def get_queryset(self):
        qs = Media.objects.all()
        params = self.request.GET
        if 'med_parent' in params and params['med_parent']:
            qs = qs.filter(med_parent=params['med_parent'])
        else:
            qs = qs.filter(med_parent__isnull=True)

        if 'child_folder' in params:
            if params['child_folder']:
                qs = qs | self.get_child_media(qs)

        return qs

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data['med_user'] = request.user.id
        return self.create(request, *args, **kwargs)


class MediaDetail(DefaultsMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # TODO Check file used in schedule, delete media in folder
        return self.destroy(request, *args, **kwargs)

class ImportYoutube(DefaultsMixin, *BaseView('create')):
    queryset = Media.objects.all()
    serializer_class = ImportLinkYoutubeSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.data
        items = validated_data.pop('items')
        med_parent = validated_data.pop('med_parent', None)
        created_id = []
        for item in items:
            item.pop('med_abs_url')
            media = Media(**item)
            media.med_parent_id = med_parent
            media.med_user = request.user
            # media.med_type = Media.TYPE_YOUTUBE
            if item['med_url'].startswith(Media.TYPE_STREAM_RTMP):
                media.med_type = Media.TYPE_STREAM_RTMP
            elif item['med_url'].startswith(Media.TYPE_STREAM_RTSP):
                media.med_type = Media.TYPE_STREAM_RTSP
            elif item['med_url'].startswith(Media.TYPE_STREAM_UDP):
                media.med_type = Media.TYPE_STREAM_UDP
            else:
                media.med_type = Media.TYPE_YOUTUBE
            media.save()
            created_id.append(media.id)
        return JsonResponse(created_id, safe=False)