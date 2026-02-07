from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AIPersona, SocialPost
from .serializers import AIPersonaSerializer, SocialPostSerializer
class AIPersonaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIPersona.objects.all()
    serializer_class = AIPersonaSerializer


class SocialPostViewSet(viewsets.ModelViewSet):
    queryset = SocialPost.objects.all()
    serializer_class = SocialPostSerializer


class PublishToBlueskyView(APIView):
    """Appendix B - POST content to Bluesky (single or thread)."""

    def post(self, request):
        content = request.data.get("content")
        post_type = request.data.get("type", "single")

        if not content:
            return Response({"error": "content is required"}, status=400)
        try:
            from .bluesky import BlueskyPublisher
        except ImportError:
            return Response({"error": "atproto not installed"}, status=503)
        publisher = BlueskyPublisher()

        if post_type == "thread":
            results = publisher.post_thread(content)
        else:
            results = publisher.post(content)

        return Response({
            "status": "published",
            "platform": "bluesky",
            "results": results,
        })
