import django
from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer
import os
from mw_events.background import collect, score

channel_layer = get_channel_layer()

# This is where django channels actually fires our code;
# it effectively replaces django management commands as used in wikilink.


class BackgroundTaskConsumer(AsyncConsumer):
    # score events
    async def score(self, message):
        try:
            await score()
        except:
            await channel_layer.send("background", {"type": "score"})

    # collect events
    async def collect(self, message):
        try:
            await collect()
        except:
            await channel_layer.send("background", {"type": "collect"})

    # ingest is simply the top level job that calls the others
    async def ingest(self, message):
        await channel_layer.send("background", {"type": "score"})
        await channel_layer.send("background", {"type": "collect"})
