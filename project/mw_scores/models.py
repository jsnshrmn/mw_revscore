from django.db import models
from mw_events.models import RevisionCreate


class LiftwingResponse(models.Model):
    class Meta:
        app_label = "mw_scores"

    def json_default():
        """
        JSONField requires a callable wrapper for default value
        """
        return {}

    model_name = models.CharField(max_length=128, null=True)
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
