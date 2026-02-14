from rest_framework import serializers
from .models import AIPersona, SocialPost


class AIPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPersona
        fields = "__all__"


class SocialPostSerializer(serializers.ModelSerializer):
    persona_name = serializers.CharField(source="persona.name", read_only=True)

    class Meta:
        model = SocialPost
        fields = "__all__"
