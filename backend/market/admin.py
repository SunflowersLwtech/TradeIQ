from django.contrib import admin
from .models import MarketInsight


@admin.register(MarketInsight)
class MarketInsightAdmin(admin.ModelAdmin):
    list_display = ("id", "instrument", "insight_type", "generated_at")
