#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import path
from . import views

urlpatterns = [
    path('positioncontrol', views.PositionViewList.as_view()),
    path('positioncontrol/adv/', views.AdvertisePositionList.as_view()),
    path('positioncontrol/<int:pk>', views.PositionViewDetail.as_view()),
]
