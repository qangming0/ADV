#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.urls import path
from . import views
from config.system.models import System


urlpatterns = [
    path('devices/', views.DeviceList.as_view()),
    path('devices/<int:pk>/', views.DeviceDetail.as_view()),
    path('devices/choices/', views.DeviceExt.list),

    path('device/register/', views.DeviceManagement.register),
    path('device/getid/', views.DeviceManagement.getId),
    path('device/getinfo/', views.DeviceManagement.getInfo),
    path('devices/active/<int:pk>/', views.DeviceManagement.active),
    path('devices/system/advertis', views.AdvertisDeviceList.as_view()),

    path('devices/synchronizing/', views.SynchrozingDevice.as_view()),

    path('devices/lines/', views.DeviceLineList.as_view()),
    path('devices/lines/<int:pk>/', views.DeviceLineDetail.as_view()),
    # List media object
    path('devices/<int:pk>/media/', views.DeviceAdvMedia.as_view()),

]