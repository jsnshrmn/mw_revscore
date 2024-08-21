from django.contrib import admin

from .models import RevisionCreate


class RevisionCreateAdmin(admin.ModelAdmin):
    list_display = ("database", "page_title", "rev_id", "rev_sha1")


admin.site.register(RevisionCreate, RevisionCreateAdmin)
