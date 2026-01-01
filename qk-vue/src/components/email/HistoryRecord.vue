<template>
  <div class="history-container">
    <h3 class="mb-4">📧 邮件历史数据</h3>
    
    <!-- 添加搜索框 -->
    <div class="search-container mb-4">
      <div class="input-group" style="max-width: 500px;">
        <input 
          type="text" 
          class="form-control" 
          v-model="searchQuery"
          placeholder="搜索发件人、收件人、主题、内容或附件..."
          @keyup.enter="handleSearch"
        >
        <button class="btn btn-primary" @click="handleSearch">
          <i class="bi bi-search"></i> 搜索
        </button>
      </div>
    </div>
    
    <div class="table-container">
      <table class="table table-hover">
        <thead class="table-light">
          <tr>
            <th scope="col" class="col-index">#</th>
            <th scope="col" class="col-type">类型</th>
            <th scope="col" class="col-time">发送时间</th>
            <th scope="col" class="col-sender">发件人</th>
            <th scope="col" class="col-recipient">收件人</th>
            <th scope="col" class="col-subject">主题</th>
            <th scope="col" class="col-content">内容</th>
            <th scope="col" class="col-attachments">附件名列表</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(record, index) in emailRecords" :key="index">
            <td>{{ index + 1 }}</td>
            <td>{{ record.type }}</td>
            <td>{{ record.date }}</td>
            <td class="text-break">{{ record.sender }}</td>
            <td class="text-break">{{ record.recipient }}</td>
            <td class="text-break">
              <div class="preview-cell" @click="showPreview('主题', record.subject)">
                {{ record.subject }}
              </div>
            </td>
            <td class="text-break">
              <div class="preview-cell" @click="showPreview('正文内容', record.body)">
                <div class="content-cell">{{ record.body }}</div>
              </div>
            </td>
            <td class="text-break">
              <div class="preview-cell" @click="showPreview('附件列表', formatAttachments(record.attachments, true))">
                <div class="attachments-cell">
                  {{ formatAttachments(record.attachments) }}
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 预览弹窗 -->
    <div class="preview-modal" v-if="showPreviewModal" @click.self="closePreview">
      <div class="preview-content">
        <div class="preview-header">
          <h5>{{ previewTitle }}</h5>
          <button class="close-btn" @click="closePreview">×</button>
        </div>
        <div class="preview-body">
          <pre>{{ previewContent }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* global defineExpose */
import { ref, onMounted } from 'vue'
import axios from 'axios'

const emailRecords = ref([])
const searchQuery = ref('')

// 预览相关的响应式变量
const showPreviewModal = ref(false)
const previewContent = ref('')
const previewTitle = ref('')

// 显示预览
const showPreview = (title, content) => {
  previewTitle.value = title
  previewContent.value = content
  showPreviewModal.value = true
}

// 关闭预览
const closePreview = () => {
  showPreviewModal.value = false
}

// 格式化附件显示
const formatAttachments = (attachments, detailed = false) => {
  if (!attachments) return '无附件'
  try {
    const files = JSON.parse(attachments)
    if (Array.isArray(files) && files.length > 0) {
      if (detailed) {
        return files.join('\n')  // 详细模式显示所有文件名
      }
      return `${files.length}个附件`  // 简略模式只显示数量
    }
    return '无附件'
  } catch (e) {
    return attachments
  }
}

// 搜索处理
const handleSearch = async () => {
  try {
    const response = await axios.get('/api/email/history', {
      params: {
        search: searchQuery.value
      }
    })
    emailRecords.value = response.data
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

onMounted(async () => {
  try {
    const response = await axios.get('/api/email/history')
    emailRecords.value = response.data
  } catch (error) {
    console.error('获取历史记录失败:', error)
  }
})

// 向父组件暴露刷新方法：根据当前搜索关键字刷新数据
defineExpose({
  refresh: async () => {
    if (searchQuery.value && searchQuery.value.trim()) {
      await handleSearch()
    } else {
      try {
        const response = await axios.get('/api/email/history')
        emailRecords.value = response.data
      } catch (error) {
        console.error('刷新历史记录失败:', error)
      }
    }
  }
})
</script>

<style scoped>
.history-container {
  width: 100%;
  height: 100%;
  padding: 1rem;
}

.table-container {
  width: 100%;
  height: calc(100vh - 8rem);
  overflow-y: auto;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

table {
  width: 100%;
  table-layout: fixed;
}

thead {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #f8f9fa;
}

th, td {
  padding: 0.75rem !important;
  vertical-align: middle;
  word-wrap: break-word;
  min-width: 0;
}

/* 设置列宽比例 */
.col-index { width: 4%; }
.col-type { width: 6%; }
.col-time { width: 10%; }
.col-sender { width: 15%; }
.col-recipient { width: 15%; }
.col-subject { width: 15%; }
.col-content { width: 25%; }
.col-attachments { width: 10%; }

/* 内容单元格样式 */
.content-cell {
  max-height: 3.6em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  line-height: 1.2;
}

/* 预览相关样式 */
.preview-cell {
  cursor: pointer;
  /* color: #0d6efd; */
}

.preview-cell:hover {
  text-decoration: underline;
}

.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.preview-content {
  background-color: white;
  border-radius: 0.5rem;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-body {
  padding: 1rem;
  overflow-y: auto;
  flex-grow: 1;
}

.preview-body pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: inherit;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  color: #6c757d;
}

.close-btn:hover {
  color: #000;
}

/* 文本样式 */
.text-break {
  word-break: break-word;
  hyphens: auto;
}

/* 自定义滚动条 */
.table-container::-webkit-scrollbar {
  width: 0.5rem;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 0.25rem;
}

.table-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 0.25rem;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .content-cell {
    max-height: 2.4em;
    -webkit-line-clamp: 2;
  }
}

/* 附件单元格样式 */
.attachments-cell {
  max-height: 1.2em;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

/* 搜索框容器 */
.search-container {
  display: flex;
  justify-content: flex-start;
}
</style> 