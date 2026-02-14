# TradeIQ Celery config (Design Doc Section 14)
from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tradeiq.settings")
app = Celery("tradeiq")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
