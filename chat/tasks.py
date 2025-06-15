from celery import shared_task
from .models import Message, Conversation
from django.utils import timezone

@shared_task
def process_incoming_message(message_id):
    """
    Processa mensagem recebida de forma assíncrona
    """
    try:
        message = Message.objects.get(whatsapp_message_id=message_id)
        
        # Aqui você pode adicionar sua lógica de processamento
        # Por exemplo: análise de sentimento, categorização, etc.
        
        message.processed = True
        message.save()
        
        # Atualiza o timestamp da conversa
        message.conversation.updated_at = timezone.now()
        message.conversation.save()
        
        return True
    except Message.DoesNotExist:
        return False

@shared_task
def cleanup_old_conversations():
    """
    Fecha conversas inativas após determinado período
    """
    threshold = timezone.now() - timezone.timedelta(days=1)
    Conversation.objects.filter(
        status='ACTIVE',
        updated_at__lt=threshold
    ).update(status='CLOSED')
