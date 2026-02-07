from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarketInsightViewSet

router = DefaultRouter()
router.register(r"insights", MarketInsightViewSet, basename="market-insight")
urlpatterns = [path("", include(router.urls))]
