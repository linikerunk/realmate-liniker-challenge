import pytest
from django.conf import settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

def pytest_configure():
    settings.DEBUG = False
    settings.CELERY_ALWAYS_EAGER = True

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def conversation_payload():
    return {
        "type": "NEW_CONVERSATION",
        "timestamp": "2025-06-17T10:00:00Z",
        "data": {
            "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
        }
    }

@pytest.fixture
def message_payload():
    return {
        "type": "NEW_MESSAGE",
        "timestamp": "2025-06-17T10:00:05Z",
        "data": {
            "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
            "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a",
            "content": "Test message"
        }
    }

@pytest.fixture
def close_conversation_payload():
    return {
        "type": "CLOSE_CONVERSATION",
        "timestamp": "2025-06-17T10:05:00Z",
        "data": {
            "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
        }
    }
