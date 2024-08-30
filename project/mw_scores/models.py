from django.db import models
from django.utils.functional import cached_property
from mw_events.models import RevisionCreate


class LiftwingResponse(models.Model):
    class Meta:
        app_label = "mw_scores"
        indexes = [
            models.Index(
                fields=[
                    "rev_id",
                ]
            ),
            models.Index(
                fields=[
                    "dt",
                ]
            ),
            models.Index(
                fields=[
                    "model_name",
                ]
            ),
        ]

    def json_default():
        """
        JSONField requires a callable wrapper for default value
        """
        return {}

    revision_create = models.ForeignKey(
        RevisionCreate, on_delete=models.CASCADE, related_name="liftwingresponse"
    )
    # denormalized from revision_create
    rev_id = models.PositiveBigIntegerField(null=True)
    # denormalized from revision_create
    dt = models.DateTimeField(null=True)
    model_version = models.PositiveSmallIntegerField(null=True)
    # Should probably be enum for efficiency
    model_name = models.CharField(max_length=128, null=True)
    prediction = models.BooleanField(null=True)
    true_probability = models.DecimalField(max_digits=17, decimal_places=17, null=True)
    status_code = models.PositiveSmallIntegerField(null=True)
    error_detail = models.CharField(max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True)
    requested = models.DateTimeField()
    elapsed = models.GeneratedField(
        expression=models.F("created") - models.F("requested"),
        output_field=models.DurationField(),
        db_persist=True,
    )
