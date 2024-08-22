from django.contrib import admin

from .models import RevisionCreate


class RevisionCreateAdmin(admin.ModelAdmin):
    list_display = ("rev_id", "dt", "database", "page_title", "rev_sha1")


admin.site.register(RevisionCreate, RevisionCreateAdmin)
