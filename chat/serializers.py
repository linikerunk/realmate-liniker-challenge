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

