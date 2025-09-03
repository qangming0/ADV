import json
import logging
from django.db.models.signals import m2m_changed, post_save, pre_delete, post_delete, pre_save
from django.dispatch import receiver
from utils.jsonmsg import JsonMessage
logger = logging.getLogger('django')

