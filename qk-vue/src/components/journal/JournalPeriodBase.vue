<template>
  <div class="journal-period">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4>📝{{ periodTitle }}</h4>
      <div class="page-actions">
        <button class="btn btn-danger btn-sm" @click="openUpdateLog" v-show="true">更新日志</button>
      </div>
    </div>
    
    <!-- 右上角版次提示 -->
    <div v-if="!currentEdition" class="edition-warning-alert">
      <i class="bi bi-exclamation-triangle"></i> 未设置版次信息
    </div>
      
      <!-- 在表格上方添加文件导入按钮 -->
      <div class="mb-3 d-flex align-items-center">
        <!-- 修改按钮组的顺序 -->
        <div class="me-3">
          <button class="btn btn-outline-primary me-2" @click="showOptionsModal('responsible')">
            <i class="bi bi-gear"></i> 责编选项管理
          </button>
          <button class="btn btn-outline-primary me-2" @click="showOptionsModal('editor')">
            <i class="bi bi-gear"></i> 编辑选项管理
          </button>
        </div>
        
        <!-- 修改文件导入按钮部分 -->
        <div class="d-flex gap-2">
          <button class="btn btn-primary" @click="addNewRow" :disabled="isImporting">
            <i class="bi bi-plus-circle"></i> 添加新行
          </button>
          <button class="btn btn-primary" @click="triggerFileInput" :disabled="isImporting">
            <i class="bi bi-folder-plus"></i> 导入文件
          </button>
          <button class="btn btn-success" @click="triggerAppendFileInput" :disabled="isImporting">
            <i class="bi bi-file-earmark-plus"></i> 追加文件
          </button>
          <button class="btn btn-danger" @click="clearAllData" :disabled="isImporting">
            <i class="bi bi-trash"></i> 一键清空
          </button>
          <button class="btn btn-success" @click="saveAllChanges" :disabled="isImporting">
            <i class="bi bi-save"></i> 保存修改
          </button>
          <button class="btn btn-outline-info" @click="showEditionModal" :disabled="isImporting">
            <i class="bi bi-calendar3"></i> 版次设置
          </button>
          <span v-if="currentEdition" class="edition-display-badge">
            <i class="bi bi-calendar-check"></i> {{ currentEdition }}
          </span>
          <input
            type="file"
            ref="fileInput"
            multiple
            @change="handleFileImport"
            style="display: none"
            accept=".doc,.docx,.pdf,.txt"
            :disabled="isImporting"
          >
          <input
            type="file"
            ref="appendFileInput"
            multiple
            @change="handleAppendFileImport"
            style="display: none"
            accept=".doc,.docx,.pdf,.txt"
            :disabled="isImporting"
          >
        </div>
      </div>

      <!-- 添加导入进度提示 -->
      <div v-if="isImporting" class="import-progress">
        <div class="spinner-border spinner-border-sm me-2" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <span>正在导入文件，请稍候...</span>
      </div>
  
      <table class="table table-bordered mt-3">
        <thead class="table-light">
          <tr>
            <th>#</th>
            <th>
              文件
              <button class="sort-btn" @click="toggleSort">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </button>
            </th>
            <th>
              责编
              <input type="text" class="date-input" v-model="proofDates.editor" placeholder="月-日" 
                @input="handleDateChange('editor', $event.target.value)">
            </th>
            <th>
              版面费
              <select class="batch-select" @change="batchUpdate($event.target.value, 'stages.fee')">
                <option value="">批量设置</option>
                <option v-for="status in statusOptions" :key="status.value" :value="status.value">
                  {{ status.emoji }} {{ status.label }}
                </option>
              </select>
            </th>
            <th>
              校对情况 <input type="text" class="date-input" v-model="proofDates.proof" placeholder="月-日"
                @input="handleDateChange('proof', $event.target.value)">
              <select class="batch-select" @change="batchUpdate($event.target.value, 'stages.proof')">
                <option value="">批量设置</option>
                <option v-for="status in statusOptions" :key="status.value" :value="status.value">
                  {{ status.emoji }} {{ status.label }}
                </option>
              </select>
            </th>
            <th>
              一、二校编辑
              <select class="batch-select" @change="batchUpdate($event.target.value, 'editors.proof12')">
                <option value="">批量设置</option>
                <option v-for="option in editorOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </th>
            <th>
              三校编辑
              <select class="batch-select" @change="batchUpdate($event.target.value, 'editors.proof3')">
                <option value="">批量设置</option>
                <option v-for="option in editorOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </th>
            <th>
              终校编辑
              <select class="batch-select" @change="batchUpdate($event.target.value, 'editors.proofFinal')">
                <option value="">批量设置</option>
                <option v-for="option in editorOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in dataList" :key="item.id">
            <td>
              {{ index + 1 }}
            </td>
            <td>
              <div class="editable-cell">
                <input 
                  type="text" 
                  v-model="item.title"
                  class="form-control form-control-sm"
                  @blur="handleInputChange(item.id, 'title', item.title)"
                >
              </div>
            </td>
            <td>
              <select 
                v-model="item.responsible" 
                class="status-select"
                @change="handleInputChange(item.id, 'responsible', $event.target.value)"
              >
                <option value="">请选择</option>
                <option v-for="option in responsibleOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </td>
            <td>
              <select 
                v-model="item.stages.fee" 
                class="status-select"
                @change="handleInputChange(item.id, 'stages.fee', $event.target.value)"
              >
                <option v-for="status in statusOptions" :key="status.value" :value="status.value">
                  {{ status.emoji }} {{ status.label }}
                </option>
              </select>
            </td>
            <td>
              <select 
                v-model="item.stages.proof" 
                class="status-select"
                @change="handleInputChange(item.id, 'stages.proof', $event.target.value)"
              >
                <option v-for="status in statusOptions" :key="status.value" :value="status.value">
                  {{ status.emoji }} {{ status.label }}
                </option>
              </select>
            </td>
            <td>
              <select 
                v-model="item.editors.proof12" 
                class="status-select"
                @change="handleInputChange(item.id, 'editors.proof12', $event.target.value)"
              >
                <option value="">请选择</option>
                <option v-for="option in editorOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </td>
            <td>
              <select 
                v-model="item.editors.proof3" 
                class="status-select"
                @change="handleInputChange(item.id, 'editors.proof3', $event.target.value)"
              >
                <option value="">请选择</option>
                <option v-for="option in editorOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </td>
            <td>
              <select 
                v-model="item.editors.proofFinal" 
                class="status-select"
                @change="handleInputChange(item.id, 'editors.proofFinal', $event.target.value)"
              >
                <option value="">请选择</option>
                <option v-for="option in editorOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </td>
            <td>
              <input type="text" class="form-control form-control-sm"
                v-model="item.remarks"
                @input="handleInputChange(item.id, 'remarks', $event.target.value)"
                placeholder="">
            </td>
            <td class="text-center">
              <button class="btn btn-outline-danger btn-sm delete-btn" @click="deleteRow(index)" title="删除此行">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
  
      <!-- 选项管理模态框 -->
      <div class="modal" tabindex="-1" ref="optionsModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">{{ modalTitle }}</h5>
              <button type="button" class="btn-close" @click="hideOptionsModal"></button>
            </div>
            <div class="modal-body">
              <div>
                <div class="mb-3">
                  <label class="form-label">添加新选项</label>
                  <div class="input-group">
                    <input type="text" class="form-control" v-model="newOption">
                    <button class="btn btn-primary" @click="addOption">添加</button>
                  </div>
                </div>
                
                <!-- 添加序号批量设置部分 -->
                <div class="mb-3">
                  <label class="form-label">按序号批量设置</label>
                  <div class="input-group">
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="batchNumbers"
                      placeholder="输入序号，如：1,2,3"
                    >
                    <select class="form-select" v-model="selectedOption">
                      <option value="">选择{{ currentOptionType === 'editor' ? '编辑' : '责编' }}</option>
                      <option v-for="option in currentOptions" :key="option" :value="option">
                        {{ option }}
                      </option>
                    </select>
                    <button class="btn btn-primary" @click="batchSetByNumbers">应用</button>
                  </div>
                  <div class="form-text">输入序号并用逗号分隔，如：1,2,3</div>
                </div>
  
                <div class="form-check mb-3">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    v-model="applyToAll" 
                    :id="'apply' + currentOptionType + 'ToAll'"
                  >
                  <label class="form-check-label" :for="'apply' + currentOptionType + 'ToAll'">
                    应用到所有记录
                  </label>
                </div>
  
                <div class="current-options">
                  <div v-for="option in currentOptions" :key="option" class="option-item">
                    {{ option }}
                    <button class="btn btn-sm btn-danger" @click="removeOption(option)">×</button>
                  </div>
                </div>
  
                <!-- 选择要应用的选项 -->
                <div class="mb-3" v-if="applyToAll">
                  <label class="form-label">选择要应用的选项</label>
                  <select class="form-select" v-model="selectedOption">
                    <option value="">请选择</option>
                    <option v-for="option in currentOptions" :key="option" :value="option">
                      {{ option }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="hideOptionsModal">取消</button>
              <button type="button" class="btn btn-primary" @click="saveOptions">保存</button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 添加保存状态提示 -->
      <div v-if="saveStatus" class="save-status" :class="{ 
        'saving': saveStatus === '保存中...', 
        'saved': saveStatus === '已保存',
        'error': saveStatus === '保存失败'
      }">
        {{ saveStatus }}
      </div>
    </div>
    <!-- 版次设置弹窗 -->
    <div class="modal" tabindex="-1" ref="editionModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">设置版次</h5>
            <button type="button" class="btn-close" @click="hideEditionModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">年份</label>
              <input 
                type="number" 
                class="form-control" 
                v-model.number="editionYear" 
                placeholder="例如：2024"
                min="2000"
                max="2100"
                ref="editionYearRef"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">月份</label>
              <input 
                type="number" 
                class="form-control" 
                v-model.number="editionMonth" 
                placeholder="例如：1"
                min="1"
                max="100"
              >
            </div>
            <div class="text-muted">
              <small>当前版次：{{ currentEdition || '未设置' }}</small>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideEditionModal">取消</button>
            <button type="button" class="btn btn-primary" @click="saveEdition" :disabled="isSavingEdition || !editionYear || !editionMonth">
              <span v-if="isSavingEdition" class="spinner-border spinner-border-sm me-2"></span>
              保存
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 更新日志弹窗 -->
    <div class="modal" tabindex="-1" ref="updateLogModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">更新日志</h5>
            <button type="button" class="btn-close" @click="hideUpdateLog"></button>
          </div>
          <div class="modal-body">
            <div v-if="updateLog">
              <div class="text-muted mb-2">更新时间：{{ updateLog.updatedAt }}</div>
              <pre style="white-space:pre-wrap; word-break:break-word;">{{ updateLog.content }}</pre>
            </div>
            <div v-else class="text-muted">暂无更新日志</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideUpdateLog">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch, defineProps, computed } from 'vue'
  import axios from 'axios'
  
  // Props 定义
  const props = defineProps({
    displayPeriod: {
      type: Number,
      required: true
    },
    backendPeriod: {
      type: Number,
      required: true
    }
  })
  
  // 响应式变量定义
  const periodTitle = computed(() => `第${props.displayPeriod}期进度管理`)
  const dataList = ref([])
  const saveStatus = ref('')
  const editorOptions = ref(['孙航', '李彦燕', '陈玉忠', '孔源博'])
  const responsibleOptions = ref([])
  const optionsModal = ref(null)
  const currentOptionType = ref('')
  const modalTitle = ref('')
  const newOption = ref('')
  const currentOptions = ref([])
  const fileInput = ref(null)
  const batchNumbers = ref('')
  const selectedOption = ref('')
  const sortOrder = ref('asc')
  const applyToAll = ref(false)  // 是否应用到所有记录
  const appendFileInput = ref(null)
  const isImporting = ref(false)  // 导入状态
  const updateLogModal = ref(null)
  const updateLog = ref(null)
  const currentEdition = ref('')  // 当前版次
  const editionModal = ref(null)  // 版次弹窗引用
  const editionYear = ref(null)  // 版次年份
  const editionMonth = ref(null)  // 版次月份
  const isSavingEdition = ref(false)  // 是否正在保存版次
  const editionYearRef = ref(null)  // 年份输入框引用
  
  // 用于存储未保存的修改
  const pendingChanges = ref(new Map())
  
  // 常量定义
  const statusOptions = [
    { value: '待更新', label: '待更新', emoji: '📝' },
    { value: '未完成', label: '未完成', emoji: '❌' },
    { value: '进行中', label: '进行中', emoji: '⏳' },
    { value: '已完成', label: '已完成', emoji: '✅' }
  ]
  
  // 修改输入处理函数，不再立即保存
  const handleInputChange = (id, field, value) => {
    const key = `${id}-${field}`
    pendingChanges.value.set(key, { id, field, value })
    saveStatus.value = '❌有未保存的修改'
  }
  
  // 添加新行的方法
  const addNewRow = async () => {
    try {
      saveStatus.value = '保存中...'
      
      const newRow = {
        title: "",
        responsible: "",
        stages: {
          fee: "待更新",
          proof: "待更新"
        },
        editors: {
          proof12: "",
          proof3: "",
          proofFinal: ""
        },
        remarks: ""
      }
      
      const response = await axios.post(`/api/journal/${props.backendPeriod}/create/`, newRow)
      
      if (response.data.status === 'success') {
        const newItem = {
          id: response.data.id,
          title: "",
          responsible: "",
          remarks: "",  // 添加备注字段
          stages: {
            fee: "待更新",
            proof: "待更新"
          },
          editors: {
            proof: ""
          },
          proofDates: { ...proofDates.value },  // 使用当前表头的时间值
          edition: currentEdition.value || ''  // 使用当前版次
        }
        dataList.value.unshift(newItem)  // 在数组开头添加新行
        saveStatus.value = '已保存'
      } else {
        throw new Error(response.data.message || '创建失败')
      }
    } catch (error) {
      console.error('创建新行失败:', error)
      saveStatus.value = '保存失败'
    }
  }
  
  // 组件挂载时的处理
  onMounted(async () => {
    try {
      // 确保更新日志按钮显示
      console.log('组件挂载，props:', { displayPeriod: props.displayPeriod, backendPeriod: props.backendPeriod })
      
      // 加载数据
      const response = await axios.get(`/api/journal/${props.backendPeriod}/data/`)
      console.log('1. 后端原始数据:', response.data)
      
      // 处理返回数据（数组格式）
      let responseData = response.data
      if (response.data && Array.isArray(response.data)) {
        responseData = response.data
        // 从第一条记录获取版次
        if (responseData.length > 0 && responseData[0].edition) {
          currentEdition.value = responseData[0].edition
        } else {
          currentEdition.value = ''
        }
      }
      
      if (responseData && Array.isArray(responseData)) {
        // 收集所有不重复的责编选项
        const uniqueResponsibles = new Set()
        responseData.forEach(item => {
          if (item.responsible) {
            uniqueResponsibles.add(item.responsible)
          }
        })
        // 更新责编选项
        responsibleOptions.value = Array.from(uniqueResponsibles)
        console.log('责编选项:', responsibleOptions.value)
  
        dataList.value = responseData.map(item => {
          const mappedItem = {
            id: parseInt(item.id),
            title: item.title || '',
            responsible: item.responsible || '',
            remarks: item.remarks || '',
            stages: {
              fee: item.stages?.fee || '待更新',
              proof: item.stages?.proof || item.stages?.proof1 || item.stages?.proof2 || item.stages?.proof12 || '待更新'
            },
            editors: {
              proof12: item.editors?.proof12 || item.editors?.proof1 || item.editors?.proof2 || '',
              proof3: item.editors?.proof3 || '',
              proofFinal: item.editors?.proofFinal || ''
            },
            proofDates: item.proofDates || {},
            edition: item.edition || ''
          }
          return mappedItem
        })
        
        // 页面加载时自动进行升序排序
        sortOrder.value = 'asc'
        sortDataList()
      }
      
      
    } catch (error) {
      console.error('加载数据失败:', error)
    }
  })
  
  // 监听数据变化
  watch([dataList], () => {
    localStorage.setItem('journalProgress', JSON.stringify(dataList.value))
    console.log('5. dataList变化后的值:', dataList.value)
  }, { deep: true })
  
  // 监听 proofDates 的绑定
  const proofDates = computed(() => {
    console.log('6. 当前的 dataList:', dataList.value)
    if (!dataList.value.length) return {
      editor: '',
      proof: ''
    }
    const firstItem = dataList.value[0]
    console.log('7. 第一条记录的 proofDates:', firstItem.proofDates)
    return firstItem.proofDates
  })
  
  // 批量更新状态
  const batchUpdate = async (value, field) => {
    if (!value) return
    
    try {
      dataList.value.forEach(item => {
        if (field.startsWith('stages.')) {
          const stageName = field.split('.')[1]
          item.stages[stageName] = value
        } else if (field.startsWith('editors.')) {
          const editorName = field.split('.')[1]
          item.editors[editorName] = value
        }
        const key = `${item.id}-${field}`
        pendingChanges.value.set(key, { id: item.id, field, value })
      })
      
      saveStatus.value = '有未保存的修改'
    } catch (error) {
      console.error('批量更新失败:', error)
      saveStatus.value = '保存失败'
    }
  }
  
  // 处理日期变化
  const handleDateChange = async (field, value) => {
    try {
      // 更新所有行的对应时间
      dataList.value.forEach(item => {
        if (!item.proofDates) {
          item.proofDates = {}
        }
        item.proofDates[field] = value
        
        const key = `${item.id}-proofDates.${field}`
        pendingChanges.value.set(key, { 
          id: item.id, 
          field: `proofDates.${field}`, 
          value 
        })
      })
      
      saveStatus.value = '有未保存的修改'
    } catch (error) {
      console.error('时间更新失败:', error)
      saveStatus.value = '保存失败'
    }
  }
  
  // 保存选项设置
  const saveOptions = async () => {
    try {
      // 保存选项到 localStorage
      localStorage.setItem(`${currentOptionType.value}Options`, JSON.stringify(currentOptions.value))
      
      hideOptionsModal()
    } catch (error) {
      console.error('保存选项失败:', error)
    }
  }
  
  const showOptionsModal = (type) => {
    currentOptionType.value = type
    if (type === 'responsible') {
      modalTitle.value = '责编选项管理'
      currentOptions.value = [...responsibleOptions.value]
    } else if (type === 'editor') {
      modalTitle.value = '编辑选项管理'
      currentOptions.value = [...editorOptions.value]
    }
    // 使用原生 DOM 方法显示模态框
    if (optionsModal.value) {
      optionsModal.value.style.display = 'block'
      optionsModal.value.classList.add('show')
    }
  }
  
  const hideOptionsModal = () => {
    // 使用原生 DOM 方法隐藏模态框
    if (optionsModal.value) {
      optionsModal.value.style.display = 'none'
      optionsModal.value.classList.remove('show')
    }
    newOption.value = ''
  }
  
  const addOption = async () => {
    if (newOption.value.trim()) {
      if (!currentOptions.value.includes(newOption.value)) {
        currentOptions.value.push(newOption.value)
        // 如果勾选了"应用到所有记录"，则立即更新
        if (selectedOption.value === newOption.value) {
          try {
            await batchUpdate(newOption.value, currentOptionType.value)
          } catch (error) {
            console.error('应用新选项失败:', error)
          }
        }
      }
      newOption.value = ''
    }
  }
  
  const removeOption = (option) => {
    currentOptions.value = currentOptions.value.filter(item => item !== option)
  }
  
  
  // 触发文件选择
  const triggerFileInput = () => {
    fileInput.value.click()
  }
  
  // 修改文件导入处理函数
  const handleFileImport = async (event) => {
    try {
      const files = event.target.files
      if (!files.length) return

      // 开始导入，显示加载状态
      isImporting.value = true
      saveStatus.value = '正在导入文件...'

      // 仅发送文件名数组，避免上传文件内容
      const filenames = Array.from(files).map(f => f.name)
      const response = await axios.post(`/api/journal/${props.backendPeriod}/data/`, { filenames })

      if (response.data.status === 'success') {
        // 将新数据添加到列表
        dataList.value.push(...response.data.data)
        saveStatus.value = '已保存'
        event.target.value = '' // 清空文件输入，允许重复选择相同文件
      } else {
        throw new Error(response.data.message || '导入失败')
      }
    } catch (error) {
      console.error('文件导入失败:', error)
      saveStatus.value = '导入失败'
    } finally {
      // 无论成功失败，都要隐藏加载状态
      isImporting.value = false
    }
  }
  
  // 添加删除行的方法
  const deleteRow = async (index) => {
    if (confirm('确定要删除这一行吗？')) {
      try {
        const id = dataList.value[index].id
        const response = await axios.post(`/api/journal/${props.backendPeriod}/delete/`, {
          id: id
        })
        
        if (response.data.status === 'success') {
          dataList.value.splice(index, 1)
          saveStatus.value = '已删除'
        } else {
          throw new Error(response.data.message || '删除失败')
        }
      } catch (error) {
        console.error('删除记录失败:', error)
        saveStatus.value = '删除失败'
      }
    }
  }
  
  // 修改清空所有数据的方法
  const clearAllData = async () => {
    try {
      if (confirm('确定要清空所有数据吗？此操作不可恢复！')) {
        console.log("开始清空数据表")
        const response = await axios.post(`/api/journal/${props.backendPeriod}/clear/`)
        
        if (response.data.status === 'success') {
          console.log("数据表清空成功")
          // 清空前端数据
          dataList.value = []
          localStorage.removeItem('journalProgress')
          saveStatus.value = '清空成功'
          setTimeout(() => {
            saveStatus.value = ''
          }, 2000)
        } else {
          throw new Error(response.data.message || '清空失败')
        }
      }
    } catch (error) {
      console.error('清空数据失败:', error)
      saveStatus.value = '清空失败'
      alert('清空数据失败: ' + (error.response?.data?.message || error.message))
    }
  }
  
  // 修改序号批量设置方法
  const batchSetByNumbers = async () => {
    try {
      if (!selectedOption.value) {
        alert('请选择要设置的选项')
        return
      }
      
      // 处理输入的序号字符串
      const numbers = batchNumbers.value.split(/[,，]/).map(n => n.trim())
      
      // 验证输入格式
      const isValid = numbers.every(n => /^\d+$/.test(n))
      if (!isValid) {
        alert('请输入正确的序号格式，如：1,2,3')
        return
      }
      
      // 转换为数字并检查范围
      const indices = numbers.map(n => parseInt(n) - 1)
      const maxIndex = dataList.value.length - 1
      
      if (indices.some(i => i < 0 || i > maxIndex)) {
        alert(`序号范围应在 1 到 ${dataList.value.length} 之间`)
        return
      }
      
      saveStatus.value = '保存中...'
      
      // 更新数据库和前端显示
      const updatePromises = indices.map(async (index) => {
        const item = dataList.value[index]
        if (!item || !item.id) {
          console.warn(`跳过无效记录，索引: ${index}`)
          return
        }
        
        try {
          console.log(`更新第 ${index + 1} 条记录:`, { id: item.id, field: currentOptionType.value, value: selectedOption.value })
          const response = await axios.post(`/api/journal/${props.backendPeriod}/update/`, {
            id: item.id,
            field: currentOptionType.value,  // 使用前端字段名，让后端处理映射
            value: selectedOption.value
          })
          
          if (response.data.status === 'success') {
            console.log(`第 ${index + 1} 条记录更新成功`)
            // 更新前端显示
            if (currentOptionType.value === 'editor') {
              item.editors[currentOptionType.value.replace('editors.', '')] = selectedOption.value
            } else if (currentOptionType.value === 'responsible') {
              item.responsible = selectedOption.value
            }
          } else {
            throw new Error(response.data.message || '更新失败')
          }
        } catch (error) {
          console.error(`更新第 ${index + 1} 条记录失败:`, error)
          throw error
        }
      })
      
      await Promise.all(updatePromises)
      console.log("批量更新完成")
      saveStatus.value = '已保存'
      
      // 清空输入
      batchNumbers.value = ''
      selectedOption.value = ''
      
    } catch (error) {
      console.error("批量设置失败:", error)
      saveStatus.value = '保存失败'
      alert('批量设置失败: ' + error.message)
    }
  }
  
  // 添加排序切换方法
  const toggleSort = () => {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    sortDataList()
  }
  
  // 自然排序比较函数
  const naturalCompare = (a, b) => {
    const splitRegex = /(\d+|\D+)/g
    const ax = a.split(splitRegex)
    const bx = b.split(splitRegex)
    
    for (let i = 0; i < Math.min(ax.length, bx.length); i++) {
      if (ax[i] !== bx[i]) {
        const numa = parseInt(ax[i])
        const numb = parseInt(bx[i])
        if (!isNaN(numa) && !isNaN(numb)) {
          return numa - numb
        }
        return ax[i].localeCompare(bx[i], 'zh-CN')
      }
    }
    return ax.length - bx.length
  }
  
  // 添加排序方法
  const sortDataList = () => {
    dataList.value.sort((a, b) => {
      const result = naturalCompare(a.title, b.title)
      return sortOrder.value === 'asc' ? result : -result
    })
  }
  
  const triggerAppendFileInput = () => {
    appendFileInput.value.click()
  }
  
  const handleAppendFileImport = async (event) => {
    try {
      const files = event.target.files
      if (!files.length) return

      // 开始导入，显示加载状态
      isImporting.value = true
      saveStatus.value = '正在追加导入文件...'
  
      // 仅发送文件名数组，避免上传文件内容
      const filenames = Array.from(files).map(f => f.name)
      const response = await axios.post(`/api/journal/${props.backendPeriod}/append_files/`, { filenames })
  
      if (response.data.status === 'success') {
        // 将新数据追加到现有列表
        const newData = response.data.data
        dataList.value.push(...newData.map(item => ({
          id: parseInt(item.id),
          title: item.title || '',
          responsible: item.responsible || '',
          stages: {
            fee: item.stages?.fee || '待更新',
            proof: item.stages?.proof || item.stages?.proof1 || item.stages?.proof2 || item.stages?.proof12 || '待更新'
          },
          editors: {
            proof12: item.editors?.proof12 || item.editors?.proof1 || item.editors?.proof2 || '',
            proof3: item.editors?.proof3 || ''
          },
          proofDates: item.proofDates || {},
          edition: item.edition || currentEdition.value || ''
        })))
        saveStatus.value = '已保存'
        event.target.value = '' // 清空文件输入
      } else {
        throw new Error(response.data.message || '追加导入失败')
      }
    } catch (error) {
      console.error('追加导入失败:', error)
      saveStatus.value = '保存失败'
    } finally {
      // 无论成功失败，都要隐藏加载状态
      isImporting.value = false
    }
  }

  // 更新日志相关
  const openUpdateLog = async () => {
    try {
      const resp = await axios.get('/api/update-log/latest/')
      if (resp.data && resp.data.status === 'success') {
        updateLog.value = resp.data.data
      } else {
        updateLog.value = null
      }
    } catch (e) {
      updateLog.value = null
    }
    if (updateLogModal.value) {
      updateLogModal.value.style.display = 'block'
      updateLogModal.value.classList.add('show')
    }
  }

  const hideUpdateLog = () => {
    if (updateLogModal.value) {
      updateLogModal.value.style.display = 'none'
      updateLogModal.value.classList.remove('show')
    }
  }
  
  // 版次相关函数
  const showEditionModal = () => {
    // 解析当前版次，填充到输入框
    if (currentEdition.value) {
      const match = currentEdition.value.match(/(\d+)年(\d+)月/)
      if (match) {
        editionYear.value = parseInt(match[1])
        editionMonth.value = parseInt(match[2])
      } else {
        editionYear.value = null
        editionMonth.value = null
      }
    } else {
      editionYear.value = null
      editionMonth.value = null
    }
    
    // 显示弹窗
    if (editionModal.value) {
      editionModal.value.style.display = 'block'
      editionModal.value.classList.add('show')
      // 聚焦年份输入框
      setTimeout(() => {
        if (editionYearRef.value) {
          editionYearRef.value.focus()
        }
      }, 100)
    }
  }
  
  const hideEditionModal = () => {
    if (editionModal.value) {
      editionModal.value.style.display = 'none'
      editionModal.value.classList.remove('show')
    }
    editionYear.value = null
    editionMonth.value = null
  }
  
  const saveEdition = async () => {
    if (!editionYear.value || !editionMonth.value) {
      alert('请填写年份和月份')
      return
    }
    
    if (editionYear.value < 2000 || editionYear.value > 2100) {
      alert('年份范围应在 2000-2100 之间')
      return
    }
    
    if (editionMonth.value < 1 || editionMonth.value > 100) {
      alert('月份范围应在 1-12 之间')
      return
    }
    
    const editionText = `${editionYear.value}年${editionMonth.value}月`
    
    try {
      isSavingEdition.value = true
      const response = await axios.post(`/api/journal/${props.backendPeriod}/edition/`, {
        edition: editionText
      })
      
      if (response.data.status === 'success') {
        currentEdition.value = editionText
        // 更新所有记录的版次字段
        dataList.value.forEach(item => {
          item.edition = editionText
        })
        hideEditionModal()
        saveStatus.value = '版次已保存'
        setTimeout(() => {
          if (saveStatus.value === '版次已保存') {
            saveStatus.value = ''
          }
        }, 2000)
      } else {
        throw new Error(response.data.message || '保存失败')
      }
    } catch (error) {
      console.error('保存版次失败:', error)
      alert('保存版次失败: ' + (error.response?.data?.message || error.message))
    } finally {
      isSavingEdition.value = false
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
          axios.post(`/api/journal/${props.backendPeriod}/update/`, {
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
  </script>
  
  <style scoped>
  .journal-period {
    padding: 20px;
  }
  .page-actions {
    /* 移除绝对定位，使用flex布局 */
    display: flex !important;
    align-items: center;
  }
  
  .page-actions button {
    display: inline-block !important;
    visibility: visible !important;
  }
  
  .status-select { 
    background: transparent;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 14px;
    min-width: 120px;
  }
  
  .status-select option {
    padding: 8px;
  }
  
  .table th {
    background-color: #f8f9fa;
    font-weight: 600;
  }
  
  .table td {
    vertical-align: middle;
  }
  
  .status-待更新 { color: #6c757d; }
  .status-未完成 { color: #dc3545; }
  .status-进行中 { color: #ffc107; }
  .status-已完成 { color: #28a745; }
  
  .table-hover tbody tr:hover {
    background-color: #f8f9fa;
  }
  
  .batch-select {
    display: block;
    width: 100%;
    padding: 2px;
    font-size: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 4px;
    cursor: pointer;
  }
  
  .batch-select:focus {
    outline: none;
    border-color: #86b7fe;
  }
  
  .option-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 10px;
    margin: 5px 0;
    background: #f8f9fa;
    border-radius: 4px;
  }
  
  .modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1050;
  }
  
  .modal.show {
    display: block;
  }
  
  .current-options {
    margin-top: 15px;
    max-height: 200px;
    overflow-y: auto;
  }
  
  /* 添加版次输入框的样式 */
  .input-group-text {
    background-color: #f8f9fa;
  }
  
  .form-text {
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }
  
  /* 添加按钮组样式 */
  .btn-group {
    display: flex;
    gap: 10px;
  }
  
  /* 删除按钮样式 */
  .delete-btn {
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 4px;
    transition: all 0.2s ease;
  }
  
  .delete-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
  }
  
  .delete-btn i {
    font-size: 14px;
  }
  
  /* 添加可编辑单元格的样式 */
  .editable-cell {
    position: relative;
    width: 100%;
  }
  
  .editable-cell input {
    width: 100%;
    border: 1px solid transparent;
    background: transparent;
    transition: all 0.3s;
  }
  
  .editable-cell input:hover {
    border-color: #dee2e6;
  }
  
  .editable-cell input:focus {
    border-color: #86b7fe;
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    background: white;
  }
  
  /* 添加日期输入框样式 */
  .date-input {
    width: 50px;
    padding: 0 4px;
    font-size: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin: 0 4px;
    height: 20px;
  }
  
  .date-input:focus {
    outline: none;
    border-color: #86b7fe;
  }
  
  /* 添加序号批量设置相关样式 */
  .form-select {
    flex: 0 0 auto;
    width: auto;
  }
  
  /* 添加排序按钮样式 */
  .sort-btn {
    background: none;
    border: none;
    padding: 0 4px;
    cursor: pointer;
    font-size: 14px;
    color: #666;
  }
  
  .sort-btn:hover {
    color: #333;
  }
  
  /* 添加新行按钮样式 */
  .add-row-tr {
    background-color: #f8f9fa;
  }
  
  .add-row-btn {
    color: #0d6efd;
    text-decoration: none;
    padding: 8px 16px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    transition: all 0.3s ease;
  }
  
  .add-row-btn:hover {
    color: #0a58ca;
    transform: scale(1.05);
  }
  
  .add-row-btn i {
    font-size: 1.2em;
  }
  
  /* 添加保存状态提示样式 */
  .save-status {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 10px 20px;
    border-radius: 4px;
    z-index: 1000;
  }
  
  .saving {
    background-color: #fff3cd;
    color: #856404;
  }
  
  .saved {
    background-color: #d4edda;
    color: #155724;
  }
  
  .error {
    background-color: #f8d7da;
    color: #721c24;
  }
  
  /* 添加保存按钮样式 */
  .btn-success {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .btn-success i {
    font-size: 1.1em;
  }
  
  /* 修改未保存提示的样式 */
  .save-status:contains('有未保存的修改') {
    color: #dc3545;
    font-weight: bold;
    background-color: #fff3cd;
    border: 2px solid #dc3545;
  }

  /* 添加导入进度提示样式 */
  .import-progress {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 20px 30px;
    border-radius: 8px;
    z-index: 9999;
    display: flex;
    align-items: center;
    font-size: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }

  .import-progress .spinner-border {
    width: 1.5rem;
    height: 1.5rem;
    border-width: 0.2em;
  }

  /* 禁用状态下的按钮样式 */
  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* 版次提示样式 */
  .edition-warning-alert {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #fff3cd;
    color: #856404;
    padding: 10px 20px;
    border-radius: 4px;
    border: 1px solid #ffc107;
    z-index: 1050;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  .edition-warning-alert i {
    font-size: 18px;
  }
  
  /* 版次显示徽章样式 */
  .edition-display-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    margin-left: 8px;
  }
  
  .edition-display-badge i {
    font-size: 16px;
    color: #0c5460;
  }
  </style> 
  
