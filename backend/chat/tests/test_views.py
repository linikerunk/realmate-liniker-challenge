import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from chat.models import Conversation, Message
from django.utils import timezone
import uuid


@pytest.mark.django_db
class TestWebhookView:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_new_conversation(self, api_client):
        conversation_id = str(uuid.uuid4())
        data = {
            "type": "NEW_CONVERSATION",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": conversation_id
            }
        }
        
        response = api_client.post(reverse('webhook'), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Conversation.objects.filter(id=conversation_id).exists()

    def test_duplicate_conversation(self, api_client):
        conversation_id = str(uuid.uuid4())
        Conversation.objects.create(id=conversation_id)
        
        data = {
            "type": "NEW_CONVERSATION",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": conversation_id
            }
        }
        
        response = api_client.post(reverse('webhook'), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_new_message(self, api_client):
        conversation = Conversation.objects.create()
        message_id = str(uuid.uuid4())
        
        data = {
            "type": "NEW_MESSAGE",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": message_id,
                "conversation_id": str(conversation.id),
                "content": "Test message"
            }
        }
        
        response = api_client.post(reverse('webhook'), data, format='json')
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert Message.objects.filter(id=message_id).exists()

    def test_message_to_closed_conversation(self, api_client):
        conversation = Conversation.objects.create(status='CLOSED')
        
        data = {
            "type": "NEW_MESSAGE",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": str(uuid.uuid4()),
                "conversation_id": str(conversation.id),
                "content": "Test message"
            }
        }
        
        response = api_client.post(reverse('webhook'), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_close_conversation(self, api_client):
        conversation = Conversation.objects.create()
        
        data = {
            "type": "CLOSE_CONVERSATION",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "id": str(conversation.id)
            }
        }
        
        response = api_client.post(reverse('webhook'), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        conversation.refresh_from_db()
        assert conversation.status == 'CLOSED'
