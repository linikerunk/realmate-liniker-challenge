import pytest
from django.utils import timezone
from chat.models import Conversation, Message


@pytest.mark.django_db
class TestConversation:
    def test_conversation_creation(self):
        conversation = Conversation.objects.create()
        assert conversation.status == 'OPEN'
        assert conversation.created_at is not None
        assert conversation.updated_at is not None

    def test_conversation_close(self):
        conversation = Conversation.objects.create()
        conversation.status = 'CLOSED'
        conversation.save()
        assert conversation.status == 'CLOSED'


@pytest.mark.django_db
class TestMessage:
    def test_message_creation(self):
        conversation = Conversation.objects.create()
        message = Message.objects.create(
            conversation=conversation,
            content="Test message",
            type="INBOUND"
        )
        assert message.content == "Test message"
        assert message.type == "INBOUND"
        assert message.conversation == conversation
        assert message.timestamp is not None
        assert message.processed is False

    def test_message_processed_flag(self):
        conversation = Conversation.objects.create()
        message = Message.objects.create(
            conversation=conversation,
            content="Test message",
            type="INBOUND"
        )
        message.processed = True
        message.save()
        assert message.processed is True
