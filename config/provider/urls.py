#!/usr/bin/python
# -*- coding: utf8 -*-


from django.urls import path
from . import views

urlpatterns = [
    path('providers/', views.ProviderList.as_view()),
    path('providers/<int:pk>/', views.ProviderDetail.as_view()),
]