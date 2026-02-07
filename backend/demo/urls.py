from django.urls import path
from .views import LoadScenarioView

urlpatterns = [
    path("load-scenario/", LoadScenarioView.as_view(), name="load-scenario"),
]
