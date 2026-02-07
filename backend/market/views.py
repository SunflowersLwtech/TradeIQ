from rest_framework import viewsets
from .models import MarketInsight
from .serializers import MarketInsightSerializer


class MarketInsightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MarketInsight.objects.all()
    serializer_class = MarketInsightSerializer
