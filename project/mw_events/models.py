from aiohttp import ClientSession
from asyncio import sleep
from django.apps import apps
from django.db import models
from django.utils.timezone import now


class RevisionCreateManager(models.Manager):
    def scored(self):
        return (
            self.scoreable()
            .filter(
                revertrisklaresponse__isnull=False, revertriskmlresponse__isnull=False
            )
            .select_related("revertrisklaresponse")
            .select_related("revertriskmlresponse")
            .order_by("rev_id")
        )

    def scoreable(self):
        scoreable = self.filter(
            rev_parent_id__isnull=False,
            database__in=["enwiki"],
        )
        return scoreable

    async def score(self):
        models = ["revertrisk-language-agnostic", "revertrisk-multilingual"]
        url = "https://api.wikimedia.org"
        headers = {"User-Agent": "mw_revscore/dev (WMF Moderator Tools Test)"}
        session = ClientSession(url)
        RevertRiskLaResponse = apps.get_model("mw_scores", "RevertRiskLaResponse")
        RevertRiskMlResponse = apps.get_model("mw_scores", "RevertRiskMlResponse")
        to_score = self.scoreable().filter(revertrisklaresponse__isnull=True)
        to_score.union(
            self.scoreable().filter(revertriskmlresponse__isnull=True)
        ).order_by("rev_id")
        async for revision_create in to_score:
            if not revision_create.database.endswith("wiki"):
                continue
            lang = revision_create.database[:-4]
            for model in models:
                async with session.post(
                    "/service/lw/inference/v1/models/{}:predict".format(model),
                    json={"rev_id": revision_create.rev_id, "lang": lang},
                    headers=headers,
                ) as response:
                    requested = now()
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
                    try:
                        error_detail = data["detail"]
                    except KeyError:
                        error_detail = None

                    if model == "revertrisk-language-agnostic":
                        await RevertRiskLaResponse(
                            model_name=model_name,
                            model_version=model_version,
                            revision_create=revision_create,
                            prediction=prediction,
                            true_probability=true_probability,
                            status_code=response.status,
                            requested=requested,
                        ).asave()
                    elif model == "revertrisk-multilingual":
                        await RevertRiskMlResponse(
                            model_name=model_name,
                            model_version=model_version,
                            revision_create=revision_create,
                            prediction=prediction,
                            true_probability=true_probability,
                            status_code=response.status,
                            requested=requested,
                        ).asave()
        await sleep(250)
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
