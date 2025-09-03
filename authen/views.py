#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
from django.conf import settings
from core.views import BaseViewMixin, DefaultsMixin
from core.views import CoreView, BaseView
from rest_framework import views, status
from rest_auth.utils import jwt_encode
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dj_rest_auth.serializers import TokenSerializer,JWTSerializer
from .models import User, Permission, Group
from .serializers import UserSerializer, UserDetailSerializer
from .serializers import GroupListSerializer, GroupDetailSerializer
from .serializers import UserSerializer, UserDetailSerializer, GroupSerializer
from dj_rest_auth.registration.views import RegisterView
from authen.permission_modules import modules
from django.http import JsonResponse
from .filtersets import UserFilter


class UserList(BaseViewMixin, *BaseView('create', 'list')):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter

    filterset_fields = {
        'last_name': ['exact', 'icontains'],
        'email': ['exact', 'icontains'],
        'is_active': ['exact']
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserDetail(BaseViewMixin, *BaseView('show', 'edit', 'delete')):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UserExt(views.APIView):
    @api_view(['GET'])
    @permission_classes((IsAuthenticated,))
    def getRequestUser(request, format=None):
        user = User.objects.get(pk=request.user.id)
        serializer = UserDetailSerializer(user)
        response = serializer.data
        # permissions = user.get_all_permissions().values('id', 'name')
        # response["permissions"] = permissions
        response["ws_cfg"] = "user"

        return Response(response, status=status.HTTP_200_OK)


class GroupList(BaseViewMixin, *BaseView('create', 'list')):
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

    # filterset_class = PermissionFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.serializer_class = GroupSerializer
        request.data['permiss'] = request.data['permissions']
        request.data['permissions'] = []
        return self.create(request, *args, **kwargs)


class GroupFullList(DefaultsMixin, *BaseView('list')):
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer
    paginator = None

    def get(self, request, *args, **kwargs):
        paginator = None
        return self.list(request, *args, **kwargs)


class GroupDetail(BaseViewMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Group.objects.all()
    serializer_class = GroupDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.serializer_class = GroupSerializer
        request.data['permiss'] = request.data['permissions']
        request.data['permissions'] = []
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PermissionList(BaseViewMixin, *BaseView('create', 'list')):
    queryset = Permission.objects.all()
    serializer_class = GroupListSerializer

    # filterset_class = PermissionFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PermissionDetail(BaseViewMixin, *BaseView('show', 'edit', 'delete')):
    queryset = Permission.objects.all()
    serializer_class = GroupDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateUserView(RegisterView):
    def post(self, request, *args, **kwargs):
        auto_password = request.data.pop('auto_password', False)
        request.data['username'] = request.data.get(
            'username',
            request.data.get('email')
        )
        if auto_password:
            password = uuid.uuid4().hex[:10]
            request.data['password1'] = password
            request.data['password2'] = password
            print(password)
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        password = serializer.validated_data['password1']
        self.request._request.content_params['password'] = password
        user = serializer.save(self.request)
        user.last_name = self.request.data.get('last_name')
        user.is_staff = True
        user.groups.set(Group.objects.filter(id__in=self.request.data.get(
            'groups', [])))
        user.save()
        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(user)
        else:
            create_token(self.token_model, user, serializer)
        return user

class PermissionStructure(BaseViewMixin, *BaseView('list')):
    def get(self, request, *args, **kwargs):
        return JsonResponse(modules, safe=False)
