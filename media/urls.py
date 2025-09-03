#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import path
from . import views

urlpatterns = [
    path('uploadfile', views.UploadMediaFile.upload),

    path('media/', views.MediaList.as_view()),
    path('media/<int:pk>/', views.MediaDetail.as_view()),
    path('folderpath/<int:pk>/', views.FolderPath.as_view()),
    path('importyoutube/', views.ImportYoutube.as_view()),
]
