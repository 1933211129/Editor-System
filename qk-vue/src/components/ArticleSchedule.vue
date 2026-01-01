<template>
  <div class="main-content">
    <h4>📅 文章预排期管理</h4>
    
    <!-- 保存状态提示 -->
    <div v-if="saveStatus" :class="['save-status', getSaveStatusClass]">
      {{ saveStatus }}
    </div>
    
    <!-- 顶部按钮组 -->
    <div class="mb-3 d-flex align-items-center gap-2">
      <button class="btn btn-primary" @click="triggerFileInput">
        <i class="bi bi-file-earmark-plus"></i> 导入新数据
      </button>
      <button class="btn btn-success" @click="addNewRow">
        <i class="bi bi-plus-circle"></i> 手动新增一行
      </button>
      <div v-if="selectedItems.length > 0" class="btn-group">
        <button class="btn btn-warning" @click="showBatchScheduleModal">
          <i class="bi bi-pencil"></i> 修改排期
        </button>
        <button class="btn btn-danger" @click="batchDelete">
          <i class="bi bi-trash"></i> 删除
        </button>
      </div>
      <button class="btn btn-success" @click="saveAllChanges">
        <i class="bi bi-save"></i> 保存修改
      </button>
      <select 
        class="form-select" 
        style="width: auto" 
        v-model="scheduleFilter"
      >
        <option value="">全部排期</option>
        <option v-for="schedule in uniqueSchedules" 
          :key="schedule" 
          :value="schedule"
        >
          {{ schedule || '未设置' }}
        </option>
      </select>
      <div class="search-box">
        <input
          type="text"
          class="form-control"
          placeholder="搜索任意字段..."
          v-model="searchKeyword"
        >
        <i class="bi bi-search"></i>
      </div>
      <input
        type="file"
        ref="fileInput"
        @change="handleFilesSelect"
        style="display: none"
        accept=".doc,.docx,.pdf,.txt"
        multiple
      >
    </div>

    <!-- 文章排期表格 -->
    <table class="table table-bordered mt-3">
      <thead class="table-light">
        <tr>
          <th style="width: 40px">
            <input 
              type="checkbox" 
              class="form-check-input"
              :checked="isAllSelected"
              @change="toggleAllSelection"
            >
          </th>
          <th style="width: 60px">#</th>
          <th>文件</th>
          <th>
            排期
            <button class="sort-btn" @click="toggleSort">
              {{ sortOrder === 'asc' ? '↑' : '↓' }}
            </button>
          </th>
          <th style="width: 160px">是否确认</th>
          <th>备注</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in filteredList" :key="item.id">
          <td>
            <input 
              type="checkbox" 
              class="form-check-input"
              v-model="selectedItems"
              :value="item.id"
            >
          </td>
          <td>
            {{ index + 1 }}
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.filename"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'filename', $event.target.value)"
              :class="{ 'saving': isSaving(item, 'filename') }"
            >
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.schedule"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'schedule', $event.target.value)"
              :class="{ 'saving': isSaving(item, 'schedule') }"
            >
          </td>
          <td>
            <select 
              v-model="item.confirmed" 
              class="form-select form-select-sm"
              @change="debounceSave(item, 'confirmed', $event.target.value)"
              :class="{ 'saving': isSaving(item, 'confirmed') }"
            >
              <option value="待更新">📝待更新</option>
              <option value="是">✅是</option>
              <option value="否">❌否</option>
            </select>
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.notes"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'notes', $event.target.value)"
              :class="{ 'saving': isSaving(item, 'notes') }"
            >
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 排期选择模态框 -->
    <div class="modal" tabindex="-1" ref="scheduleModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">选择排期</h5>
            <button type="button" class="btn-close" @click="hideScheduleModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <select class="form-select" v-model="selectedSchedule">
                <option value="">选择现有排期</option>
                <option v-for="schedule in uniqueSchedules" 
                  :key="schedule" 
                  :value="schedule"
                >
                  {{ schedule || '未设置' }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <div class="input-group">
                <input
                  type="text"
                  class="form-control"
                  placeholder="或输入新的排期"
                  v-model="newSchedule"
                >
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideScheduleModal">取消</button>
            <button type="button" class="btn btn-primary" @click="confirmSchedule">确定</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量修改排期模态框 -->
    <div class="modal" tabindex="-1" ref="batchScheduleModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">修改排期</h5>
            <button type="button" class="btn-close" @click="hideBatchScheduleModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <select class="form-select" v-model="batchSelectedSchedule">
                <option value="">选择现有排期</option>
                <option v-for="schedule in uniqueSchedules" 
                  :key="schedule" 
                  :value="schedule"
                >
                  {{ schedule || '未设置' }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <div class="input-group">
                <input
                  type="text"
                  class="form-control"
                  placeholder="或输入新的排期"
                  v-model="batchNewSchedule"
                >
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideBatchScheduleModal">取消</button>
            <button type="button" class="btn btn-primary" @click="confirmBatchSchedule">确定</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const articleList = ref([])
const fileInput = ref(null)
const searchKeyword = ref('')
const scheduleFilter = ref('')
const saveStatus = ref('')
// let saveTimeout = null
const savingFields = ref(new Map()) // 记录正在保存的字段
const sortOrder = ref('asc')
const scheduleModal = ref(null)
const selectedSchedule = ref('')
const newSchedule = ref('')
const currentAction = ref('') // 'batch' 或 'single'

// 获取所有唯一的排期值
const uniqueSchedules = computed(() => {
  const schedules = new Set(articleList.value.map(item => item.schedule))
  return Array.from(schedules).sort()
})

// 先按排期筛选，再按关键字搜索
const filteredList = computed(() => {
  let filtered = articleList.value
  
  // 排期筛选
  if (scheduleFilter.value) {
    filtered = filtered.filter(item => item.schedule === scheduleFilter.value)
  }
  
  // 关键字搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(item => {
      return Object.values(item).some(value => 
        String(value).toLowerCase().includes(keyword)
      )
    })
  }
  return filtered
})

