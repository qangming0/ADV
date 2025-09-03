#!/usr/bin/python
# -*- coding: utf8 -*-

from django.urls import path
from . import views

urlpatterns = [
    path('rest-auth/registration/', views.CreateUserView.as_view()),

    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('user/me', views.UserExt.getRequestUser),
    path('groups/', views.GroupList.as_view()),
    path('groups/<int:pk>/', views.GroupDetail.as_view()),
    path('groups/full/', views.GroupFullList.as_view()),
    path('permissions/', views.PermissionList.as_view()),
    path('permissions/<int:pk>/', views.PermissionDetail.as_view()),
    path('permissions_structure/', views.PermissionStructure.as_view()),
]
