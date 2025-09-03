#!/usr/bin/python
# -*- coding: utf8 -*-


from django.urls import path
from . import views

urlpatterns = [
    path('systems/', views.SystemList.getList),
    path('systemconfig/', views.SystemConfig.AdvConfig),
]