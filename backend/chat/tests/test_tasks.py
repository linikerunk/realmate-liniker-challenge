import pytest
from django.utils import timezone
from datetime import timedelta
from chat.models import Conversation, Message
from chat.tasks import process_grouped_messages
from unittest.mock import patch


@pytest.mark.django_db
class TestMessageProcessing:
    def test_single_message_processing(self):
        import ipdb; ipdb.set_trace()
        conversation = Conversation.objects.create()
        message = Message.objects.create(
            conversation=conversation,
            content="Test message",
            type="INBOUND"
        )
        
        process_grouped_messages(conversation.id)
        
        outbound_messages = Message.objects.filter(
            conversation=conversation,
            type="OUTBOUND"
        )
        assert outbound_messages.count() == 1
        assert f"Mensagens recebidas:\n{message.id}" in outbound_messages.first().content
        
        message.refresh_from_db()
        assert message.processed is True

    def test_multiple_messages_processing(self):
        conversation = Conversation.objects.create()
        messages = []
        
        # Criar 3 mensagens em sequência rápida
        for i in range(3):
            message = Message.objects.create(
                conversation=conversation,
                content=f"Message {i}",
                type="INBOUND",
                timestamp=timezone.now() + timedelta(seconds=i)
            )
            messages.append(message)
        
        process_grouped_messages(conversation.id)
        
        outbound_messages = Message.objects.filter(
            conversation=conversation,
            type="OUTBOUND"
        )
        assert outbound_messages.count() == 1
        
        # Verificar se todas as mensagens foram incluídas na resposta
        outbound_content = outbound_messages.first().content
        for message in messages:
            assert str(message.id) in outbound_content
            message.refresh_from_db()
            assert message.processed is True

    def test_message_after_6_seconds(self):
        conversation = Conversation.objects.create()
        late_message = Message.objects.create(
            conversation=conversation,
            content="Late message",
            type="INBOUND",
            timestamp=conversation.created_at + timedelta(seconds=7)
        )
        
        process_grouped_messages(conversation.id)
        
        outbound_messages = Message.objects.filter(
            conversation=conversation,
            type="OUTBOUND"
        )
        assert outbound_messages.count() == 1
        assert str(late_message.id) in outbound_messages.first().content
        
        late_message.refresh_from_db()
        assert late_message.processed is True

    @patch('chat.tasks.process_grouped_messages.apply_async')
    def test_requeue_for_recent_messages(self, mock_apply_async):
        conversation = Conversation.objects.create()
        
        # Mensagem recente (menos de 5 segundos)
        Message.objects.create(
            conversation=conversation,
            content="Recent message",
            type="INBOUND",
            timestamp=timezone.now()
        )
        
        process_grouped_messages(conversation.id)
        
        # Verifica se a task foi reagendada
        mock_apply_async.assert_called_once_with(
            args=[conversation.id],
            countdown=5
        )
