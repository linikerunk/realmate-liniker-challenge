<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  conversations: {
    type: Array,
    required: true
  },
  selectedId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['select-conversation'])

const handleClick = (conversation) => {
  emit('select-conversation', conversation)
}

// Formata a data para exibição
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR', { 
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Pega a última mensagem da conversa
const getLastMessage = (conversation) => {
  if (conversation.messages && conversation.messages.length > 0) {
    return conversation.messages[conversation.messages.length - 1].content
  }
  return 'Nenhuma mensagem'
}
</script>

<template>
  <div class="conversation-list">
    <!-- Lista de conversas -->
    <div class="conversation-scroll">
      <div 
        v-for="conversation in conversations" 
        :key="conversation.id"
        @click="handleClick(conversation)"
        class="conversation-item"
        :class="{ 'selected': selectedId === conversation.id }"
      >
        <div class="conversation-content">
          <div class="avatar">
            <span class="avatar-text">
              {{ conversation.id.substring(0, 2).toUpperCase() }}
            </span>
          </div>
          
          <div class="conversation-info">
            <div class="conversation-header">
              <span class="conversation-id">Conversa #{{ conversation.id.substring(0, 8) }}</span>
              <span :class="['status-badge', conversation.status.toLowerCase()]">
                {{ conversation.status }}
              </span>
            </div>
            <div class="conversation-message">{{ getLastMessage(conversation) }}</div>
            <div class="conversation-time">{{ formatDate(conversation.updated_at) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.conversation-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #26272a;
  overflow: hidden;
}

.conversation-scroll {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #4b5563 #26272a;
}

.conversation-scroll::-webkit-scrollbar {
  width: 4px;
}

.conversation-scroll::-webkit-scrollbar-track {
  background: #26272a;
}

.conversation-scroll::-webkit-scrollbar-thumb {
  background-color: #4b5563;
  border-radius: 2px;
}

.conversation-item {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #3f3f46;
  transition: all 0.2s;
  cursor: pointer;
}

.conversation-item:hover {
  background-color: #323337;
}

.conversation-item.selected {
  background-color: #3b82f6;
}

.conversation-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 9999px;
  background-color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-text {
  color: #3b82f6;
  font-size: 1.25rem;
  font-weight: 600;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.conversation-id {
  font-size: 1rem;
  font-weight: 500;
  color: #e5e7eb;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-weight: 500;
}

.status-badge.open {
  background-color: #059669;
  color: white;
}

.status-badge.closed {
  background-color: #dc2626;
  color: white;
}

.conversation-message {
  font-size: 0.875rem;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.25rem;
}

.conversation-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.selected .conversation-id,
.selected .conversation-message,
.selected .conversation-time {
  color: white;
}

.selected .status-badge {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.selected .avatar {
  background-color: rgba(255, 255, 255, 0.2);
}

.selected .avatar-text {
  color: white;
}
</style>
