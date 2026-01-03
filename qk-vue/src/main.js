import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)

// 配置 axios - 使用相对路径，生产环境通过 Nginx 代理到后端
axios.defaults.baseURL = ''

app.config.globalProperties.$axios = axios
app.use(router)
app.mount('#app')
