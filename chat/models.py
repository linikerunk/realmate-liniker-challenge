from django.db import models
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Aberta'),
        ('CLOSED', 'Fechada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='OPEN'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversa {self.id} - {self.status}"

    class Meta:
        ordering = ['-updated_at']

    def close(self):
        """Fecha a conversa se estiver aberta"""
        if self.status == 'CLOSED':
            raise ValidationError("Conversation is already closed")
        self.status = 'CLOSED'
        self.save()

    def can_add_message(self):
        """Verifica se é possível adicionar novas mensagens"""
        return self.status == 'OPEN'

class Message(models.Model):
    TYPE_CHOICES = [
        ('INBOUND', 'Recebida'),
        ('OUTBOUND', 'Enviada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    type = models.CharField(
        max_length=8, 
        choices=TYPE_CHOICES
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)
    whatsapp_message_id = models.CharField(
        max_length=100, 
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.type} - {self.timestamp}"

    class Meta:
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        if not self.conversation.can_add_message():
            raise ValidationError("Cannot add message to a closed conversation")
        super().save(*args, **kwargs)
