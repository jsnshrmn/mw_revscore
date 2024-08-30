from aiohttp import ClientSession
from aiohttp_retry import RetryClient, ExponentialRetry
from asyncio import sleep
from django.apps import apps
from django.db import models
from django.utils.timezone import now

# This could be a reusable standalone eventstream data collector app.
# I've bundled in me_scores things to the model manager here
# which breaks the separation of concerns, but was a convient way to
# experiment with moving our ingest close to the orm.

# @TODO: move this to settings, or maybe a model to mimic wikilink.
#        for example, there could be a Jobs model that specified a wiki and a
#        select list of models.
model_names = ["revertrisk-language-agnostic", "revertrisk-multilingual"]


class RevisionCreateManager(models.Manager):
    def unscored(self):
        return self.scoreable().filter(liftwingresponse__isnull=True).order_by("rev_id")

    def scored(self):
        return (
            self.scoreable().filter(liftwingresponse__isnull=False).order_by("rev_id")
        )

    def scoreable(self):
        scoreable = self.filter(
            rev_parent_id__isnull=False,
            database__in=["enwiki"],
        )
        return scoreable

    async def score(self):
        url = "https://api.wikimedia.org"
        headers = {"User-Agent": "mw_revscore/dev (WMF Moderator Tools Test)"}
        session = ClientSession(url)
        retry_options = ExponentialRetry(attempts=0)
        client = RetryClient(
            client_session=session, raise_for_status=False, retry_options=retry_options
        )
        LiftwingResponse = apps.get_model("mw_scores", "LiftwingResponse")
        async for revision_create in self.unscored():
            lang = revision_create.database[:-4]
            for model in model_names:
                async with client.post(
                    "/service/lw/inference/v1/models/{}:predict".format(model),
                    json={"rev_id": revision_create.rev_id, "lang": lang},
                    headers=headers,
                ) as response:
                    requested = now()
                    data = await response.json()
                    try:
                        model_name = data["model_name"]
                    except KeyError:
                        model_name = model
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
                    await LiftwingResponse(
                        rev_id=revision_create.rev_id,
                        dt=revision_create.dt,
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
