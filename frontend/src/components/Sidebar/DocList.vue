<template>
  <div class="h-full flex flex-col p-5">
    <div class="flex items-center gap-3 mb-8">
      <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
        <span class="text-white">A</span>
      </div>
      <span class="text-[#C4C7C5] font-bold text-xl">WZA RAG</span>
    </div>

    <el-scrollbar class="flex-1">
      <div class="text-[#C4C7C5] text-sm font-medium mb-4 uppercase tracking-wider">最近文档</div>

      <div class="space-y-2">
        <div
          v-for="doc in documentList"
          :key="doc.id"
          @click="handleSelect(doc)"
          :class="[
            'flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all border',
            currentDocId === doc.id
              ? 'bg-blue-600/10 border-blue-500/30 text-blue-400'
              : 'border-transparent text-gray-400 hover:bg-gray-800',
          ]"
        >
          <el-icon><Document /></el-icon>
          <span class="text-sm truncate flex-1">{{ doc.name }}</span>
          <div v-if="currentDocId === doc.id" class="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
        </div>
      </div>
    </el-scrollbar>

    <div class="pt-4 border-t border-[#3c4043]">
      <el-upload
        v-model:file-list="fileList"
        class="upload-demo text-center"
        action="#"
        :show-file-list="false"
        :http-request="handleUpload"
      >
        <el-button
          type="primary"
          class="w-full !rounded-xl !h-11 !bg-blue-600 hover:!bg-blue-500 !border-none"
          :loading="isUploading"
        >
          <el-icon class="mr-2"><Upload /></el-icon>
          {{ isUploading ? '正在解析 PDF...' : '点击上传' }}
        </el-button>
        <template #tip>
          <div class="el-upload__tip">仅支持标准 PDF 文档，最大支持 20MB</div>
        </template>
      </el-upload>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDocumentStore } from '@/store/document'
import { storeToRefs } from 'pinia'
import { Upload, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 1. 引入store
const docStore = useDocumentStore()
// 2. 使用 storeToRefs 保持解构后的响应式
const { documentList, isUploading, currentDoc } = storeToRefs(docStore)
const fileList = ref([])

// 3. 挂载时立即拉取列表
onMounted(() => {
  docStore.fetchDocuments()
})

const handleUpload = async (options) => {
  const { file } = options
  // 基础校验：虽然后端有校验，但前端拦截能极大提升用户体验
  if (file.type !== 'application/pdf') {
    ElMessage.warning('请上传 PDF 格式的文件')
    return
  }
  const res = await docStore.uploadFile(file)
  if (res.success) {
    ElMessage.success('文档解析成功，已加入知识库')
  } else {
    ElMessage.error(res.message)
  }
}

const onSelect = (doc) => {
  docStore.selectDoc(doc)
}
</script>

<style scoped>
:deep(.el-upload) {
  width: 100%;
}
</style>
