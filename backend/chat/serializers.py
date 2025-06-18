from rest_framework import serializers
from .models import Conversation, Message


class WebHookPayloadSerializer(serializers.Serializer):
    """
    Serializer para payload de webhook do WhatsApp.
    """
    type = serializers.ChoiceField(choices=['NEW_CONVERSATION', 'NEW_MESSAGE', 'CLOSE_CONVERSATION'])
    timestamp = serializers.DateTimeField()
    data = serializers.JSONField()  # Alterado para JSONField para melhor suporte a JSON
    
    def validate(self, data):
        """
        Valida o payload do webhook.
        """
        if data['type'] == 'NEW_MESSAGE':
            if 'id' not in data['data']:
                raise serializers.ValidationError("Missing 'conversation_id' for NEW_MESSAGE type")
            if 'conversation_id' not in data['data']:
                raise serializers.ValidationError("Missing 'conversation_id' for NEW_MESSAGE type")
            if 'content' not in data['data']:
                raise serializers.ValidationError("Missing 'content' for NEW_MESSAGE type")
        
        elif data['type'] == 'NEW_CONVERSATION':
            if 'id' not in data['data']:
                raise serializers.ValidationError("Missing 'id' for NEW_CONVERSATION type")
        
        elif data['type'] == 'CLOSE_CONVERSATION':
            if 'id' not in data['data']:
                raise serializers.ValidationError("Missing 'id' for CLOSE_CONVERSATION type")
        
        return data



class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Message.
    """
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'type', 'content', 'timestamp']
        read_only_fields = ['timestamp']
    
    def validate(self, data):
        """
        Valida os dados da mensagem.
        """
        if not data.get('content'):
            raise serializers.ValidationError("Content cannot be empty")
        
        return data


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Conversation.
    Inclui todos os campos do modelo Message relacionados via related_name.
    """
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'status', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']

