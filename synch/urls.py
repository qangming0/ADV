#!/usr/bin/python
# -*- coding: utf8 -*-


from django.urls import path, include
from synch.modules.adv import adv_view

urlpatterns = [
    path('synchronize/', include([

        # for advantise
        path('adv/schedule/', adv_view.AdvSync.as_view()),
    ])),
]