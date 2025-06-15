from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    MessageSerializer,
    WebhookNewConversationSerializer,
    WebhookNewMessageSerializer,
    WebhookCloseConversationSerializer
)
from .tasks import process_incoming_message
import uuid

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root endpoint
    """
    return Response({
        'webhook': reverse('chat:webhook', request=request, format=format),
        'conversations': reverse('chat:conversation-list', request=request, format=format),
    })

@api_view(['POST'])
def webhook(request):
    """
    Endpoint principal para receber eventos do webhook
    """
    # ...resto do código existente...