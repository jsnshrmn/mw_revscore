from django.core.management.base import BaseCommand

import logging
import sys
from asyncio import run
from ...models import RevisionCreate

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "fetch and save scores for revisions in revision-create events"

    def handle(self, *args, **options):
        while True:
            run(RevisionCreate.objects.score())
