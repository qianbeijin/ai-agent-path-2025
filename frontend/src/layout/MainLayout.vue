<template>
  <el-container class="h-screen w-full overflow-hidden bg-[#131314]">
    <el-aside width="308px" class="bg-[#1e1f20]">
      <DocList />
    </el-aside>

    <el-container class="flex flex-col relative">
      <el-main class="flex-1">
        <router-view />
      </el-main>

      <el-footer class="p-6">
        <div class="max-w-4xl mx-auto">
          <ChatInput />
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import DocList from '../components/Sidebar/DocList.vue'
import ChatInput from '../components/Chat/ChatInput.vue'
</script>

<style scoped>
/* 针对 Element Plus 容器的微调 */
:deep(.el-main) {
  --el-main-padding: 0;
}

:deep(.el-footer) {
  --el-footer-height: auto;
}

:deep(.el-textarea__inner) {
  background: #1e1f20;
  box-shadow: none;

  &:hover {
    box-shadow: none;
  }

  &:focus {
    box-shadow: none;
  }
}
</style>
