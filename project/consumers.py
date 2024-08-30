import django
from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer
import os
from mw_events.background import collect, score

channel_layer = get_channel_layer()


class BackgroundTaskConsumer(AsyncConsumer):
    async def score(self, message):
        try:
            await score()
        except:
            await channel_layer.send("background", {"type": "score"})

    async def collect(self, message):
        try:
            await collect()
        except:
            await channel_layer.send("background", {"type": "collect"})

    async def ingest(self, message):
        await channel_layer.send("background", {"type": "score"})
        await channel_layer.send("background", {"type": "collect"})