// 从后端加载数据
const loadData = async () => {
  try {
    const response = await axios.get('/api/schedule/data/')
    articleList.value = response.data
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})

// 计算保存状态的样式类
const getSaveStatusClass = computed(() => {
  if (saveStatus.value.includes('失败')) return 'error'
  if (saveStatus.value === '已保存') return 'saved'
  return 'saving'
})

// 检查字段是否正在保存
const isSaving = (item, field) => {
  const key = `${item.id}-${field}`
  return savingFields.value.has(key)
}

// 用于存储未保存的修改
const pendingChanges = ref(new Map())

// 修改输入处理函数，不再立即保存
const debounceSave = (item, field, value) => {
  try {
    const key = `${item.id}-${field}`
    pendingChanges.value.set(key, { id: item.id, field, value })
    saveStatus.value = '❌有未保存的修改'
  } catch (error) {
    console.error('保存失败:', error)
    saveStatus.value = '保存失败'
  }
}

// 添加保存所有修改的函数
const saveAllChanges = async () => {
  try {
    if (pendingChanges.value.size === 0) {
      saveStatus.value = '没有需要保存的修改'
      return
    }
    
    saveStatus.value = '保存中...'
    const promises = []
    
    for (const change of pendingChanges.value.values()) {
      const { id, field, value } = change
      promises.push(
        axios.post('/api/schedule/update/', {
          id,
          field,
          value
        })
      )
    }
    
    await Promise.all(promises)
    pendingChanges.value.clear()
    saveStatus.value = '已保存'
    
    setTimeout(() => {
      if (saveStatus.value === '已保存') {
        saveStatus.value = ''
      }
    }, 2000)
  } catch (error) {
    console.error('保存失败:', error)
    saveStatus.value = '保存失败: ' + error.message
  }
}

// 显示排期选择模态框
const showScheduleModal = (action) => {
  currentAction.value = action
  selectedSchedule.value = ''
  newSchedule.value = ''
  scheduleModal.value.style.display = 'block'
  scheduleModal.value.classList.add('show')
}

// 隐藏排期选择模态框
const hideScheduleModal = () => {
  scheduleModal.value.style.display = 'none'
  scheduleModal.value.classList.remove('show')
}

// 确认排期选择
const confirmSchedule = () => {
  const schedule = newSchedule.value || selectedSchedule.value
  if (!schedule) {
    alert('请选择或输入排期')
    return
  }
  
  hideScheduleModal()
  if (currentAction.value === 'batch') {
    fileInput.value.click()
  } else {
    createNewRow(schedule)
  }
}

// 实际创建新行的函数
const createNewRow = async (schedule) => {
  try {
    const response = await axios.post('/api/schedule/create/', {
      filename: '',
      schedule: schedule,
      confirmed: '待更新',
      notes: ''
    })
    if (response.data.status === 'success') {
      await loadData()
    } else {
      console.error('新增行失败:', response.data.message)
    }
  } catch (error) {
    console.error('新增行失败:', error)
  }
}

// 修改文件选择处理函数
const handleFilesSelect = async (event) => {
  const files = event.target.files
  if (!files.length) return
  
  try {
    saveStatus.value = '添加中...'
    const schedule = newSchedule.value || selectedSchedule.value
    
    for (const file of files) {
      const filename = file.name.replace(/\.[^/.]+$/, "")
      
      const response = await axios.post('/api/schedule/create/', {
        filename,
        schedule: schedule,
        confirmed: '待更新',
        notes: ''
      })
      
      if (response.data.status === 'success') {
        articleList.value.unshift({
          id: response.data.id,
          filename,
          schedule: schedule,
          confirmed: '待更新',
          notes: ''
        })
      }
    }
    
    saveStatus.value = '添加成功'
    setTimeout(() => {
      if (saveStatus.value === '添加成功') saveStatus.value = ''
    }, 2000)
    
    // 清空文件输入，以便可以重复选择同一文件
    event.target.value = ''
  } catch (error) {
    console.error('添加失败:', error)
    saveStatus.value = '添加失败: ' + error.message
  }
}

