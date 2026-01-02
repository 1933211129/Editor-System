import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  // 路径别名配置
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  
  // 开发服务器配置
  server: {
    port: 8080,
    cors: true, // 启用 CORS，方便 Django 调用
    origin: 'http://localhost:8080',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // 生产环境构建输出到 Django 的 static 目录
    // 如果需要，可以修改为 Django 的 static 目录路径
    // outDir: '../qk/qikan/static',
    rollupOptions: {
      output: {
        // 确保静态资源路径正确
        assetFileNames: 'assets/[name].[hash].[ext]',
        chunkFileNames: 'assets/[name].[hash].js',
        entryFileNames: 'assets/[name].[hash].js'
      }
    }
  },
  
  // 公共基础路径（对应 Vue CLI 的 publicPath）
  base: '/xuebao/',
  
  // 公共目录配置
  publicDir: 'public'
})

