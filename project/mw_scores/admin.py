from django.contrib import admin

from .models import RevertRiskLaResponse, RevertRiskMlResponse


class RevertRiskLaResponseAdmin(admin.ModelAdmin):
    def elapsed_time(self, obj):
        elapsed = obj.created - obj.requested
        return elapsed

    list_display = (
        "revision_create__rev_id",
        "elapsed_time",
        "status_code",
        "true_probability",
    )


admin.site.register(RevertRiskLaResponse, RevertRiskLaResponseAdmin)


class RevertRiskMlResponseAdmin(admin.ModelAdmin):
    def elapsed_time(self, obj):
        elapsed = obj.created - obj.requested
        return elapsed

    list_display = (
        "revision_create__rev_id",
        "elapsed_time",
        "status_code",
        "true_probability",
    )


admin.site.register(RevertRiskMlResponse, RevertRiskMlResponseAdmin)
