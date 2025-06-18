from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Conversation, Message


@shared_task
def process_grouped_messages(conversation_id):
    """
    Processa mensagens de uma conversa, agrupando aquelas que têm
    intervalo de até 5 segundos entre si.
    """
    conversation = Conversation.objects.get(id=conversation_id)
    
    # Busca mensagens INBOUND não processadas
    messages = Message.objects.filter(
        conversation=conversation,
        type='INBOUND',
        processed=False
    ).order_by('timestamp')

    if not messages.exists():
        return

    # Coleta mensagens que formam uma sequência contínua
    # (não mais que 5 segundos entre mensagens consecutivas)
    current_time = timezone.now()
    messages_to_process = []
    last_message = None

    for message in messages:
        if last_message is None:
            messages_to_process.append(message)
        else:
            time_diff = (message.timestamp - last_message.timestamp).total_seconds()
            # Se a diferença for maior que 5 segundos, para de coletar
            if time_diff > 5:
                break
            messages_to_process.append(message)
        last_message = message

    # Verifica se passou tempo suficiente desde a última mensagem
    if messages_to_process:
        last_message = messages_to_process[-1]
        time_since_last = (current_time - last_message.timestamp).total_seconds()
        
        # Só processa se não houver mensagens novas nos últimos 5 segundos
        if time_since_last >= 5:
            # Verifica se é a primeira mensagem do usuário
            is_first_message = not Message.objects.filter(
                conversation=conversation,
                type='OUTBOUND'
            ).exists()

            # Define o conteúdo da mensagem
            if is_first_message:
                content = "Olá! Sou o assistente de busca de imóveis. Em que posso ajudá-lo hoje?"
            else:
                content = f"Mensagens recebidas:\n{chr(10).join(str(msg.id) for msg in messages_to_process)}"

            # Cria a mensagem OUTBOUND
            Message.objects.create(
                conversation=conversation,
                content=content,
                type='OUTBOUND',
                timestamp=current_time
            )
            
            # Marca as mensagens como processadas
            for message in messages_to_process:
                message.processed = True
                message.save()
        else:
            # Reagenda a task para tentar novamente em 5 segundos
            process_grouped_messages.apply_async(
                args=[conversation_id],
                countdown=5
            )
    
    # Se ainda houver mensagens não processadas, agenda nova execução
    remaining_unprocessed = messages.filter(processed=False).exclude(
        id__in=[m.id for m in messages_to_process]
    ).exists()
    
    if remaining_unprocessed:
        process_grouped_messages.apply_async(
            args=[conversation_id],
            countdown=5
        )
