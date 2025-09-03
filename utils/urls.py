import os
from django.contrib.sites.models import Site

def get_media_url(relaUrl):
    if relaUrl is None or relaUrl == '':
        return ''
    if relaUrl.startswith('/') == False:
        return relaUrl
    local_site = Site.objects.get_current()
    domain = os.getenv('MEDIA_DOMAIN', local_site.domain)
    return '{}{}'.format(domain, relaUrl)
