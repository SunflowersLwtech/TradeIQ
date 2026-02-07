from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIPersonaViewSet, SocialPostViewSet, PublishToBlueskyView

router = DefaultRouter()
router.register(r"personas", AIPersonaViewSet, basename="aipersona")
router.register(r"posts", SocialPostViewSet, basename="socialpost")
urlpatterns = [
    path("", include(router.urls)),
    path("publish-bluesky/", PublishToBlueskyView.as_view(), name="publish-bluesky"),
]
