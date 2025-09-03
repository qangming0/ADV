from channels.auth import AuthMiddlewareStack
from notify.tokenauth import TokenAuthMiddleware
# from notify.tokenauth import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import notify.urls

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    # 'websocket': AuthMiddlewareStack(
    'websocket': TokenAuthMiddleware(
        URLRouter(
            notify.urls.urlpatterns
        )
    ),
})