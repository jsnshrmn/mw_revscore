from django.contrib import admin

from .models import LiftwingResponse


class LiftwingResponseAdmin(admin.ModelAdmin):
    list_display = (
        "revision_create__rev_id",
        "model_name",
        "elapsed",
        "status_code",
        "true_probability",
    )


admin.site.register(LiftwingResponse, LiftwingResponseAdmin)
