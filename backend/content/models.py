# Design Document Section 7 - ai_personas, social_posts
from django.db import models
import uuid


class AIPersona(models.Model):
    """Calm Analyst, Data Nerd, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    personality_type = models.CharField(max_length=64, blank=True)
    system_prompt = models.TextField(blank=True)
    voice_config = models.JSONField(default=dict, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_personas"
        ordering = ["-is_primary", "name"]

    def __str__(self):
        return self.name


class SocialPost(models.Model):
    """Platform default bluesky; content; status."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    persona = models.ForeignKey(
        AIPersona, on_delete=models.CASCADE, related_name="social_posts", db_column="persona_id"
    )
    platform = models.CharField(max_length=32, default="bluesky")
    content = models.TextField()
    status = models.CharField(max_length=32, default="draft")  # draft, published, scheduled
    engagement_metrics = models.JSONField(default=dict, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.platform} {self.status}"
