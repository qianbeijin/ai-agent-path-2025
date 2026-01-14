<template>
  <el-container class="py-8 max-w-4xl mx-auto text-[#E3E3E3]">
    <el-main>
      <el-scrollbar ref="scrollbarRef" class="px-4">
        <div class="flex flex-col gap-4">
          <template v-for="item in messages">
            <div class="flex" :class="item.role">
              <div
                v-if="item.role === 'assistant'"
                class="w-8 h-8 mr-3 rounded-full bg-gradient-to-br from-[#4285F4] via-[#9B72CB] to-[#D96570] flex-shrink-0 flex items-center justify-center text-[10px] text-white font-bold shadow-lg"
              >
                AI
              </div>
              <div
                class="reply markdown-body"
                :style="{
                  borderRadius: item.role == 'user' ? '24px 2px 24px 24px' : '2px 24px 24px 24px',
                }"
                v-html="renderMarkdown(item.content)"
              />
              <div
                v-if="item.role === 'user'"
                class="w-8 h-8 ml-3 rounded-full bg-[#b4b4b4] text-white flex items-center justify-center"
              >
                U
              </div>
            </div>
          </template>
        </div>
      </el-scrollbar>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/store/chat'
import { storeToRefs } from 'pinia'
import { renderMarkdown } from '@/utils/markdown' // 引入工具函数

const chatStore = useChatStore()
const { messages, isLoading } = storeToRefs(chatStore)

// 1. 定义 scrollbar 的引用
const scrollbarRef = ref(null)

// 2. 核心逻辑：监听消息数量变化
watch(
  () => messages.value.length,
  () => {
    // nextTick 确保 Vue 已经把新消息渲染到了页面上
    nextTick(() => {
      if (scrollbarRef.value) {
        // 获取 el-scrollbar 内部的滚动容器
        const scrollEl = scrollbarRef.value.wrapRef
        if (scrollEl) {
          // 平滑滚动到底部
          scrollEl.scrollTo({
            top: scrollEl.scrollHeight,
            behavior: 'smooth',
          })
        }
      }
    })
  },
  { deep: true }, // 深度监听数组内部变化
)

// 3. (可选) 监听 isLoading 状态
// 当 AI 开始“思考中...”时，也向下滚动一次，防止提示语被遮挡
watch(isLoading, (val) => {
  if (val) {
    nextTick(() => {
      const scrollEl = scrollbarRef.value?.wrapRef
      scrollEl?.scrollTo({ top: scrollEl.scrollHeight, behavior: 'smooth' })
    })
  }
})
</script>

<style scoped>
.reply {
  padding: 16px;
  background: #282a2c;
  max-width: 60%;
  color: #e3e3e3;
  letter-spacing: 0.01em;
}

.assistant {
  justify-content: left;
}

.user {
  justify-content: right;
}

/* 🏆 增加一些 Markdown 的基础样式，防止表格或代码块溢出 */
:deep(.markdown-body) {
  line-height: 1.6;
  word-wrap: break-word;
}
:deep(.markdown-body pre) {
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  background-color: #1e1e1e; /* 配合 github-dark 主题 */
}
:deep(.markdown-body table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}
:deep(.markdown-body th),
:deep(.markdown-body td) {
  border: 1px solid #ddd;
  padding: 8px;
}
</style>
