<template>
  <el-container class="pt-8 max-w-4xl mx-auto text-[#E3E3E3]">
    <el-main>
      <el-scrollbar class="bg-blue">
        <div class="flex flex-col gap-4">
          <template v-for="item in messages">
            <div class="reply">{{ item.content }}</div>
          </template>
        </div>
      </el-scrollbar>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useChatStore } from '@/store/chat'
import { storeToRefs } from 'pinia'

const chatStore = useChatStore()
const { messages, isLoading } = storeToRefs(chatStore)
</script>

<style scoped>
.reply {
  padding: 16px;
  border-radius: 24px 2px 24px 24px;
  background: #282a2c;
  max-width: 60%;
  color: #e3e3e3;
}

.ai {
}
</style>
