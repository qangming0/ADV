from django.contrib import admin
from .models import Building, Floor, Zone, Door
# Register your models here.

admin.site.register((Building, Floor, Zone, Door, ))