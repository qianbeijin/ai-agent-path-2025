<template>
  <div class="h-full flex flex-col p-5">
    <div class="flex items-center gap-3 mb-8">
      <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
        <span class="text-white">A</span>
      </div>
      <span class="text-[#C4C7C5] font-bold text-xl">WZA RAG</span>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div class="text-[#C4C7C5] text-sm font-medium mb-4 uppercase tracking-wider">最近文档</div>
    </div>

    <div class="pt-4 border-t border-[#3c4043]">
      <el-button
        type="primary"
        class="w-full !rounded-xl !bg-[#1a73e8] hover:!bg-[#1557b0] !border-none"
      >
        + 上传 PDF
      </el-button>
    </div>
  </div>
</template>

<script></script>
