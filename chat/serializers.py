from rest_framework import serializers
from .models import Conversation, Message
from django.utils import timezone

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'type', 'content', 'timestamp', 'whatsapp_message_id', 'processed']
        read_only_fields = ['id', 'processed']

    def validate(self, data):
        # Verifica se a conversa está fechada
        conversation = data.get('conversation')
        if conversation and conversation.status == 'CLOSED':
            raise serializers.ValidationError({
                "conversation": "Cannot add messages to a closed conversation"
            })
        return data

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'status', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_status(self, value):
        # Impede que uma conversa fechada seja reaberta
        if self.instance and self.instance.status == 'CLOSED' and value != 'CLOSED':
            raise serializers.ValidationError("A closed conversation cannot be reopened")
        return value

class WebhookSerializer(serializers.Serializer):
    """
    Serializer para validar os eventos recebidos via webhook
    """
    event_type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    message_id = serializers.CharField()
    conversation_id = serializers.CharField(required=False)
    content = serializers.CharField()
    
    def validate_event_type(self, value):
        valid_types = ['message.received', 'message.sent', 'message.read']
        if value not in valid_types:
            raise serializers.ValidationError(f"Event type must be one of: {valid_types}")
        return value

class WebhookNewConversationSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=False)  # Se não fornecido, será gerado
    initial_message = serializers.CharField(required=True)

    def validate_conversation_id(self, value):
        if Conversation.objects.filter(id=value).exists():
            raise serializers.ValidationError("Conversation ID already exists")
        return value

class WebhookNewMessageSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=True)
    content = serializers.CharField(required=True)
    timestamp = serializers.DateTimeField(required=False, default=timezone.now)
    whatsapp_message_id = serializers.CharField(required=True)

    def validate_conversation_id(self, value):
        try:
            conversation = Conversation.objects.get(id=value)
            if not conversation.can_add_message():
                raise serializers.ValidationError("Conversation is closed")
            return value
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation not found")

class WebhookCloseConversationSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=True)

    def validate_conversation_id(self, value):
        try:
            conversation = Conversation.objects.get(id=value)
            if conversation.status == 'CLOSED':
                raise serializers.ValidationError("Conversation is already closed")
            return value
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation not found")