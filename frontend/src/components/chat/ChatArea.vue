<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import MessageList from './MessageList.vue'
import ChatInput from './ChatInput.vue'
import { chatService } from '../../services/chatService'

const props = defineProps({
  conversation: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['conversation-closed', 'message-sent'])

const messages = ref([])
const loading = ref(false)
const error = ref(null)
const isTyping = ref(false)

// Carrega as mensagens da conversa
const loadMessages = async () => {
  if (!props.conversation) return
  
  try {
    loading.value = true
    const data = await chatService.getConversationMessages(props.conversation.id)
    messages.value = data.messages
  } catch (err) {
    error.value = 'Erro ao carregar mensagens: ' + err.message
  } finally {
    loading.value = false
  }
}

// Envia uma nova mensagem
const handleSendMessage = async (content) => {
  if (!props.conversation) return
  
  try {
    isTyping.value = true // Mostra o indicador de digitação
    await chatService.sendMessage(props.conversation.id, content)
    emit('message-sent')
    // Mantém o indicador por 5 segundos após enviar a mensagem
    setTimeout(() => {
      isTyping.value = false
    }, 5000)
  } catch (err) {
    error.value = 'Erro ao enviar mensagem: ' + err.message
    isTyping.value = false
  } finally {
    loading.value = false
  }
}

// Encerra a conversa
const handleCloseChat = async () => {
  if (!props.conversation) return
  
  try {
    loading.value = true
    await chatService.closeConversation(props.conversation.id)
    emit('conversation-closed')
  } catch (err) {
    error.value = 'Erro ao encerrar chat: ' + err.message
  } finally {
    loading.value = false
  }
}

// Observa mudanças na conversa selecionada
watch(() => props.conversation, (newConversation) => {
  if (newConversation) {
    messages.value = newConversation.messages || []
  } else {
    messages.value = []
  }
}, { immediate: true })
</script>

<template>
  <div class="chat-area">
    <!-- Header do chat -->
    <div class="chat-header">
      <div v-if="conversation" class="chat-header-content">
        <h3 class="chat-title">{{ conversation.status === 'CLOSED' ? '[Encerrada] ' : '' }}{{ conversation.id }}</h3>
        <button 
          v-if="conversation.status !== 'CLOSED'"
          class="end-chat-btn"
          @click="handleCloseChat"
          :disabled="loading"
        >
          {{ loading ? 'Encerrando...' : 'Encerrar Chat' }}
        </button>
      </div>
    </div>

    <!-- Área de mensagens -->
    <MessageList 
      v-if="conversation"
      :messages="conversation.messages || []"
      :loading="loading"
      :isTyping="isTyping"
      class="message-list"
    />

    <!-- Indicador de digitação -->
    <div v-if="isTyping" class="typing-indicator">
      <div class="typing-bubble">
        <span>digitando</span>
        <span class="dots">...</span>
      </div>
    </div>

    <!-- Input de mensagem -->
    <ChatInput 
      v-if="conversation && conversation.status !== 'CLOSED'"
      @send="handleSendMessage"
      :disabled="loading"
      class="chat-input"
    />

    <!-- Tela vazia quando não há conversa selecionada -->
    <div 
      v-else 
      class="empty-state"
    >
      <div class="text-center">
        <p class="empty-text">Selecione uma conversa para começar</p>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<style scoped>
.chat-area {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #2c2d30;
}

.chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #3f3f46;
  background-color: #26272a;
}

.chat-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #e5e7eb;
}

.end-chat-btn {
  padding: 0.5rem 1rem;
  color: #ef4444;
  font-weight: 500;
  border: 1px solid #ef4444;
  border-radius: 6px;
  background: transparent;
  transition: all 0.2s;
  cursor: pointer;
}

.end-chat-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background-color: #2c2d30;
}

.typing-indicator {
  position: absolute;
  bottom: 80px;
  right: 20px;
  z-index: 10;
}

.typing-bubble {
  background-color: #1a1a1a;
  padding: 8px 16px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #ffffff;
  font-size: 0.9em;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dots {
  animation: typing 1.4s infinite;
}

@keyframes typing {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

.chat-input {
  padding: 1rem 1.5rem;
  background-color: #26272a;
  border-top: 1px solid #3f3f46;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2c2d30;
}

.empty-text {
  font-size: 1.125rem;
  color: #9ca3af;
  font-weight: 500;
}

.error-message {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background-color: #991b1b;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  z-index: 10;
}
</style>