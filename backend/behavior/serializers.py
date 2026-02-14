from rest_framework import serializers
from .models import UserProfile, Trade, BehavioralMetric


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = "__all__"


class BehavioralMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehavioralMetric
        fields = "__all__"
