import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ProtocolConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope.get("user") or not self.scope["user"].is_authenticated:
            await self.close(code=4401)
            return

        self.group_name = "protocols"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept(subprotocol="jwt")

    async def disconnect(self, close_code):
        if not hasattr(self, "group_name"):
            return

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def protocol_status_changed(self, event):
        await self.send(text_data=json.dumps({
            "type": "protocol_status_changed",
            "protocol": event["protocol"],
        }))