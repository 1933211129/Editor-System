<template>
  <div class="main-content">
    <h3>📄 通知文件自动生成</h3>
    
    <!-- 功能暂停访问遮罩 -->
    <div class="disabled-overlay">
      <div class="disabled-content">
        <i class="bi bi-exclamation-triangle-fill"></i>
        <h4>功能暂停访问</h4>
        <p>因资源占用较大，此功能暂时停止访问</p>
      </div>
    </div>
    
    <!-- 添加加载遮罩 -->
    <div class="loading-overlay" v-if="isGenerating">
      <div class="loading-content">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">文件正在生成，请稍候...</p>
      </div>
    </div>
    
    <div class="content-container">
      <!-- 左侧：文件模板预览编辑 -->
      <div class="template-section">
        <h4>文件模板预览编辑</h4>
        <div class="template-navigation">
          <button 
            class="nav-btn" 
            :disabled="currentTemplateIndex === 0"
            @click="currentTemplateIndex--"
          >
            <i class="bi bi-chevron-left"></i>
          </button>
          <span class="template-title">{{ templates[currentTemplateIndex].name }}</span>
          <button 
            class="nav-btn" 
            :disabled="currentTemplateIndex === templates.length - 1"
            @click="currentTemplateIndex++"
          >
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>
        
        <div class="template-editor">
          <textarea 
            v-model="templates[currentTemplateIndex].content"
            class="form-control"
            rows="20"
          ></textarea>
          <button class="btn btn-primary mt-3" @click="saveTemplate">
            <i class="bi bi-save"></i> 保存模板
          </button>
        </div>
      </div>

      <!-- 右侧：参数设置及文件生成 -->
      <div class="params-section">
        <h4>参数设置及文件生成</h4>
        
        <!-- 添加通知类型选择 -->
        <div class="task-type-selector mb-3">
          <label class="form-label">选择生成类型：</label>
          <div class="btn-group" role="group">
            <input type="radio" class="btn-check" name="task-type" id="task-type-all" 
                   v-model="taskType" value="A" autocomplete="off">
            <label class="btn btn-outline-primary" for="task-type-all">全部生成</label>

            <input type="radio" class="btn-check" name="task-type" id="task-type-accept" 
                   v-model="taskType" value="L" autocomplete="off">
            <label class="btn btn-outline-primary" for="task-type-accept">仅录用通知</label>

            <input type="radio" class="btn-check" name="task-type" id="task-type-charge" 
                   v-model="taskType" value="B" autocomplete="off">
            <label class="btn btn-outline-primary" for="task-type-charge">仅版面费通知</label>
          </div>
        </div>
        
        <div class="params-navigation">
          <button 
            class="nav-btn" 
            :disabled="currentParamsIndex === 0"
            @click="currentParamsIndex--"
          >
            <i class="bi bi-chevron-left"></i>
          </button>
          <span class="params-title">参数组 {{ currentParamsIndex + 1 }}/{{ paramsList.length }}</span>
          <button 
            class="nav-btn" 
            :disabled="currentParamsIndex === paramsList.length - 1"
            @click="currentParamsIndex++"
          >
            <i class="bi bi-chevron-right"></i>
          </button>
          <button 
            class="btn btn-danger btn-sm"
            @click="deleteCurrentParams"
            :disabled="paramsList.length === 1"
          >
            <i class="bi bi-trash"></i>
          </button>
        </div>

        <div class="params-form">
          <div class="form-group">
            <label>作者姓名（以分号分隔）</label>
            <input 
              type="text" 
              class="form-control"
              v-model="paramsList[currentParamsIndex].author_names"
              placeholder="例如：张三;李四;王五"
            >
          </div>
          <div class="form-group">
            <label>文章标题</label>
            <input 
              type="text" 
              class="form-control"
              v-model="paramsList[currentParamsIndex].paper_title"
            >
          </div>
          <div class="form-group">
            <label>文章编号</label>
            <input 
              type="text" 
              class="form-control"
              v-model="paramsList[currentParamsIndex].paper_id"
            >
          </div>
          <div class="form-group">
            <label>来稿日期</label>
            <input 
              type="date" 
              class="form-control"
              v-model="paramsList[currentParamsIndex].submit_date"
            >
          </div>
          <div class="form-group">
            <label>版面费</label>
            <input 
              type="number" 
              class="form-control"
              v-model="paramsList[currentParamsIndex].charge"
            >
          </div>
          <div class="form-group">
            <label>开具时间</label>
            <input 
              type="date" 
              class="form-control"
              v-model="paramsList[currentParamsIndex].time"
            >
          </div>
        </div>

        <div class="params-actions">
          <button class="btn btn-success" @click="addNewParams">
            <i class="bi bi-plus-circle"></i> 新增参数组
          </button>
          <button class="btn btn-primary" @click="generateDocuments">
            <i class="bi bi-file-earmark-text"></i> 生成文件
          </button>
        </div>
      </div>
    </div>

    <!-- 生成结果显示框（移到下方） -->
    <div class="result-section mt-4" v-if="generateResult || generatedFiles.length > 0">
      <h5>生成结果</h5>
      <div class="result-box" v-if="generateResult">
        {{ generateResult }}
      </div>
      <!-- 文件列表显示 -->
      <div class="generated-files" v-if="generatedFiles.length > 0">
        <div class="files-header">
          <h6>生成的文件列表：</h6>
          <button class="btn btn-primary" @click="downloadAllFiles">
            <i class="bi bi-download"></i> 批量下载
          </button>
        </div>
        <div class="file-list">
          <div v-for="file in generatedFiles" :key="file.path" class="file-item">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
            <button class="btn btn-sm btn-primary" @click="downloadFile(file)">
              <i class="bi bi-download"></i> 下载
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'NotificationGenerator',
  setup() {
    const templates = ref([
      { name: '版面费模板', path: 'charge_template.docx', content: '' },
      { name: '录用通知模板', path: 'accept_template.docx', content: '' }
    ])
    const currentTemplateIndex = ref(0)
    const currentParamsIndex = ref(0)
    const generateResult = ref('')

    // 参数列表，初始化一组空参数
    const paramsList = ref([{
      author_names: '',
      paper_title: '',
      paper_id: '',
      submit_date: '',
      charge: '',
      time: ''
    }])

    const generatedFiles = ref([])

    const taskType = ref('A') // 默认生成全部类型

    const isGenerating = ref(false)
    const hasDownloaded = ref(false)

    // 加载模板文件
    const loadTemplates = async () => {
      try {
        for (let template of templates.value) {
          const response = await axios.get('/api/template/load/', {
            params: {
              template: template.path
            }
          })
          if (response.data.status === 'success') {
            template.content = response.data.content
          } else {
            throw new Error(response.data.message)
          }
        }
      } catch (error) {
        console.error('加载模板失败:', error)
      }
    }

    // 保存模板
    const saveTemplate = async () => {
      try {
        const template = templates.value[currentTemplateIndex.value]
        await axios.post('/api/template/save/', {
          path: template.path,
          content: template.content
        })
        alert('模板保存成功')
      } catch (error) {
        console.error('保存模板失败:', error)
        alert('保存失败: ' + error.message)
      }
    }

    // 添加新的参数组
    const addNewParams = () => {
      paramsList.value.push({
        author_names: '',
        paper_title: '',
        paper_id: '',
        submit_date: '',
        charge: '',
        time: ''
      })
      currentParamsIndex.value = paramsList.value.length - 1
    }

    // 生成文件
    const generateDocuments = async () => {
      try {
        isGenerating.value = true
        hasDownloaded.value = false
        
        // 修正字段名
        const processedParams = paramsList.value.map(param => ({
          ...param,
          submmit_date: param.submit_date // 修正字段名
        }))
        
        const response = await axios.post('/api/notification/generate/', {
          params_list: processedParams,
          task_type: taskType.value
        })
        
        if (response.data.status === 'success') {
          generateResult.value = response.data.message
          generatedFiles.value = response.data.files
        } else {
          throw new Error(response.data.message)
        }
      } catch (error) {
        console.error('生成文件失败:', error)
        generateResult.value = '生成失败: ' + error.message
        generatedFiles.value = []
      } finally {
        isGenerating.value = false
      }
    }

    // 下载单个文件
    const downloadFile = async (file) => {
      try {
        if (hasDownloaded.value) {
          alert('您已下载文件，后端文件已自动删除，如若需要请再次生成。')
          return
        }
        
        const response = await axios.get(`/api/notification/download/${file.name}`, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', file.name)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        // 标记为已下载
        hasDownloaded.value = true
        
        // 清空后端文件
        await axios.post('/api/notification/clear_files/')
      } catch (error) {
        console.error('下载失败:', error)
        alert('下载失败: ' + error.message)
      }
    }

    // 批量下载所有文件
    const downloadAllFiles = async () => {
      if (hasDownloaded.value) {
        alert('您已下载文件，后端文件已自动删除，如若需要请再次生成。')
        return
      }
      
      try {
        for (const file of generatedFiles.value) {
          const response = await axios.get(`/api/notification/download/${file.name}`, {
            responseType: 'blob'
          })
          
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', file.name)
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        }
        
        // 标记为已下载
        hasDownloaded.value = true
        
        // 清空后端文件
        await axios.post('/api/notification/clear_files/')
      } catch (error) {
        console.error('批量下载失败:', error)
        alert('批量下载失败: ' + error.message)
      }
    }

    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    // 删除当前参数组
    const deleteCurrentParams = () => {
      if (paramsList.value.length > 1) {
        paramsList.value.splice(currentParamsIndex.value, 1)
        if (currentParamsIndex.value >= paramsList.value.length) {
          currentParamsIndex.value = paramsList.value.length - 1
        }
      }
    }

    onMounted(() => {
      loadTemplates()
    })

    return {
      templates,
      currentTemplateIndex,
      paramsList,
      currentParamsIndex,
      generateResult,
      saveTemplate,
      addNewParams,
      generateDocuments,
      deleteCurrentParams,
      generatedFiles,
      downloadFile,
      formatFileSize,
      taskType,
      isGenerating,
      hasDownloaded,
      downloadAllFiles
    }
  }
}
</script>

