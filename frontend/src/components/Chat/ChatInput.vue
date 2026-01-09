<template>
  <div class="p-3 bg-[#1e1f20]" style="border-radius: 24px">
    <el-input
      v-model="inputContent"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 6 }"
      placeholder="问问你的 AI..."
      class="gemini-input"
    />
    <div class="text-right mt-2">
      <el-button type="" circle :disabled="!inputContent.trim()" @click="doSend">
        <el-icon :size="18"><Promotion /></el-icon>
      </el-button>
    </div>
  </div>
  <div class="py-3 text-[11px] text-[#C4C7C5] text-center">AI 助手可能会出错。请核实重要信息。</div>
</template>

<script name="ChatInput" setup>
import { ref } from 'vue'
import { Plus, Promotion } from '@element-plus/icons-vue'

const inputContent = ref('')
</script>

<style scoped>
/* 1. 核心：禁止拖拽缩放 */
:deep(.el-textarea__inner) {
  resize: none !important; /* 彻底禁用右下角的拉伸手柄 */
  background-color: transparent !important; /* 配合你的深色背景 */
  border: none !important;
  box-shadow: none !important;
  color: #e3e3e3 !important;
  padding: 12px 16px;
  font-size: 16px;
}

/* 2. 滚动条美化（当超过 6 行出现滚动条时） */
:deep(.el-textarea__inner::-webkit-scrollbar) {
  width: 10px;
}
:deep(.el-textarea__inner::-webkit-scrollbar-thumb) {
  background: #333537;
  border-radius: 10px;
}
</style>
