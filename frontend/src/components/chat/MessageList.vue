<script setup>
import { defineProps, ref } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  isTyping: {
    type: Boolean,
    default: false
  }
})

const messageContainer = ref(null)

// Formata a data para exibição
const formatMessageTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    day: '2-digit',
    month: '2-digit'
  })
}
</script>

<template>
  <div class="messages-container" ref="messageContainer">
    <div v-if="loading" class="loading-indicator">
      <div class="loading-spinner"></div>
      <span>Carregando mensagens...</span>
    </div>
    
    <div v-else-if="messages.length === 0" class="empty-messages">
      <p>Nenhuma mensagem ainda. Comece a conversa!</p>
    </div>
    
    <div v-else class="messages-list">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="[
          'message-wrapper',
          message.type === 'OUTBOUND' ? 'justify-end' : 'justify-start'
        ]"
      >
        <!-- Avatar para mensagens recebidas -->
        <div 
          v-if="message.type === 'INBOUND'"
          class="message-avatar"
        >
          <span class="avatar-text">U</span>
        </div>

        <!-- Bolha de mensagem -->
        <div
          :class="[
            'message-bubble',
            message.type === 'OUTBOUND' ? 'message-sent' : 'message-received'
          ]"
        >
          <div class="message-content">
            {{ message.content }}
          </div>
          <div class="message-info">
            <div class="message-time">
              {{ formatMessageTime(message.timestamp) }}
            </div>
            <div v-if="message.type === 'INBOUND' && message.processed" class="message-status">
              ✓ Processada
            </div>
          </div>
        </div>

        <!-- Avatar para mensagens enviadas -->
        <div 
          v-if="message.type === 'OUTBOUND'"
          class="message-avatar bot"
        >
          <span class="avatar-text">B</span>
        </div>
      </div>

      <!-- Indicador de digitação -->
      <div v-if="isTyping" class="message-wrapper justify-end">
        <div class="message-bubble message-sent typing-bubble">
          <div class="typing-indicator">
            <span>digitando</span>
            <span class="dot-1">.</span>
            <span class="dot-2">.</span>
            <span class="dot-3">.</span>
          </div>
        </div>
        <div class="message-avatar bot">
          <span class="avatar-text">B</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #9ca3af;
  padding: 2rem;
}

.loading-spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #3b82f6;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-messages {
  text-align: center;
  color: #9ca3af;
  padding: 2rem;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.message-wrapper.justify-end {
  justify-content: flex-end;
}

.message-wrapper.justify-start {
  justify-content: flex-start;
}

.message-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background-color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-avatar.bot {
  background-color: #3b82f6;
}

.avatar-text {
  color: #ffffff;
  font-weight: 600;
  font-size: 0.875rem;
}

.message-bubble {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  position: relative;
}

.message-sent {
  background-color: #3b82f6;
  color: #ffffff;
  border-bottom-right-radius: 0.25rem;
}

.message-received {
  background-color: #374151;
  color: #ffffff;
  border-bottom-left-radius: 0.25rem;
}

.message-content {
  font-size: 0.938rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.8;
}

.message-status {
  font-size: 0.7rem;
  color: #4CAF50;
}

/* Estilos para o indicador de digitação */
.typing-bubble {
  padding: 8px 16px;
  min-width: 80px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.9em;
  color: #fff;
}

.typing-indicator span {
  opacity: 0.8;
}

.typing-indicator .dot-1,
.typing-indicator .dot-2,
.typing-indicator .dot-3 {
  animation: typingDot 1.4s infinite;
  display: inline-block;
}

.typing-indicator .dot-2 {
  animation-delay: 0.2s;
}

.typing-indicator .dot-3 {
  animation-delay: 0.4s;
}

@keyframes typingDot {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estilização da scrollbar */
.messages-container {
  scrollbar-width: thin;
  scrollbar-color: #4b5563 transparent;
}

.messages-container::-webkit-scrollbar {
  width: 4px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background-color: #4b5563;
  border-radius: 2px;
}
</style>
