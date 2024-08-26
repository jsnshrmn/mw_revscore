from django.views.generic import ListView
from .models import LiftwingResponse


class Home(ListView):
    context_object_name = "liftwingresponse"

    def get_queryset(self):
        return LiftwingResponse.objects.all()
