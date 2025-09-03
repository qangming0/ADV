import sys
import types
import django.utils.translation as translation

# ugettext -> gettext
if not hasattr(translation, 'ugettext'):
    translation.ugettext = translation.gettext
if not hasattr(translation, 'ugettext_lazy'):
    translation.ugettext_lazy = translation.gettext_lazy

# Alias rest_auth -> dj_rest_auth
try:
    import dj_rest_auth
    sys.modules['rest_auth'] = dj_rest_auth

    # Tạo module rỗng trước khi import views/registration
    for mod in ['rest_auth.views', 'rest_auth.registration', 'rest_auth.registration.views']:
        if mod not in sys.modules:
            sys.modules[mod] = types.ModuleType(mod)

except ImportError:
    pass
