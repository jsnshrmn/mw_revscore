from django.contrib import admin

from .models import LiftwingResponse


class LiftwingResponseAdmin(admin.ModelAdmin):
    list_display = ("revision_create__rev_id", "created", "revision_create__dt", "revision_create__database", "status_code", "true_probability")


admin.site.register(LiftwingResponse, LiftwingResponseAdmin)
