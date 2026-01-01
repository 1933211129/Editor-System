import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)

// 配置 axios
axios.defaults.baseURL = 'http://127.0.0.1:8000'  // 确保这个地址正确

app.config.globalProperties.$axios = axios
app.use(router)
app.mount('#app')
