<script setup>
import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'
import Chat from './components/Chat.vue'

// initialize components based on data attribute selectors
onMounted(() => {
    initFlowbite();
})
</script>



<template>
  <Chat />
</template>

