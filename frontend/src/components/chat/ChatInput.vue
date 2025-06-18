<script setup>
import { ref, defineEmits } from 'vue'

const emit = defineEmits(['send'])

const messageText = ref('')

const handleSubmit = () => {
  const text = messageText.value.trim()
  if (text) {
    emit('send', text)
    messageText.value = ''
  }
}

const handleKeyDown = (event) => {
  // Envia mensagem quando pressionar Enter (sem Shift)
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <textarea
        v-model="messageText"
        @keydown="handleKeyDown"
        placeholder="Digite sua mensagem..."
        class="message-textarea"
        rows="1"
      ></textarea>
      <button
        @click="handleSubmit"
        class="send-button"
        :disabled="!messageText.trim()"
      >
        Enviar
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-input-container {
  padding: 1rem;
  background-color: #26272a;
}

.input-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background-color: #26272a;
  border-radius: 8px;
  padding: 0.5rem;
}

.message-textarea {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 0.75rem;
  border: 1px solid #3f3f46;
  border-radius: 8px;
  resize: none;
  font-size: 0.95rem;
  line-height: 1.5;
  background-color: #1f2022;
  color: #e5e7eb;
  transition: all 0.2s;
}

.message-textarea::placeholder {
  color: #6b7280;
}

.message-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background-color: #1a1b1e;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.send-button {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-end;
  white-space: nowrap;
}

.send-button:hover {
  background-color: #2563eb;
}

.send-button:disabled {
  background-color: #374151;
  color: #6b7280;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .input-wrapper {
    gap: 0.5rem;
  }
  
  .send-button {
    padding: 0.75rem 1rem;
  }
}
</style>
