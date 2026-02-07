# Django Channels WebSocket consumer (Design Doc Section 14)
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # TODO: route to agents.router.route_query and stream response
        await self.send(text_data=json.dumps({"type": "reply", "text": "Echo: " + data.get("message", "")}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
