from aiohttp import ClientSession
from django.apps import apps
from django.db import models


class RevisionCreateManager(models.Manager):
    async def score(self):
        url = "https://api.wikimedia.org/service/lw/inference/v1/models/revertrisk-language-agnostic:predict"
        headers = {"User-Agent": "mw_revscore/dev (WMF Moderator Tools Test)"}
        session = ClientSession()
        LiftwingResponse = apps.get_model("mw_scores", "LiftwingResponse")
        async for revision_create in self.filter(
            liftwingresponse__isnull=True, database__in=["enwiki"]
        ):
            if not revision_create.database.endswith("wiki"):
                continue
            lang = revision_create.database[:-4]
            async with session.post(
                url,
                json={"rev_id": revision_create.rev_id, "lang": lang},
                headers=headers,
            ) as response:
                data = await response.json()
                try:
                    model_name = data["model_name"]
                except KeyError:
                    model_name = None
                try:
                    model_version = data["model_version"]
                except KeyError:
                    model_version = None
                try:
                    prediction = data["output"]["prediction"]
                except KeyError:
                    prediction = None
                try:
                    true_probability = data["output"]["probabilities"]["true"]
                except KeyError:
                    true_probability = None

                liftwing_response = LiftwingResponse(
                    model_name=model_name,
                    model_version=model_version,
                    revision_create=revision_create,
                    prediction=prediction,
                    true_probability=true_probability,
                    status_code=response.status,
                )
                await liftwing_response.asave()
        await session.close()


class RevisionCreate(models.Model):
    class Meta:
        app_label = "mw_events"
        get_latest_by = "dt"
        indexes = [
            models.Index(
                fields=[
                    "dt",
                ]
            ),
        ]

    def json_default():
        """
        JSONField requires a callable wrapper for default value
        """
        return {}

    objects = RevisionCreateManager()
    schema = models.CharField(max_length=128)
    comment = models.CharField(null=True, max_length=128)
    database = models.CharField(max_length=32)
    dt = models.DateTimeField()
    meta = models.JSONField()
    page_id = models.PositiveBigIntegerField()
    page_is_redirect = models.BooleanField()
    page_namespace = models.PositiveIntegerField()
    page_title = models.CharField(max_length=128)
    performer = models.JSONField()
    rev_content_changed = models.BooleanField(default=False)
    rev_content_format = models.CharField(null=True, max_length=128)
    rev_content_model = models.CharField(null=True, max_length=128)
    rev_id = models.PositiveBigIntegerField(primary_key=True)
    rev_is_revert = models.BooleanField(default=False)
    rev_len = models.BigIntegerField(null=True)
    rev_minor_edit = models.BooleanField(default=False)
    rev_parent_id = models.PositiveBigIntegerField(null=True)
    rev_revert_details = models.JSONField(default=json_default)
    rev_sha1 = models.CharField(null=True, max_length=128)
    rev_slots = models.JSONField(default=json_default)
    rev_timestamp = models.DateTimeField()
