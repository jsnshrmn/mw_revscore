from django.db import models
from mw_events.models import RevisionCreate


class LiftwingResponse(models.Model):
    class Meta:
        app_label = "mw_scores"
        abstract = True

    def json_default():
        """
        JSONField requires a callable wrapper for default value
        """
        return {}

    model_version = models.PositiveSmallIntegerField(null=True)
    # should match RevisionCreate.database
    # wiki_db = models.CharField(max_length=32, null=True)
    revision_create = models.OneToOneField(
        RevisionCreate,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    prediction = models.BooleanField(null=True)
    true_probability = models.DecimalField(max_digits=17, decimal_places=17, null=True)
    status_code = models.PositiveSmallIntegerField(null=True)
    error_detail = models.CharField(max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True)
    requested = models.DateTimeField()


class RevertRiskLaResponse(LiftwingResponse):
    model_name = models.CharField(max_length=128, null=True)


class RevertRiskMlResponse(LiftwingResponse):
    model_name = models.CharField(max_length=128, null=True)
