from threading import Thread
from django.core.management import call_command
from channels.consumer import AsyncConsumer


class BackgroundTaskConsumer(AsyncConsumer):
    async def ingest(self, message):
        score = Thread(target=call_command, args=("score",))
        collect = Thread(
            target=call_command,
            args=(
                "collect",
                "--historical",
            ),
        )

        score.start()
        collect.start()

        score.join()
        collect.join()
