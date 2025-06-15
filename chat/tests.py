from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Conversation, Message
import uuid
from django.utils import timezone

class ChatAPITests(APITestCase):
    def setUp(self):
        # Criar uma conversa para os testes
        self.conversation = Conversation.objects.create()
        
    def test_new_conversation_flow(self):
        """Testa o fluxo completo de criação de nova conversa"""
        url = reverse('webhook')
        data = {
            'conversation_id': str(uuid.uuid4()),
            'initial_message': 'Olá, esta é uma nova conversa'
        }
        
        # Tenta criar nova conversa
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica se a conversa foi criada
        conversation_id = response.data['conversation_id']
        conversation_url = reverse('conversation-detail', args=[conversation_id])
        response = self.client.get(conversation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'OPEN')
        
        # Verifica se a mensagem inicial foi criada
        self.assertEqual(len(response.data['messages']), 1)
        self.assertEqual(response.data['messages'][0]['content'], 'Olá, esta é uma nova conversa')

    def test_message_flow(self):
        """Testa o fluxo completo de mensagens em uma conversa"""
        url = reverse('webhook')
        
        # Envia mensagem INBOUND
        inbound_data = {
            'conversation_id': str(self.conversation.id),
            'content': 'Mensagem do cliente',
            'type': 'INBOUND',
            'whatsapp_message_id': str(uuid.uuid4())
        }
        response = self.client.post(url, inbound_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        # Envia mensagem OUTBOUND
        outbound_data = {
            'conversation_id': str(self.conversation.id),
            'content': 'Resposta do sistema',
            'type': 'OUTBOUND',
            'whatsapp_message_id': str(uuid.uuid4())
        }
        response = self.client.post(url, outbound_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        # Verifica se as mensagens foram salvas corretamente
        conversation_url = reverse('conversation-detail', args=[self.conversation.id])
        response = self.client.get(conversation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['messages']), 2)
        
        messages = response.data['messages']
        self.assertEqual(messages[0]['content'], 'Mensagem do cliente')
        self.assertEqual(messages[0]['type'], 'INBOUND')
        self.assertEqual(messages[1]['content'], 'Resposta do sistema')
        self.assertEqual(messages[1]['type'], 'OUTBOUND')

    def test_closed_conversation(self):
        """Testa regras de conversa fechada"""
        # Fecha a conversa
        self.conversation.status = 'CLOSED'
        self.conversation.save()
        
        url = reverse('webhook')
        data = {
            'conversation_id': str(self.conversation.id),
            'content': 'Tentando enviar mensagem em conversa fechada',
            'type': 'INBOUND',
            'whatsapp_message_id': str(uuid.uuid4())
        }
        
        # Tenta enviar mensagem para conversa fechada
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verifica se nenhuma mensagem foi adicionada
        conversation_url = reverse('conversation-detail', args=[self.conversation.id])
        response = self.client.get(conversation_url)
        self.assertEqual(len(response.data['messages']), 0)

    def test_conversation_not_found(self):
        """Testa envio de mensagem para conversa inexistente"""
        url = reverse('webhook')
        data = {
            'conversation_id': str(uuid.uuid4()),  # ID que não existe
            'content': 'Mensagem para conversa inexistente',
            'type': 'INBOUND',
            'whatsapp_message_id': str(uuid.uuid4())
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_message(self):
        """Testa envio de mensagem duplicada (mesmo whatsapp_message_id)"""
        url = reverse('webhook')
        whatsapp_message_id = str(uuid.uuid4())
        
        # Primeira mensagem
        data = {
            'conversation_id': str(self.conversation.id),
            'content': 'Mensagem original',
            'type': 'INBOUND',
            'whatsapp_message_id': whatsapp_message_id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        # Tenta enviar a mesma mensagem novamente
        data['content'] = 'Mensagem duplicada'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