<style scoped>
.main-content {
  margin-left: 250px;
  padding: 20px;
}

.placeholder {
  text-align: center;
  padding: 50px;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 20px;
}

.content-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.template-section,
.params-section {
  flex: 1;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.template-navigation,
.params-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
  position: relative;
}

.nav-btn {
  border: none;
  background: none;
  color: #0d6efd;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
}

.nav-btn:disabled {
  color: #6c757d;
  cursor: not-allowed;
}

.template-title,
.params-title {
  font-weight: 500;
  color: #495057;
}

.template-editor textarea {
  width: 100%;
  font-family: monospace;
  resize: vertical;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #495057;
}

.params-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.result-section {
  margin-top: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.result-box {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  min-height: 100px;
  white-space: pre-wrap;
}

.params-navigation .btn-danger {
  position: absolute;
  right: 0;
  padding: 0.25rem 0.5rem;
}

.params-navigation .btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.files-header h6 {
  margin: 0;
}

.generated-files {
  margin-top: 20px;
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #dee2e6;
}

.file-item:last-child {
  border-bottom: none;
}

.file-name {
  flex: 1;
  margin-right: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  margin-right: 15px;
  color: #6c757d;
  font-size: 0.9em;
  white-space: nowrap;
}

.file-item .btn {
  padding: 2px 8px;
  font-size: 0.875rem;
}

.file-item .btn i {
  margin-right: 4px;
}

.task-type-selector {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.task-type-selector .form-label {
  margin-bottom: 10px;
  font-weight: 500;
}

.task-type-selector .btn-group {
  width: 100%;
}

.task-type-selector .btn {
  flex: 1;
  white-space: nowrap;
}

.btn-check:checked + .btn-outline-primary {
  background-color: #0d6efd;
  color: white;
}

/* 功能暂停访问遮罩 */
.disabled-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  backdrop-filter: blur(2px);
}

.disabled-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-width: 500px;
}

.disabled-content i {
  font-size: 64px;
  color: #ffc107;
  margin-bottom: 20px;
  display: block;
}

.disabled-content h4 {
  font-size: 24px;
  color: #495057;
  margin-bottom: 15px;
  font-weight: 600;
}

.disabled-content p {
  font-size: 16px;
  color: #6c757d;
  margin: 0;
}

/* 禁用所有交互元素 */
.main-content {
  pointer-events: none;
  opacity: 0.6;
}

.main-content * {
  pointer-events: none;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
  .content-container {
    grid-template-columns: 1fr;
  }
}
</style> 