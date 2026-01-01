<template>
  <div class="main-content">
    <h3>📑 邮件模板管理</h3>
    
    <!-- 添加新模板按钮 -->
    <div class="mb-4">
      <button class="btn btn-primary" @click="showAddModal">
        <i class="bi bi-plus-circle"></i> 新建模板
      </button>
    </div>

    <!-- 模板列表 -->
    <div class="template-table">
      <table class="table table-hover">
        <thead class="table-light">
          <tr>
            <th style="width: 80px">#</th>
            <th style="width: 200px">模板标题</th>
            <th>模板内容</th>
            <th style="width: 200px">创建时间</th>
            <th style="width: 100px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(template, index) in templates" :key="template.id">
            <td>{{ index + 1 }}</td>
            <td>{{ template.title }}</td>
            <td>
              <div class="template-content" v-html="template.content"></div>
            </td>
            <td>{{ formatTime(template.updateTime) }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-2" @click="editTemplate(template)">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteTemplate(template.id)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 编辑模板对话框 -->
    <div class="modal" tabindex="-1" ref="templateModal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? '编辑模板' : '新建模板' }}</h5>
            <button type="button" class="btn-close" @click="hideModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">模板标题</label>
              <input type="text" class="form-control" v-model="currentTemplate.title" placeholder="请输入模板标题">
            </div>
            <div class="mb-3">
              <label class="form-label">模板内容</label>
              <div class="editor-container">
                <!-- 变量插入按钮 -->
                <div class="variable-toolbar">
                  <span class="toolbar-label">快速插入变量：</span>
                  <button type="button" class="btn btn-sm btn-outline-primary" @click="insertVariable('{{姓名}}')" title="插入姓名变量">
                    &#123;&#123;姓名&#125;&#125;
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-primary" @click="insertVariable('{{邮箱}}')" title="插入邮箱变量">
                    &#123;&#123;邮箱&#125;&#125;
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-primary" @click="insertVariable('{{日期}}')" title="插入日期变量">
                    &#123;&#123;日期&#125;&#125;
                  </button>
                </div>
                <!-- Quill编辑器 -->
                <div ref="quillEditor" class="quill-editor"></div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideModal">取消</button>
            <button type="button" class="btn btn-primary" @click="saveTemplate">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  date.setHours(date.getHours() + 8)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
/* global defineExpose */

import { ref, onMounted, nextTick } from 'vue'

// 模板列表
const templates = ref([])
// 当前编辑的模板
const currentTemplate = ref({
  id: '',
  title: '',
  content: '',
  createTime: ''
})
// 是否处于编辑状态
const isEditing = ref(false)
// 模态框引用
const templateModal = ref(null)
// Quill编辑器引用
const quillEditor = ref(null)
// Quill实例
let quillInstance = null

// 组件挂载时加载数据
onMounted(() => {
  // 动态加载Quill.js
  loadQuillJS()
  // 加载模板数据
  loadTemplates()
})

// 动态加载Quill.js
const loadQuillJS = () => {
  // 检查是否已经加载
  if (window.Quill) {
    return
  }
  
  // 加载CSS
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = 'https://cdn.quilljs.com/1.3.6/quill.snow.css'
  document.head.appendChild(link)
  
  // 加载JS
  const script = document.createElement('script')
  script.src = 'https://cdn.quilljs.com/1.3.6/quill.min.js'
  script.onload = () => {
    console.log('Quill.js loaded successfully')
  }
  document.head.appendChild(script)
}

// 显示添加模板对话框
const showAddModal = () => {
  isEditing.value = false
  currentTemplate.value = {
    id: Date.now().toString(),
    title: '',
    content: '',
    createTime: new Date().toLocaleString()
  }
  showModal()
}

// 显示编辑模板对话框
const editTemplate = (template) => {
  isEditing.value = true
  currentTemplate.value = { ...template }
  showModal()
}

// 保存模板
const saveTemplate = async () => {
  if (!currentTemplate.value.title.trim()) {
    alert('请输入模板标题')
    return
  }
  
  console.log('开始保存模板...')
  
  try {
    const templateData = {
      title: currentTemplate.value.title,
      content: currentTemplate.value.content
    }
    
    console.log('模板数据:', templateData)
    
    let response
    let url
    if (isEditing.value) {
      // 更新现有模板
      url = `/api/email-templates/${currentTemplate.value.id}/update/`
      console.log('发送PUT请求到:', url)
      response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData)
      })
    } else {
      // 创建新模板
      url = '/api/email-templates/create/'
      console.log('发送POST请求到:', url)
      response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData)
      })
    }
    
    console.log('响应状态:', response.status)
    console.log('响应头:', response.headers)
    
    if (!response.ok) {
      console.error('HTTP错误:', response.status, response.statusText)
      alert(`请求失败: ${response.status} ${response.statusText}`)
      return
    }
    
    const result = await response.json()
    console.log('响应结果:', result)
    
    if (result.status === 'success') {
      hideModal()
      // 重置表单
      currentTemplate.value = {
        id: '',
        title: '',
        content: '',
        createTime: ''
      }
      isEditing.value = false
      loadTemplates() // 重新加载模板列表
    } else {
      alert(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存模板失败:', error)
    alert('保存失败，请重试')
  }
}

