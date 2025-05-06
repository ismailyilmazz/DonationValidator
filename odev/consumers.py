from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "global_chat"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):        
        data = json.loads(text_data)
        key = data.get("key")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_keypress",
                "key": key
            }
        )

    async def broadcast_keypress(self, event):
        print(">> GRUPTAKİ BİRİNE GÖNDERİLİYOR")
        key = event["key"]
        await self.send(text_data=json.dumps({
            "type": "keypress",
            "key": key,
            "message": f"{key} tuşuna basıldı"
        }))
