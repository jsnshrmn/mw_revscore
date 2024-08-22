from threading import Thread
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        help = "service command for simultaneously collecting revsions and scores"

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
