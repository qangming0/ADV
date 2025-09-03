#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import path
from . import views

urlpatterns = [
    path('advschedules/', views.AdvScheduleList.as_view()),
    path('advschedules/<int:pk>/', views.AdvScheduleDetail.as_view()),
    path('advtype/choices/', views.AdvScheduleChoise.get),
    path('advplans/', views.AdvPlanList.as_view()),
    path('advplans/<int:pk>/', views.AdvPlanDetail.as_view()),
    path('advcontents/', views.AdvContentList.as_view()),
    path('advcontents/<int:pk>/', views.AdvContentDetail.as_view()),
    path('onenetcontents/', views.OneNetContentList.as_view()),
    path('onenetcontents/<int:pk>/', views.OneNetContentDetail.as_view()),
]
