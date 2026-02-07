"""
Django Channels WebSocket Consumer for TradeIQ Chat
Routes messages to AI agents via DeepSeek function calling
"""
import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    DEMO_USER_ID = "d1000000-0000-0000-0000-000000000001"

    async def connect(self):
        query_params = parse_qs(self.scope.get("query_string", b"").decode())
        requested_user_id = query_params.get("user_id", [None])[0]
        self.user_id = requested_user_id or self.DEMO_USER_ID
        fallback_group_id = self.channel_name.replace(".", "_").replace("!", "_")
        self.room_group_name = f"chat_user_{requested_user_id or fallback_group_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send welcome message
        await self.send(text_data=json.dumps({
            "type": "system",
            "message": "Connected to TradeIQ AI. Ask me about markets, your trading patterns, or content creation.",
            "agent_type": "system",
            "user_id": self.user_id,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message") or data.get("content", "")
        agent_type = data.get("agent_type", "auto")
        user_id = data.get("user_id") or self.user_id

        if not message:
            return

        # Send "thinking" indicator
        await self.send(text_data=json.dumps({
            "type": "thinking",
            "message": "Analyzing...",
        }))

        # Route to agent system (run sync code in thread)
        result = await sync_to_async(self._route_message)(message, agent_type, user_id)

        # Send response
        await self.send(text_data=json.dumps({
            "type": "reply",
            "message": result.get("response", "I couldn't process that request."),
            "agent_type": result.get("source", "unknown"),
            "tools_used": result.get("tools_used", []),
        }))

    def _route_message(self, message, agent_type, user_id):
        """Synchronous routing to agent system."""
        from agents.router import route_query

        # Auto-detect agent type
        if agent_type == "auto":
            msg_lower = message.lower()
            if any(w in msg_lower for w in ["pattern", "behavior", "nudge", "revenge", "overtrad", "habit", "streak", "discipline", "trading history", "my trades"]):
                agent_type = "behavior"
            elif any(w in msg_lower for w in ["post", "bluesky", "content", "thread", "persona", "publish", "social media"]):
                agent_type = "content"
            else:
                agent_type = "market"

        return route_query(
            query=message,
            agent_type=agent_type,
            user_id=user_id,
        )

    async def chat_message(self, event):
        """Handle messages from channel layer (e.g., behavioral nudges)."""
        message = event.get("message", {})
        await self.send(text_data=json.dumps(message))
