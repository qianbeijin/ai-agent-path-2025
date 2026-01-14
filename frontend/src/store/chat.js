import { defineStore } from 'pinia'
import { useDocumentStore } from './document' // 引入文档 Store 获取上下文
import { ref, computed } from 'vue'
import { chatApi } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  const isLoading = ref(false)
  const messages = ref([
    {
      role: 'assistant',
      content:
        '你好！我是你的专属 AI 助手小吴。你可以直接向我提问，或者在左侧选择一个文档进行深度探讨。',
    },
  ])

  // 注入另一个 Store 的状态
  const docStore = useDocumentStore()

  // --- 2. Getters ---
  // 判断当前是否在针对特定文档对话
  const isContextChat = computed(() => !!docStore.currentDocId)

  const sendMessage = async (userInput) => {
    if (!userInput.trim() || isLoading.value) return

    const userMsg = { role: 'user', content: userInput }
    messages.value.push(userMsg)

    // 插入一条空的 AI 消息占位
    messages.value.push({ role: 'assistant', content: '' })
    const assistantMsgIndex = messages.value.length - 1
    isLoading.value = true

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userInput,
          history: messages.value.slice(0, -1).map((m) => ({ role: m.role, content: m.content })),
          docId: docStore.currentDocId, //
        }),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        // 解析 SSE 格式数据 (data: {"text": "..."})
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6)
            if (dataStr === '[DONE]') break

            try {
              const { text } = JSON.parse(dataStr)
              // 🏆 核心：实时更新响应式数组中的最后一条消息
              messages.value[assistantMsgIndex].content += text
            } catch (e) {
              /* 忽略心跳或空行 */
            }
          }
        }
      }
    } finally {
      isLoading.value = false //
    }
  }

  // 清空对话历史
  const clearHistory = () => {
    messages.value = [messages.value[0]] // 只保留第一条欢迎语
  }

  return {
    messages,
    isLoading,
    isContextChat,
    sendMessage,
    clearHistory,
  }
})
