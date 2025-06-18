import uuid
from django.db import models

# Create your models here.
## create models class conevrsation and message as the cheallegende talk :
## conversation: id, status, created_at, updated_at
## conversation_status: OPEN, CLOSED
class Conversation(models.Model):
    """
    Model representing a conversation.
    """
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(
         primary_key=True,
         default=uuid.uuid4,
         editable=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Conversation {self.id} - {self.status}"
    


class Message(models.Model):
    """
    Model representing a message in a conversation.
    """
    TYPE_CHOICES = [
        ('INBOUND', 'Inbound'),
        ('OUTBOUND', 'Outbound'),
    ]
    id = models.UUIDField(
         primary_key=True,
         default=uuid.uuid4,
         editable=True)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    type = models.CharField(max_length=8, choices=TYPE_CHOICES, default='INBOUND')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False, null=True, blank=True)
   
    def __str__(self):
        return f"Message {self.id} - {self.type} at {self.timestamp}"

    class Meta:
        ordering = ['timestamp']