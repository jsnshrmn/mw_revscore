from django.contrib import admin

from .models import RevertRiskLaResponse, RevertRiskMlResponse


class RevertRiskLaResponseAdmin(admin.ModelAdmin):
    list_display = (
        "revision_create__rev_id",
        "elapsed",
        "status_code",
        "true_probability",
    )


admin.site.register(RevertRiskLaResponse, RevertRiskLaResponseAdmin)


class RevertRiskMlResponseAdmin(admin.ModelAdmin):
    list_display = (
        "revision_create__rev_id",
        "elapsed",
        "status_code",
        "true_probability",
    )


admin.site.register(RevertRiskMlResponse, RevertRiskMlResponseAdmin)
