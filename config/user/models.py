from django.db import models
from core.models import CoreModel
from authen.models import User


class UserConfig(CoreModel):
    uco_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='configs')
    uco_key = models.CharField(max_length=50)
    uco_value = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (("uco_user", "uco_key",),)

    def __str__(self):
        return '{} - {}'.format(self.uco_user.username, self.uco_key)