// 修改触发文件选择函数
const triggerFileInput = () => {
  showScheduleModal('batch')
}

// 修改新增行函数
const addNewRow = () => {
  showScheduleModal('single')
}

// 排序切换方法
const toggleSort = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  sortDataList()
}

// 排序方法
const sortDataList = () => {
  articleList.value.sort((a, b) => {
    const scheduleA = a.schedule || ''
    const scheduleB = b.schedule || ''
    const result = scheduleA.localeCompare(scheduleB, 'zh-CN')
    return sortOrder.value === 'asc' ? result : -result
  })
}

// 多选相关
const selectedItems = ref([])
const batchScheduleModal = ref(null)
const batchSelectedSchedule = ref('')
const batchNewSchedule = ref('')

// 计算是否全选
const isAllSelected = computed(() => {
  return filteredList.value.length > 0 && 
    selectedItems.value.length === filteredList.value.length
})

// 切换全选
const toggleAllSelection = () => {
  if (isAllSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = filteredList.value.map(item => item.id)
  }
}

// 显示批量修改排期模态框
const showBatchScheduleModal = () => {
  batchSelectedSchedule.value = ''
  batchNewSchedule.value = ''
  batchScheduleModal.value.style.display = 'block'
  batchScheduleModal.value.classList.add('show')
}

// 隐藏批量修改排期模态框
const hideBatchScheduleModal = () => {
  batchScheduleModal.value.style.display = 'none'
  batchScheduleModal.value.classList.remove('show')
}

// 确认批量修改排期
const confirmBatchSchedule = async () => {
  const schedule = batchNewSchedule.value || batchSelectedSchedule.value
  if (!schedule) {
    alert('请选择或输入排期')
    return
  }
  
  try {
    saveStatus.value = '保存中...'
    const promises = selectedItems.value.map(id => 
      axios.post('/api/schedule/update/', {
        id,
        field: 'schedule',
        value: schedule
      })
    )
    
    await Promise.all(promises)
    await loadData()
    selectedItems.value = []
    hideBatchScheduleModal()
    saveStatus.value = '已保存'
  } catch (error) {
    console.error('批量修改失败:', error)
    saveStatus.value = '保存失败'
  }
}

// 批量删除
const batchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedItems.value.length} 条记录吗？此操作不可恢复！`)) {
    return
  }
  
  try {
    const promises = selectedItems.value.map(id =>
      axios.post('/api/schedule/delete/', { id })
    )
    
    await Promise.all(promises)
    await loadData()
    selectedItems.value = []
  } catch (error) {
    console.error('批量删除失败:', error)
  }
}
</script>

<style scoped>
.main-content {
  margin-left: 250px;
  padding: 20px;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  white-space: nowrap;
}

.table td {
  vertical-align: middle;
}

/* 搜索框样式 */
.search-box {
  position: relative;
  width: 250px;
}

.search-box input {
  padding-right: 30px;
}

.search-box i {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

/* 按钮图标样式 */
.btn i {
  margin-right: 5px;
}

/* 导入按钮组样式 */
.btn-primary + .btn-primary {
  margin-left: -1px;  /* 让两个导入按钮紧贴 */
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
}

/* 排期筛选下拉框样式 */
.form-select {
  min-width: 120px;
  background-color: #fff;
}

.form-select option:first-child {
  font-weight: bold;
}

/* 未设置排期的选项样式 */
.form-select option[value=""] {
  color: #6c757d;
  font-style: italic;
}

/* 保存状态提示样式 */
.save-status {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 10px 20px;
  border-radius: 4px;
  z-index: 1000;
  transition: all 0.3s ease;
}

.saving {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}

.saved {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 正在保存的输入框样式 */
input.saving,
select.saving {
  background-color: #fff3cd !important;
  border-color: #ffeeba !important;
}

.sort-btn {
  border: none;
  background: none;
  padding: 0 4px;
  cursor: pointer;
}

.sort-btn:hover {
  color: #0d6efd;
}

/* 修改未保存提示的样式 */
.save-status:contains('有未保存的修改') {
  color: #dc3545;
  font-weight: bold;
  background-color: #fff3cd;
  border: 2px solid #dc3545;
}

/* 模态框样式 */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal.show {
  display: block;
}

/* 多选框样式 */
.form-check-input {
  cursor: pointer;
}

/* 批量操作按钮组样式 */
.btn-group {
  display: flex;
  gap: 8px;
}
</style> 