import sys
from django.apps import AppConfig
from .permission_modules import SYSTEM_PARAM_KEY, version, modules


class AuthenConfig(AppConfig):
    name = 'authen'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True

        from .models import Permission
        from config.common.models import SystemParam

        permission_version = SystemParam.objects.filter(spm_key=SYSTEM_PARAM_KEY).first()
        if permission_version:
            if permission_version.spm_value >= version:
                # print('Permissions: file version less than or equal current version. Do not update')
                return

        file_codes = []
        list_permissions = []

        for module in modules:
            if 'children' in module:
                for submodule in module['children']:
                    if 'permissions' in submodule:
                        for permission in submodule['permissions']:
                            # permission.pop('title')
                            list_permissions.append(permission)
                            file_codes.append(permission['code'])

            if 'permissions' in module:
                for permission in module['permissions']:
                    # permission.pop('title')
                    list_permissions.append(permission)
                    file_codes.append(permission['code'])

        Permission.objects.all().exclude(code__in=file_codes).delete()

        for permission in list_permissions:
            current_permission = Permission.objects.filter(code=permission['code']).first()
            if current_permission is not None:
                if current_permission.name != permission['name'] \
                        or current_permission.title != permission['title']:
                    current_permission.name = permission['name']
                    current_permission.save()
            else:
                Permission.objects.create(**permission)

        if not permission_version:
            permission_version = SystemParam(spm_key=SYSTEM_PARAM_KEY, spm_value=version)
        else:
            permission_version.spm_value = version
        permission_version.save()
        print('Loaded new permissions from file')