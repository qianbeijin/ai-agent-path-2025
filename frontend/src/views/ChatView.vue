<script setup>
import { ref } from 'vue'
import axios from 'axios'

const userInput = ref('')
const messages = ref([{ role: 'ai', message: '你好！我是你的 AI 助手，有什么可以帮助你的吗？' }])

const isLoading = ref(false)
async function sendMessage() {
  // 判断用户是否输入为空
  if (!userInput.value.trim()) return
  // 如果ai在思考中，则需等到ai思考结束
  if (isLoading.value) return
  isLoading.value = true
  messages.value.push({
    role: 'user',
    message: userInput.value,
  })
  const params = {
    message: userInput.value,
  }
  userInput.value = ''
  try {
    const res = await axios.post('http://127.0.0.1:8000/chat', params)
    if (res.status == 200) {
      messages.value.push({
        role: 'ai',
        message: res.data.reply,
      })
    } else {
      messages.value.push({ role: 'ai', message: '其他错误' })
    }
  } catch {
    //  捕获区：专门处理“意外”
    console.error('出错了:', error) // 在控制台打印具体的错，方便调试

    // 这里可以给用户一个友好的提示
    messages.value.push({
      role: 'ai',
      message: '❌ 哎呀，出错了！可能是后端没启动，或者网络连不上。',
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="chat-container">
    <div class="message_title">DeepSeek AI 助手</div>
    <div class="message_box">
      <template v-for="(msg, index) in messages" :key="index">
        <div class="message" :class="msg.role">
          <div class="reply">
            {{ msg.message }}
          </div>
        </div>
      </template>
      <div v-if="isLoading" class="message ai">
        <div class="reply">思考中...</div>
      </div>
    </div>
    <div class="message_bottom">
      <input
        type="text"
        placeholder="请输入你的问题..."
        @keyup.enter="sendMessage"
        v-model="userInput"
      />
      <button @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  width: 540px;
  height: 90vh;
  background-color: #f5f5f5;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

.message_title {
  font-size: 25px;
  background: #007bff;
  color: #ffffff;
  text-align: center;
  padding: 20px 0;
  border-radius: 10px 10px 0 0;
}

.message_box {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.message {
  display: flex;
}

.message.ai {
  justify-content: left;
}

.message.user {
  justify-content: right;
}

.reply {
  padding: 10px 15px;
  border-radius: 15px;
  max-width: 70%;
  word-wrap: break-word;
}

.message.ai .reply {
  background-color: white;
  color: #333;
  border: 1px solid #ddd;
  border-bottom-left-radius: 2px;
}

.message.user .reply {
  background-color: #007bff;
  color: white;
  border-bottom-right-radius: 2px;
}

.message_bottom {
  padding: 20px;
  background: #ffffff;
  border-radius: 0 0 10px 10px;
  display: flex;
  align-items: center;
}

input {
  flex: 1;
  border-radius: 5px;
  padding: 10px;
  border: 1px solid #ddd;
  outline: none; /* 去除点击产生的高亮效果 */
}

button {
  margin-left: 10px;
  height: 100%;
  padding: 0 16px;
  color: #ffffff;
  background: #007bff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
