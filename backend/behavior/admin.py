from django.contrib import admin
from .models import UserProfile, Trade, BehavioralMetric


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "created_at")


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "instrument", "pnl", "is_mock", "opened_at")


@admin.register(BehavioralMetric)
class BehavioralMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "trading_date", "total_trades", "emotional_state")
