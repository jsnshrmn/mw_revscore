"""
ASGI config for mw_revscore project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from asyncio import run
from channels.layers import get_channel_layer
from channels.routing import ChannelNameRouter, ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from consumers import BackgroundTaskConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = ProtocolTypeRouter(
    {
        # Django's ASGI application to handle traditional HTTP requests
        "http": get_asgi_application(),
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
run(channel_layer.send("background", {"type": "ingest"}))
