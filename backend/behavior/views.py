from rest_framework import viewsets
from .models import UserProfile, Trade, BehavioralMetric
from .serializers import UserProfileSerializer, TradeSerializer, BehavioralMetricSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer


class BehavioralMetricViewSet(viewsets.ModelViewSet):
    queryset = BehavioralMetric.objects.all()
    serializer_class = BehavioralMetricSerializer
