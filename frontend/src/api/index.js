import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
})

// 2. 请求拦截器：未来可以在这里统一添加 Token 或 SessionID
apiClient.interceptors.request.use(
  (config) => {
    // 比如：config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error),
)

// 3. 响应拦截器：全局处理错误
apiClient.interceptors.response.use(
  (response) => response.data, // 30k 细节：直接返回 data，让组件里少写一层 .data
  (error) => {
    const message = error.response?.data?.detail || '网络连接异常'
    // 这里可以接入 Element Plus 的 ElMessage 弹窗提示用户
    console.error('API Error:', message)
    return Promise.reject(error)
  },
)

export default apiClient
