from django.contrib import admin
from .models import AIPersona, SocialPost


@admin.register(AIPersona)
class AIPersonaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "personality_type", "is_primary")


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ("id", "persona", "platform", "status", "created_at")
