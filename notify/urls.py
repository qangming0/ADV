# chat/routing.py
from django.conf.urls import url

from . import consumers

urlpatterns = [
    url(r'^notify$', consumers.ChatConsumer),
]