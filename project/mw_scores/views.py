from adrf.viewsets import ModelViewSet
from adrf.serializers import ModelSerializer
from django_filters import rest_framework as filters
from django.views.generic import TemplateView
from mw_scores.models import LiftwingResponse


class IndexView(TemplateView):
    template_name = "index.html"


# Serializers define the API representation.
class ScoreSerializer(ModelSerializer):
    class Meta:
        model = LiftwingResponse
        fields = [
            "rev_id",
            "dt",
            "model_name",
            "true_probability",
            "status_code",
            "elapsed",
        ]


class ScoreFilter(filters.FilterSet):
    dt = filters.DateTimeFromToRangeFilter(field_name="dt")
    rev_id = filters.NumericRangeFilter(field_name="rev_id")

    class Meta:
        model = LiftwingResponse
        fields = ["model_name"]


# ViewSets define the view behavior.
class ScoreViewSet(ModelViewSet):
    queryset = LiftwingResponse.objects.all()
    serializer_class = ScoreSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ScoreFilter
