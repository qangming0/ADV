#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from .models import User, Group, Permission
from core.serializers import CoreModelSerializer
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordChangeSerializer
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


class UserSerializer(CoreModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserDetailSerializer(CoreModelSerializer):
    permission_codes = serializers.ReadOnlyField()
    groups = serializers.ListField(child=serializers.IntegerField(),
                                   default=[], write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'last_name',
            'require_change_password',
            'email',
            'permission_codes',
            'is_staff',
            'is_superuser',
            'groups'
        ]

    def validate_groups(self, data):
        return Group.objects.filter(id__in=data)

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', [])
        newinstance = super().update(instance, validated_data)
        newinstance.groups.set(groups)
        newinstance.save()
        return newinstance


class GroupListSerializer(CoreModelSerializer):
    permissions = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = '__all__'

    def get_permissions(self, obj):
        # permis = PermissionListSerializer(obj.permissions, many=True).data
        permis_codes = obj.permissions.all().values_list('code', flat=True)
        return {"perm_{}".format(code, ): True for code in permis_codes}

    def get_user(self, obj):
        return obj.user_set.values_list('id', flat=True)


class GroupDetailSerializer(CoreModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class PermissionListSerializer(CoreModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class PermissionDetailSerializer(CoreModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class NameRegistrationSerializer(RegisterSerializer):
    last_name = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=True)
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True
    )

    def custom_signup(self, request, user):
        user.last_name = self.validated_data.get('last_name', '')
        user.is_active = self.validated_data.get('is_active', '')
        user.personnel = self.validated_data.get('personnel', None)
        groups = self.validated_data.get('groups', [])
        user.groups.set(groups)
        user.require_change_password = True
        user.is_staff = True
        user.save(update_fields=['last_name', 'is_active', 'personnel', 'require_change_password', 'is_staff'])


class CustomPasswordChangeSerializer(PasswordChangeSerializer):

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError(_('Invalid password'))
        return value

    def save(self):
        self.user.require_change_password = False
        super().save()

class GroupSerializer(CoreModelSerializer):
    permiss = serializers.JSONField(required=False)
    user = serializers.PrimaryKeyRelatedField(source='user_set', queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        permissions = validated_data.pop('permiss', {})
        lstPermisCodes = []
        for perlable, val in permissions.items():
            if val:
                lstPermisCodes.append(int(perlable[5:]))
        lstPermission = Permission.objects.filter(code__in=lstPermisCodes).values_list('id', flat=True)
        validated_data.pop('permissions')
        lstUser = [item.id for item in validated_data.pop('user_set')]
        instance = Group(**validated_data)
        instance.save()
        instance.permissions.set(lstPermission)
        instance.user_set.set(lstUser)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permiss', {})
        lstPermisCodes = []
        for perlable, val in permissions.items():
            if val:
                lstPermisCodes.append(int(perlable[5:]))
        lstPermission = Permission.objects.filter(code__in=lstPermisCodes).values_list('id', flat=True)
        validated_data.pop('permissions')
        lstUser = [item.id for item in validated_data.pop('user_set')]
        instance.name = validated_data.get('name')
        instance.permissions.set(lstPermission)
        instance.user_set.set(lstUser)
        instance.save()
        return instance
