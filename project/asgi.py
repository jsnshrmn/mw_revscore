"""
ASGI config for mw_revscore project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django_asgi = get_asgi_application()

from asyncio import get_event_loop
from channels.layers import get_channel_layer
from channels.routing import ChannelNameRouter, ProtocolTypeRouter
from consumers import BackgroundTaskConsumer

application = ProtocolTypeRouter(
    {
        # Django's ASGI application to handle traditional HTTP requests
        "http": django_asgi,
        # Channel router for other lifecycles
        "channel": ChannelNameRouter(
            {
                "background": BackgroundTaskConsumer.as_asgi(),
            }
        ),
    }
)

# request ingest start with the server
channel_layer = get_channel_layer()
loop = get_event_loop()
loop.run_until_complete(channel_layer.send("background", {"type": "ingest"}))
