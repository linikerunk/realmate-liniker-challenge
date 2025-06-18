<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import ConversationList from './chat/ConversationList.vue'
import ChatArea from './chat/ChatArea.vue'
import { chatService } from '../services/chatService'

const conversations = ref([])
const selectedConversation = ref(null)
const loading = ref(false)
const error = ref(null)
const pollingInterval = ref(null)
const POLLING_INTERVAL = 3000 // 3 segundos

// Limpa o erro após 5 segundos
const clearError = () => {
  setTimeout(() => {
    error.value = null
  }, 5000)
}

// Carrega a lista de conversas
const loadConversations = async () => {
  try {
    loading.value = true
    const response = await chatService.getConversations()
    conversations.value = response
    
    // Se tiver uma conversa selecionada, atualiza ela com os novos dados
    if (selectedConversation.value) {
      const updatedConversation = response.find(c => c.id === selectedConversation.value.id)
      if (updatedConversation) {
        selectedConversation.value = updatedConversation
      }
    } 
    // Se não tiver conversa selecionada e houver conversas, seleciona a primeira
    else if (response.length > 0 && !selectedConversation.value) {
      selectedConversation.value = response[0]
    }
  } catch (err) {
    error.value = 'Erro ao carregar conversas: ' + err.message
    clearError()
  } finally {
    loading.value = false
  }
}

// Função para buscar atualizações da conversa atual
const pollCurrentConversation = async () => {
  if (!selectedConversation.value) return
  
  try {
    const conversation = await chatService.getConversationMessages(selectedConversation.value.id)
    // Verifica se há novas mensagens comparando a última mensagem
    const currentLastMessage = selectedConversation.value.messages[selectedConversation.value.messages.length - 1]
    const newLastMessage = conversation.messages[conversation.messages.length - 1]
    
    if (!currentLastMessage || 
        !newLastMessage || 
        currentLastMessage.id !== newLastMessage.id ||
        conversation.status !== selectedConversation.value.status) {
      // Atualiza a conversa selecionada e a lista de conversas
      selectedConversation.value = conversation
      await loadConversations()
    }
  } catch (err) {
    console.error('Erro ao atualizar conversa:', err)
  }
}

// Inicia o polling
const startPolling = () => {
  stopPolling() // Garante que não haja múltiplos intervals
  pollingInterval.value = setInterval(pollCurrentConversation, POLLING_INTERVAL)
}

// Para o polling
const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

// Cria uma nova conversa
const handleNewChat = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Cria a nova conversa
    const response = await chatService.createConversation()
    
    // Recarrega a lista de conversas
    await loadConversations()
    
    // Encontra e seleciona a nova conversa
    const newConversation = conversations.value.find(c => c.id === response.conversation_id)
    if (newConversation) {
      selectedConversation.value = newConversation
      startPolling() // Inicia o polling quando uma nova conversa é criada
    }
  } catch (err) {
    error.value = 'Erro ao criar conversa: ' + err.message
    clearError()
  } finally {
    loading.value = false
  }
}

const handleSelectConversation = (conversation) => {
  selectedConversation.value = conversation
  startPolling() // Reinicia o polling quando uma conversa é selecionada
}

// Lifecycle hooks
onMounted(() => {
  loadConversations()
  startPolling()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<template>
  <div class="chat-container">
    <div class="chat-layout">
      <div class="sidebar">
        <div class="sidebar-header">
          <h2 class="title">Conversas</h2>
          <button 
            class="new-chat-btn" 
            @click="handleNewChat" 
            :disabled="loading"
            :class="{ 'loading': loading }"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? 'Criando...' : 'Novo Chat' }}
          </button>
        </div>
        <ConversationList 
          :conversations="conversations"
          :selectedId="selectedConversation?.id"
          @select-conversation="handleSelectConversation"
        />
      </div>
      <div class="chat-main">
        <ChatArea 
          :conversation="selectedConversation"
          @conversation-closed="loadConversations"
          @message-sent="pollCurrentConversation"
        />
      </div>
    </div>
    <transition name="fade">
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </transition>
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  background-color: #1a1b1e;
  color: #e5e7eb;
}

#app {
  height: 100vh;
  width: 100vw;
  display: flex;
  background-color: #1a1b1e;
}

.chat-container {
  flex: 1;
  display: flex;
  width: 100%;
  height: 100%;
  padding: 1rem;
}

.chat-layout {
  flex: 1;
  display: flex;
  width: 100%;
  background: #2c2d30;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.sidebar {
  width: 320px;
  border-right: 1px solid #3f3f46;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background-color: #26272a;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #3f3f46;
}

.title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 1rem;
}

.new-chat-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.new-chat-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.new-chat-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.chat-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  background-color: #2c2d30;
}

.error-message {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background-color: #991b1b;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  z-index: 1000;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .chat-container {
    padding: 0;
  }
  
  .chat-layout {
    border-radius: 0;
  }

  .sidebar {
    width: 280px;
  }
}
</style>
