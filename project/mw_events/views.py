from django.views.generic import ListView
from .models import RevisionCreate


class Home(ListView):
    context_object_name = "revisioncreate"

    def get_queryset(self):
        return RevisionCreate.objects.scored()
