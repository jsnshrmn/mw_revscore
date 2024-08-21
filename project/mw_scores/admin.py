from django.contrib import admin

from .models import LiftwingResponse


class LiftwingResponseAdmin(admin.ModelAdmin):
    list_display = ("revision_create",)


admin.site.register(LiftwingResponse, LiftwingResponseAdmin)
