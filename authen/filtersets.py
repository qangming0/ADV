from core.filterset import CoreFilterSet, NumberInFilter, IdInFilter
from authen.models import User


class UserFilter(CoreFilterSet):
    id__in = NumberInFilter(field_name='id', lookup_expr='in')
    id__notin = NumberInFilter(field_name='id', method='field_notin_filter')

    class Meta:
        model = User
        fields = {
            'last_name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'is_staff': ['exact'],
        }