from rest_framework import serializers
from .models import MarketInsight


class MarketInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketInsight
        fields = "__all__"
