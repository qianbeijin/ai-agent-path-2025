import apiClient from '@/api/index' // 引入刚才封装好的工业级 API 客户端

export const chatApi = {
  // 发送消息
  sendMessage: (payload) => apiClient.post('/chat/send', payload),
}
