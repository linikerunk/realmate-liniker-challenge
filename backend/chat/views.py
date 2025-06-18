from rest_framework import generics, status
from rest_framework.response import Response
import json
from django.core.exceptions import ObjectDoesNotExist

from chat.tasks import process_grouped_messages
from .models import Conversation, Message
from .serializers import ConversationSerializer, WebHookPayloadSerializer, MessageSerializer

class WebhookView(generics.CreateAPIView):
    """
    Endpoint para receber eventos do webhook.
    Aceita apenas método POST.
    """
    serializer_class = WebHookPayloadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        event_type = serializer.validated_data['type']
        data = serializer.validated_data['data']

        if event_type == 'NEW_CONVERSATION':
            # Verifica se já existe conversa com este ID
            if Conversation.objects.filter(id=data['id']).exists():
                return Response({
                    'error': 'Conversation with this ID already exists'
                }, status=status.HTTP_400_BAD_REQUEST)

            conversation = Conversation.objects.create(id=data['id'])
            return Response({
                'conversation_id': conversation.id
            }, status=status.HTTP_201_CREATED)

        elif event_type == 'NEW_MESSAGE':
            try:
                conversation = Conversation.objects.get(id=data['conversation_id'])
            except ObjectDoesNotExist:
                return Response({
                    'error': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if conversation.status == 'CLOSED':
                return Response({
                    'error': 'Cannot add message to closed conversation'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Cria a mensagem
            message = Message.objects.create(
                id=data['id'],
                conversation=conversation,
                content=data['content'],
                type='INBOUND'
            )

            # Agenda o processamento assíncrono
            process_grouped_messages.apply_async(
                args=[conversation.id],
                countdown=5
            )

            return Response({
                'message_id': message.id,
                'conversation_id': conversation.id
            }, status=status.HTTP_202_ACCEPTED)

        elif event_type == 'CLOSE_CONVERSATION':
            try:
                conversation = Conversation.objects.get(id=data['id'])
            except ObjectDoesNotExist:
                return Response({
                    'error': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if conversation.status == 'CLOSED':
                return Response({
                    'error': 'Conversation is already closed'
                }, status=status.HTTP_400_BAD_REQUEST)

            conversation.status = 'CLOSED'
            conversation.save()
            
            return Response({
                'conversation_id': conversation.id,
                'status': conversation.status
            }, status=status.HTTP_200_OK)

        return Response({
            'error': f'Invalid event type: {event_type}'
        }, status=status.HTTP_400_BAD_REQUEST)


class ListConversationsView(generics.ListAPIView):
    """
    Endpoint para listar todas as conversas.
    Aceita apenas método GET.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer  # Use a serializer that fits your needs

    def get(self, request, *args, **kwargs):
        conversations = self.get_queryset()
        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConversationDetailView(generics.RetrieveAPIView):
    """
    Endpoint para obter detalhes de uma conversa específica.
    Aceita apenas método GET.
    """
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        try:
            conversation = self.get_object()
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)