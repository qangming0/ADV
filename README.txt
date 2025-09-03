1. create python3 virtual environment
	python.exe -m venv ..\src_v2\server\tornado\virtualenv


2.============= CLUSTER =================
#Django cluster

https://devcenter.heroku.com/articles/django-memcache
https://django-q.readthedocs.io/en/latest/cluster.html
https://github.com/perlbal/Perlbal


#System Setup
#First, download the dependencies:

brew install memcached or sudo apt-get install memcached

pip install python-memcached

# Start:
brew services start memcached or sudo service memcached start

# Django Setup
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


# Do the Thing
# Views
from django.core.cache import cache
def my_view(request):
    cache_key = 'my_unique_key'  # needs to be unique
    cache_time = 86400  # time in seconds for cache to be valid
    data = cache.get(cache_key)  # returns None if no key-value pair
    if not data:
        my_service = Service()
        data = service.get_data()

    cache.set(cache_key, data, cache_time)


return JsonResponse(data, safe=False)

3. =============== TURNING ========================
https://djangobook.com/scaling-django/

4. =============== BUILD LOCALE FILE ==============
# Note: install GNU gettext tools for os that you uses
cd root/app/module
-- generate django.po
mkdir locale
django-admin makemessages -l vi [-e txt]
# django-admin makemessages -a
-- generate django.mo
django-admin compilemessages