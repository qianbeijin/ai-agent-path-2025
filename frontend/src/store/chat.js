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

    isLoading.value = true

    const payload = {
      message: userInput,
      // 传递历史记录实现多轮对话，排除最后一条刚刚添加的消息
      history: messages.value.slice(0, -1).map((m) => ({
        role: m.role,
        content: m.content,
      })),
      // 核心：自动注入当前选中的文档 ID
      docId: docStore.currentDocId,
    }
    try {
      const res = await chatApi.sendMessage(payload)
      if (res.status == 'success') {
        messages.value.push({
          role: 'assistant',
          content: res.answer,
          sources: res.sources || [],
        })
      }
    } catch (error) {
      // 错误降级处理
      messages.value.push({
        role: 'assistant',
        content: '抱歉，服务器暂时忙碌，我没能接收到您的消息。',
      })
    } finally {
      isLoading.value = false
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
