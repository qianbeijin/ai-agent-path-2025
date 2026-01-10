import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router' // 导入路由配置

// 1. 引入 Element Plus 插件及其样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 2. 引入 Tailwind CSS
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(router) // 挂载路由
app.use(pinia) //挂载pinia
app.use(ElementPlus) // 全局注册 Element Plus

app.mount('#app')
