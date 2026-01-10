import apiClient from '@/api/index' // 引入刚才封装好的工业级 API 客户端

export const documentApi = {
  // 获取列表
  getList: () => apiClient.get('/document/list'),

  // 上传文件
  upload: (formData) =>
    apiClient.post('/document/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
}
