from django.views.generic import ListView
from .models import LiftwingResponse


class Home(ListView):
    model = LiftwingResponse
    context_object_name = "liftwingresponse"
    paginate_by = 1000

