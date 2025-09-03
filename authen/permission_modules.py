from django.utils.translation import gettext_lazy as _
from .permissions import *

version = '0.0.7'
SYSTEM_PARAM_KEY = 'PERMISSION_VERSION'

modules = [
    {
        'name': 'Manage devices',
        'title': _('Manage devices'),
        'permissions': [
            {
                'code': CREATE_DEVICE,
                'name': 'Create',
                'title': _('Create')
            },
            {
                'code': VIEW_DEVICE,
                'name': 'View',
                'title': _('View')
            },
            {
                'code': EDIT_DEVICE,
                'name': 'Edit',
                'title': _('Edit')
            },
            {
                'code': DELETE_DEVICE,
                'name': 'Delete',
                'title': _('Delete')
            }
        ]
    },
    {
        'name': 'Manage building',
        'title': _('Manage building'),
        'children': [
            {
                'name': 'Building',
                'title': _('Building'),
                'permissions': [
                    {
                        'code': CREATE_BUILDING,
                        'name': 'Create',
                        'title': _('Create')
                    },
                    {
                        'code': VIEW_BUILDING,
                        'name': 'View',
                        'title': _('View')
                    },
                    {
                        'code': EDIT_BUILDING,
                        'name': 'Edit',
                        'title': _('Edit')
                    },
                    {
                        'code': DELETE_BUILDING,
                        'name': 'Delete',
                        'title': _('Delete')
                    },
                    {
                        'code': SYNC_BUILDING,
                        'name': 'Synchronize',
                        'title': _('Synchronize')
                    }
                ]
            },
            {
                'name': 'Manage floors',
                'title': _('Floors'),
                'permissions': [
                    {
                        'code': CREATE_FLOOR,
                        'name': 'Create',
                        'title': _('Create')
                    },
                    {
                        'code': VIEW_FLOOR,
                        'name': 'View',
                        'title': _('View')
                    },
                    {
                        'code': EDIT_FLOOR,
                        'name': 'Edit',
                        'title': _('Edit')
                    },
                    {
                        'code': DELETE_FLOOR,
                        'name': 'Delete',
                        'title': _('Delete')
                    }
                ]
            },
            {
                'name': 'Manage door',
                'title': _('Doors'),
                'permissions': [
                    {
                        'code': CREATE_DOOR,
                        'name': 'Create',
                        'title': _('Create')
                    },
                    {
                        'code': VIEW_DOOR,
                        'name': 'View',
                        'title': _('View')
                    },
                    {
                        'code': EDIT_DOOR,
                        'name': 'Edit',
                        'title': _('Edit')
                    },
                    {
                        'code': DELETE_DOOR,
                        'name': 'Delete',
                        'title': _('Delete')
                    }
                ]
            },
            {
                'name': 'Manage area',
                'title': _('Zones'),
                'permissions': [
                    {
                        'code': CREATE_ZONE,
                        'name': 'Create',
                        'title': _('Create')
                    },
                    {
                        'code': VIEW_ZONE,
                        'name': 'View',
                        'title': _('View')
                    },
                    {
                        'code': EDIT_ZONE,
                        'name': 'Edit',
                        'title': _('Edit')
                    },
                    {
                        'code': DELETE_ZONE,
                        'name': 'Delete',
                        'title': _('Delete')
                    }
                ]
            }
        ]
    },
    {
        'name': 'Manage Config',
        'title': _('Config'),
        'permissions': [
            {
                'code': CONFIG_VIEW,
                'name': 'View config',
                'title': _('View config')
            },
            {
                'code': CONFIG_SHIFT_PERIOD,
                'name': 'config shift period',
                'title': _('config shift period')
            },
            {
                'code': CONFIG_SHIFT_TIME,
                'name': 'config shift time',
                'title': _('config shift time')
            },
            {
                'code': CONFIG_PROVIDER,
                'name': 'config provider',
                'title': _('config provider')
            },
            {
                'code': CONFIG_FACTOR,
                'name': 'config factor',
                'title': _('config factor')
            }
        ]
    },
    {
        'name': 'Manage media',
        'title': _('Manage media'),
        'permissions': [
            {
                'code': MEDIA_CREATE,
                'name': 'Create',
                'title': _('Create')
            },
            {
                'code': MEDIA_VIEW,
                'name': 'View',
                'title': _('View')
            },
            {
                'code': MEDIA_EDIT,
                'name': 'Edit',
                'title': _('Edit')
            },
            {
                'code': MEDIA_DELETE,
                'name': 'Delete',
                'title': _('Delete')
            }
        ]
    },
    {
        'name': 'Manage Advertise',
        'title': _('Manage Advertise'),
        'children': [
            {
                'name': 'Schedule',
                'title': _('Schedule'),
                'permissions': [
                    {
                        'code': ADV_SCHEDULE_VIEW,
                        'name': 'View',
                        'title': _('View')
                    },
                    {
                        'code': ADV_SCHEDULE_CREATE,
                        'name': 'Create',
                        'title': _('Create')
                    },
                    {
                        'code': ADV_SCHEDULE_EDIT,
                        'name': 'Edit',
                        'title': _('Edit')
                    },
                    {
                        'code': ADV_SCHEDULE_DELETE,
                        'name': 'Delete',
                        'title': _('Delete')
                    }
                ]
            },
            {
                'name': 'Position control',
                'title': _('Position'),
                'permissions': [
                    {
                        'code': ADV_POSITION_VIEW,
                        'name': 'View',
                        'title': _('View')
                    },
                    {
                        'code': ADV_POSITION_CONTROL,
                        'name': 'Control',
                        'title': _('Control')
                    }
                ]
            },
        ],
        'permissions': [
            {
                'code': ADV_NOTICE,
                'name': 'Adv notice',
                'title': _('adv notice')
            }
        ]
    }
]
