from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation
from .serializers import WebHookPayloadSerializer

class WebhookView(generics.CreateAPIView):
    """
    Endpoint para receber eventos do webhook.
    Aceita apenas método POST.
    """
    serializer_class = WebHookPayloadSerializer

    def post(self, request, *args, **kwargs):
        import ipdb; ipdb.set_trace();
        event_type = request.data.get('event_type')

        if event_type == 'NEW_CONVERSATION':
            # Cria nova conversa
            conversation = Conversation.objects.create()
            message_data = {
                'conversation': conversation.id,
                'type': 'INBOUND',
                'content': request.data.get('content', '')
            }
            serializer = self.get_serializer(data=message_data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'conversation_id': conversation.id,
                    'message': serializer.data
                }, status=status.HTTP_201_CREATED)

        elif event_type == 'NEW_MESSAGE':
            # Adiciona mensagem a uma conversa existente
            conversation_id = request.data.get('conversation_id')
            conversation = get_object_or_404(Conversation, id=conversation_id)
            
            if conversation.status == 'CLOSED':
                return Response({
                    'error': 'Cannot add message to closed conversation'
                }, status=status.HTTP_400_BAD_REQUEST)

            message_data = {
                'conversation': conversation.id,
                'type': request.data.get('type', 'INBOUND'),
                'content': request.data.get('content')
            }
            serializer = self.get_serializer(data=message_data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        elif event_type == 'CLOSE_CONVERSATION':
            # Fecha uma conversa existente
            conversation_id = request.data.get('conversation_id')
            conversation = get_object_or_404(Conversation, id=conversation_id)
            
            if conversation.status == 'CLOSED':
                return Response({
                    'error': 'Conversation is already closed'
                }, status=status.HTTP_400_BAD_REQUEST)

            conversation.status = 'CLOSED'
            conversation.save()
            
            return Response(status=status.HTTP_200_OK)

        return Response({
            'error': f'Invalid event_type: {event_type}'
        }, status=status.HTTP_400_BAD_REQUEST)