// 删除模板
const deleteTemplate = async (id) => {
  if (confirm('确定要删除这个模板吗？')) {
    try {
      const response = await fetch(`/api/email-templates/${id}/delete/`, {
        method: 'DELETE'
      })
      
      const result = await response.json()
      
      if (result.status === 'success') {
        loadTemplates() // 重新加载模板列表
      } else {
        alert(result.message || '删除失败')
      }
    } catch (error) {
      console.error('删除模板失败:', error)
      alert('删除失败，请重试')
    }
  }
}

// 初始化Quill编辑器
const initQuillEditor = () => {
  if (!window.Quill || !quillEditor.value) return
  
  // 销毁现有实例
  if (quillInstance) {
    try {
      quillInstance.off('text-change')
      const toolbar = quillEditor.value.previousElementSibling
      if (toolbar && toolbar.classList.contains('ql-toolbar')) {
        toolbar.remove()
      }
    } catch (e) {
      console.log('清理Quill实例时出错:', e)
    }
    quillInstance = null
  }
  
  // 清空编辑器容器
  quillEditor.value.innerHTML = ''
  
  // 创建新的Quill实例
  quillInstance = new window.Quill(quillEditor.value, {
    theme: 'snow',
    placeholder: '请输入邮件模板内容...',
    modules: {
      toolbar: [
        [{ 'header': [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'align': [] }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        ['link'],
        ['clean']
      ]
    }
  })
  
  // 监听内容变化
  quillInstance.on('text-change', () => {
    currentTemplate.value.content = quillInstance.root.innerHTML
  })
  
  // 设置初始内容
  if (currentTemplate.value.content) {
    quillInstance.root.innerHTML = currentTemplate.value.content
  }
}

// 显示模态框
const showModal = async () => {
  templateModal.value.style.display = 'block'
  templateModal.value.classList.add('show')
  
  // 等待DOM更新后初始化编辑器
  await nextTick()
  
  // 等待Quill加载完成
  const waitForQuill = () => {
    if (window.Quill) {
      initQuillEditor()
    } else {
      setTimeout(waitForQuill, 100)
    }
  }
  waitForQuill()
}

// 隐藏模态框
const hideModal = () => {
  templateModal.value.style.display = 'none'
  templateModal.value.classList.remove('show')
  
  // 清理Quill实例
  if (quillInstance) {
    try {
      quillInstance.off('text-change')
      const toolbar = quillEditor.value.previousElementSibling
      if (toolbar && toolbar.classList.contains('ql-toolbar')) {
        toolbar.remove()
      }
    } catch (e) {
      console.log('清理Quill实例时出错:', e)
    }
    quillInstance = null
  }
}

// 加载模板列表
const loadTemplates = async () => {
  console.log('开始加载模板列表...')
  try {
    const response = await fetch('/api/email-templates/')
    console.log('模板列表响应状态:', response.status)
    
    if (!response.ok) {
      console.error('HTTP错误:', response.status, response.statusText)
      return
    }
    
    const result = await response.json()
    console.log('模板列表响应结果:', result)
    
    if (result.status === 'success') {
      templates.value = result.data
      console.log('模板列表加载成功，数量:', result.data.length)
    } else {
      console.error('加载模板失败:', result.message)
    }
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

// 向父组件暴露刷新方法
defineExpose({
  refresh: () => {
    loadTemplates()
  }
})

// 插入变量到Quill编辑器
const insertVariable = (variable) => {
  if (!quillInstance) return
  
  const range = quillInstance.getSelection()
  if (range) {
    // 在当前光标位置插入变量
    quillInstance.insertText(range.index, variable, {
      'background': '#e3f2fd',
      'color': '#1976d2',
      'bold': true
    })
    
    // 移动光标到变量后面
    quillInstance.setSelection(range.index + variable.length)
  } else {
    // 如果没有选择，在末尾插入
    const length = quillInstance.getLength()
    quillInstance.insertText(length - 1, variable, {
      'background': '#e3f2fd',
      'color': '#1976d2',
      'bold': true
    })
  }
}
</script>

<style scoped>
.template-content {
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

/* 编辑器样式 */
.editor-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

/* 变量工具栏样式 */
.variable-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
  flex-wrap: wrap;
}

.toolbar-label {
  font-size: 14px;
  color: #495057;
  font-weight: 500;
  margin-right: 8px;
}

/* Quill编辑器样式 */
.quill-editor {
  min-height: 300px;
}

/* 覆盖Quill默认样式 */
:deep(.ql-editor) {
  min-height: 300px;
  font-size: 14px;
  line-height: 1.6;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

:deep(.ql-toolbar) {
  border-top: none;
  border-left: none;
  border-right: none;
  border-bottom: 1px solid #ccc;
}

:deep(.ql-container) {
  border-left: none;
  border-right: none;
  border-bottom: none;
}

/* 其他样式保持与 EmailManage.vue 一致 */
.main-content {
  margin-left: 250px;
  padding: 20px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
  
  .editor-toolbar {
    padding: 8px;
    gap: 4px;
  }
  
  .toolbar-group {
    gap: 2px;
  }
  
  .toolbar-btn {
    width: 28px;
    height: 28px;
    font-size: 11px;
  }
  
  .editor-content {
    min-height: 250px;
    padding: 12px;
  }
}

/* 表格样式优化 */
.template-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table {
  margin-bottom: 0;
}

.table th {
  background: #f8f9fa;
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.table td {
  vertical-align: middle;
}

/* 按钮样式优化 */
.btn {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style> 