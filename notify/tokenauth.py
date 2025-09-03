import jwt

from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

from django.db import close_old_connections
from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import AnonymousUser

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

class TokenAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):

        try:
            token_name, token_key = scope['query_string'].decode('utf-8').split('=')
            if token_name == 'token':
                payload = jwt_decode_handler(token_key)
                user = self.authenticate_credentials(payload)
                # token = Token.objects.get(key=token_key)
                scope['user'] = user
        # except Token.DoesNotExist:
        except Exception as ex:
            scope['user'] = AnonymousUser()

        close_old_connections()

        return self.inner(dict(scope, user=scope['user']))

    def authenticate_credentials(self, payload):
        """
                Returns an active user that matches the payload's user id and email.
                """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
            # user = User.objects.get(pk=payload.get('user_id'))
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user

# TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))