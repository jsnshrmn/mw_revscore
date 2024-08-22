from django.core.management.base import BaseCommand

import asyncio
import aiohttp
from aiosseclient import aiosseclient
import hashlib
from datetime import datetime
import json
import logging
import sys
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from ...models import RevisionCreate

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Monitors revision-create for events"

    def add_arguments(self, parser):
        parser.add_argument(
            "--historical",
            action="store_true",
            help="Parse event stream from last logged event",
        )

        parser.add_argument(
            "--test",
            nargs=1,
            help="Test the command without having to access the stream. Passes a json event",
        )

    def handle(self, *args, **options):
        base_stream_url = "https://stream.wikimedia.org/v2/stream/revision-create"

        if options["test"]:
            event_data = options["test"]
            # Since we are not testing the EventStream functionality, we finish
            # execution here
            sys.exit(0)

        # Every time this script is started, find the latest entry in the
        # database, and start the eventstream from there. This ensures that in
        # the event of any downtime, we always maintain 100% data coverage (up
        # to the ~7 days that the EventStream historical data is kept anyway).
        if options["historical"]:
            all_events = RevisionCreate.objects.all()
            if all_events.exists():
                latest_datetime = all_events.latest().dt
                latest_date_formatted = latest_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

                url = base_stream_url + "?since={date}".format(
                    date=latest_date_formatted
                )
            else:
                url = base_stream_url
        else:
            url = base_stream_url

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        loop.run_until_complete(self._process_events(url))

    async def _process_events(self, url):
        async for event in aiosseclient(url):
            if event.event == "message":
                try:
                    event_data = json.loads(event.data)
                except ValueError:
                    continue

                await self._save_event(event_data)

    async def _save_event(self, event_data):
        if "Z" in event_data["meta"]["dt"]:
            string_format = "%Y-%m-%dT%H:%M:%SZ"
        else:
            string_format = "%Y-%m-%dT%H:%M:%S+00:00"
        # May or may not have milliseconds
        try:
            datetime_object = datetime.strptime(event_data["meta"]["dt"], string_format)
        except ValueError:
            string_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            datetime_object = datetime.strptime(event_data["meta"]["dt"], string_format)
        try:
            performer = event_data["performer"]
        except KeyError:
            # Per https://phabricator.wikimedia.org/T216726, edits to Flow
            # pages have no performer, so we'll abandon logging this event
            # rather than worry about how to present such an edit.
            logger.info(
                "Skipped event {event_id} due to no performer".format(
                    event_id=event_data["meta"]["id"]
                )
            )
            return

        if event_data["database"] not in ["enwiki"]:
            return

        # Other potentially null fields
        try:
            comment = event_data["comment"]
        except KeyError:
            comment = None
        try:
            rev_content_changed = event_data["rev_content_changed"]
        except KeyError:
            rev_content_changed = False
        try:
            rev_content_format = event_data["rev_content_format"]
        except KeyError:
            rev_content_format = None
        try:
            rev_content_model = event_data["rev_content_model"]
        except KeyError:
            rev_content_model = None
        try:
            rev_is_revert = event_data["rev_is_revert"]
        except KeyError:
            rev_is_revert = False
        try:
            rev_len = event_data["rev_len"]
        except KeyError:
            rev_len = None
        try:
            rev_minor_edit = event_data["rev_minor_edit"]
        except KeyError:
            rev_minor_edit = False
        try:
            rev_parent_id = event_data["rev_parent_id"]
        except KeyError:
            rev_parent_id = None
        try:
            rev_revert_details = event_data["rev_revert_details"]
        except KeyError:
            rev_revert_details = {}
        try:
            rev_sha1 = event_data["rev_sha1"]
        except KeyError:
            rev_sha1 = None
        try:
            rev_slots = event_data["rev_slots"]
        except KeyError:
            rev_slots = {}

        new_event = RevisionCreate(
            schema=event_data["$schema"],
            comment=comment,
            database=event_data["database"],
            dt=datetime_object.replace(tzinfo=ZoneInfo("UTC")),
            meta=event_data["meta"],
            page_id=event_data["page_id"],
            page_is_redirect=event_data["page_is_redirect"],
            page_namespace=event_data["page_namespace"],
            page_title=event_data["page_title"],
            performer=performer,
            rev_content_changed=rev_content_changed,
            rev_content_format=rev_content_format,
            rev_content_model=rev_content_model,
            rev_id=event_data["rev_id"],
            rev_is_revert=rev_is_revert,
            rev_len=rev_len,
            rev_minor_edit=rev_minor_edit,
            rev_parent_id=rev_parent_id,
            rev_revert_details=rev_revert_details,
            rev_sha1=rev_sha1,
            rev_slots=rev_slots,
            rev_timestamp=event_data["rev_timestamp"],
        )
        await new_event.asave()
