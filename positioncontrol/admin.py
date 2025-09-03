from django.contrib import admin
from .models import PositionItem, PositionView
# Register your models here.

admin.site.register((PositionItem, PositionView, ))
