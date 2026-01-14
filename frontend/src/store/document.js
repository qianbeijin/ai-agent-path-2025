// src/store/document.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentApi } from '@/api/document'

export const useDocumentStore = defineStore('document', () => {
  // --- 1. State (用 ref 定义) ---
  const documentList = ref([])
  const isUploading = ref(false)
  const currentDocId = ref(null) // 记录 ID 而不是名字

  // --- 2. Actions (直接写异步函数) ---

  // 获取文件列表
  const fetchDocuments = async () => {
    try {
      const response = await documentApi.getList()
      // 注意：我们在拦截器里直接返回了 response.data
      if (response.status === 'success') {
        documentList.value = response.data
      }
    } catch (error) {
      console.error('获取文档列表失败:', error)
    }
  }

  // 上传文件逻辑
  const uploadFile = async (file) => {
    isUploading.value = true
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await documentApi.upload(formData)

      if (response.status === 'success') {
        // 核心交互：上传完立即刷新列表
        await fetchDocuments()
        return { success: true, message: response.message }
      }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '上传失败',
      }
    } finally {
      isUploading.value = false
    }
  }

  const selectDoc = (doc) => {
    // doc 是一个对象 { id, name }
    if (currentDocId.value === doc.id) {
      currentDocId.value = null
    } else {
      currentDocId.value = doc.id
    }
  }

  // --- 3. 暴露给外部 ---
  return {
    documentList,
    isUploading,
    currentDocId,
    fetchDocuments,
    uploadFile,
    selectDoc,
  }
})
