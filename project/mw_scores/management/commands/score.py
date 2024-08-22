from django.core.management.base import BaseCommand

import logging
import sys
from asyncio import run
from ...models import RevisionCreate

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "fetch and save scores for revisions in revision-create events"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            nargs=1,
            help="Test the command without having to access the stream. Passes a json event",
        )

    def handle(self, *args, **options):
        if options["test"]:
            event_data = options["test"]
            # Since we are not testing the EventStream functionality, we finish
            # execution here
            sys.exit(0)

        run(RevisionCreate.objects.score())
