# backend/content/bluesky.py - Appendix B
from django.conf import settings


class BlueskyPublisher:
    """Publish trading content to Bluesky via AT Protocol."""

    def __init__(self):
        from atproto import Client
        self.client = Client()
        self.client.login(
            settings.BLUESKY_HANDLE,
            settings.BLUESKY_APP_PASSWORD,
        )

    def post(self, text: str) -> dict:
        """Publish a single post (max 300 chars)."""
        response = self.client.send_post(text=text)
        return {
            "uri": response.uri,
            "cid": response.cid,
            "url": self._uri_to_url(response.uri),
        }

    def post_thread(self, posts: list) -> list:
        """Publish a thread (list of posts, each max 300 chars)."""
        results = []
        parent = None
        root = None

        for i, text in enumerate(posts):
            if parent is None:
                response = self.client.send_post(text=text)
                root = {"uri": response.uri, "cid": response.cid}
                parent = root
            else:
                response = self.client.send_post(
                    text=text,
                    reply_to={
                        "root": root,
                        "parent": parent,
                    },
                )
                parent = {"uri": response.uri, "cid": response.cid}

            results.append({
                "index": i,
                "uri": response.uri,
                "cid": response.cid,
                "url": self._uri_to_url(response.uri),
            })

        return results

    def _uri_to_url(self, uri: str) -> str:
        """Convert AT URI to web URL."""
        parts = uri.replace("at://", "").split("/")
        did = parts[0]
        post_id = parts[-1]
        return f"https://bsky.app/profile/{did}/post/{post_id}"
