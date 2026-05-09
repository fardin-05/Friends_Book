from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

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
        sender = self.scope['user']
        msg_type = data.get('type', 'text')

        if msg_type == 'text':
            message = data.get('message', '')
            if not message.strip():
                return

            await self.save_message(sender, self.room_name, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'msg_type': 'text',
                    'message': message,
                    'sender': sender.full_name,
                    'sender_id': sender.id,
                }
            )

            # ✅ অন্য participant দের inbox notify করো
            await self.notify_inbox(sender, self.room_name, message, 'text')

        elif msg_type == 'file':
            file_url = data.get('file_url', '')
            file_type = data.get('file_type', 'file')
            file_name = data.get('file_name', 'file')
            message = data.get('message', '')

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'msg_type': 'file',
                    'file_url': file_url,
                    'file_type': file_type,
                    'file_name': file_name,
                    'message': message,
                    'sender': sender.full_name,
                    'sender_id': sender.id,
                }
            )

            # ✅ file পাঠালেও inbox notify করো
            await self.notify_inbox(sender, self.room_name, f'📎 {file_name}', 'file')

        elif msg_type == 'seen':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'msg_type': 'seen',
                    'seen_by': sender.id,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender, conversation_id, content):
        from .models import Conversation, Message
        try:
            convo = Conversation.objects.get(id=conversation_id)
            Message.objects.create(
                conversation=convo,
                sender=sender,
                content=content
            )
        except Conversation.DoesNotExist:
            pass

    # ✅ inbox notify helper
    @database_sync_to_async
    def get_other_participants(self, conversation_id, sender):
        from .models import Conversation
        try:
            convo = Conversation.objects.get(id=conversation_id)
            return list(convo.participants.exclude(id=sender.id).values_list('id', flat=True))
        except Conversation.DoesNotExist:
            return []

    async def notify_inbox(self, sender, conversation_id, preview, msg_type):
        other_ids = await self.get_other_participants(conversation_id, sender)
        for user_id in other_ids:
            await self.channel_layer.group_send(
                f'inbox_{user_id}',
                {
                    'type': 'inbox_message',
                    'sender_name': sender.full_name,
                    'sender_id': sender.id,
                    'conversation_id': int(conversation_id),
                    'preview': preview,
                    'msg_type': msg_type,
                }
            )


# ✅ নতুন InboxConsumer
class InboxConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close()
            return

        self.group_name = f'inbox_{user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def inbox_message(self, event):
        await self.send(text_data=json.dumps(event))