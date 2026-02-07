# Design Document Section 7 - users, trades, behavioral_metrics
from django.db import models
import uuid


class UserProfile(models.Model):
    """App user profile (matches Supabase users table)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    watchlist = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email


class Trade(models.Model):
    """User trade (instrument, pnl, duration, is_mock)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="trades", db_column="user_id"
    )
    instrument = models.CharField(max_length=64)
    direction = models.CharField(max_length=16, blank=True)
    entry_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    exit_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    pnl = models.DecimalField(max_digits=20, decimal_places=8)
    duration_seconds = models.IntegerField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_mock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "trades"
        ordering = ["-opened_at", "-created_at"]

    def __str__(self):
        return f"{self.instrument} {self.pnl}"


class BehavioralMetric(models.Model):
    """Per-day behavioral metrics; pattern_flags e.g. revenge_trading."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="behavioral_metrics", db_column="user_id"
    )
    trading_date = models.DateField()
    total_trades = models.IntegerField(default=0)
    win_count = models.IntegerField(default=0)
    loss_count = models.IntegerField(default=0)
    avg_hold_time = models.FloatField(null=True, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    emotional_state = models.CharField(max_length=64, blank=True)
    pattern_flags = models.JSONField(default=dict, blank=True)  # e.g. {"revenge_trading": true}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavioral_metrics"
        ordering = ["-trading_date"]
        unique_together = [["user", "trading_date"]]

    def __str__(self):
        return f"{self.user_id} {self.trading_date}"
