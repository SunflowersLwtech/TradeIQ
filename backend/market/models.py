# Design Document Section 7 - Market app models
# MARKET_INSIGHTS from ERD; trades live in behavior app
from django.db import models
import uuid


class MarketInsight(models.Model):
    """Stored market insights (instrument, type, content, sentiment)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instrument = models.CharField(max_length=64)
    insight_type = models.CharField(max_length=64)
    content = models.TextField()
    sentiment_score = models.FloatField(null=True, blank=True)
    sources = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "market_insights"
        ordering = ["-generated_at"]
