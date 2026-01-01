<template>
  <div class="main-content">
    <h3>👥 作者通讯录管理</h3>
    
    <!-- 未保存提示 -->
    <div v-if="hasUnsavedChanges" class="unsaved-changes-alert">
      <div class="alert alert-warning d-flex align-items-center">
        <i class="bi bi-exclamation-triangle me-2"></i>
        有未保存的修改
        <button class="btn btn-primary btn-sm ms-3" @click="saveChanges">
          保存修改
        </button>
      </div>
    </div>

    <!-- 导入对话框 -->
    <div class="modal fade" id="importModal" tabindex="-1" ref="importModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">导入通讯录数据</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">选择文件（支持 Excel/CSV）</label>
              <input type="file" class="form-control" @change="handleFileSelect" accept=".xlsx,.xls,.csv">
            </div>
            <div class="mb-3">
              <label class="form-label">通讯录标签</label>
              <div class="row g-2">
                <div class="col">
                  <input type="number" class="form-control" v-model="importYear" placeholder="年份（如：2025）" min="2000" max="2100">
                </div>
                <div class="col">
                  <select class="form-select" v-model="importMonth">
                    <option value="">选择月份</option>
                    <option v-for="month in 12" :key="month" :value="month">{{ month }}月</option>
                  </select>
                </div>
              </div>
            </div>
            <div v-if="previewData.length > 0" class="preview-section">
              <h6>数据预览</h6>
              <div class="preview-table">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th v-for="header in previewHeaders" :key="header">{{ header }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in previewData.slice(0, 3)" :key="index">
                      <td v-for="header in previewHeaders" :key="header">{{ row[header] }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
            <button type="button" class="btn btn-primary" @click="importData" :disabled="!isValidImportLabel">确认导入</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出对话框 -->
    <div class="modal fade" id="exportModal" tabindex="-1" ref="exportModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">导出通讯录数据</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">选择要导出的标签</label>
              <select class="form-select" v-model="exportLabel">
                <option value="">导出全部数据</option>
                <option v-for="label in uniqueLabels" :key="label" :value="label">
                  {{ label }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
            <button type="button" class="btn btn-primary" @click="executeExport">确认导出</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 清空确认对话框 -->
    <div class="modal fade" id="clearModal" tabindex="-1" ref="clearModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">清空通讯录数据</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">选择要清空的标签</label>
              <select class="form-select" v-model="clearLabel">
                <option value="">清空全部数据</option>
                <option v-for="label in uniqueLabels" :key="label" :value="label">
                  {{ label }}
                </option>
              </select>
            </div>
            <div class="alert alert-danger">
              此操作不可恢复，请谨慎操作！
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
            <button type="button" class="btn btn-danger" @click="executeClear">确认清空</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 顶部工具栏 -->
    <div class="toolbar mb-3">
      <div class="tool-group">
        <button class="btn btn-primary" @click="showImportModal">
          <i class="bi bi-file-earmark-excel"></i> 导入数据
        </button>
        <button class="btn btn-primary" @click="showExportModal">
          <i class="bi bi-download"></i> 导出Excel
        </button>
        <button class="btn btn-danger" @click="showClearModal">
          <i class="bi bi-trash"></i> 一键清空
        </button>
        <button class="btn btn-success" @click="addNewRow">
          <i class="bi bi-plus-circle"></i> 新增一行
        </button>
        <select class="form-select" v-model="selectedLabel">
          <option value="">全部标签</option>
          <option v-for="label in uniqueLabels" :key="label" :value="label">
            {{ label }}
          </option>
        </select>
        <div class="search-box">
          <input
            type="text"
            class="form-control"
            v-model="searchKeyword"
            placeholder="搜索任意字段..."
          >
          <i class="bi bi-search"></i>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-responsive">
      <table class="table table-bordered">
        <thead class="table-light">
          <tr>
            <th>#</th>
            <th>邮编</th>
            <th>姓名</th>
            <th>手机</th>
            <th>地址</th>
            <th>邮箱</th>
            <th>备注</th>
            <th>标签</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(contact, index) in filteredContacts" :key="contact.id || contact.tempId">
            <td>{{ index + 1 }}</td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="contact.postcode" 
                @input="handleFieldChange(contact)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="contact.name"
                @input="handleFieldChange(contact)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="contact.phone"
                @input="handleFieldChange(contact)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="contact.address"
                @input="handleFieldChange(contact)">
            </td>
            <td>
              <input type="email" class="form-control form-control-sm" 
                v-model="contact.email"
                @input="handleFieldChange(contact)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="contact.notes"
                @input="handleFieldChange(contact)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="contact.label"
                @input="handleFieldChange(contact)">
            </td>
            <td>
              <button class="btn btn-sm btn-danger" @click="deleteRow(contact)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { Modal } from 'bootstrap'
import axios from 'axios'

export default {
  name: 'ContactsManage',
  setup() {
    const contacts = ref([])
    const searchKeyword = ref('')
    const selectedLabel = ref('')
    const importYear = ref('')
    const importMonth = ref('')
    const exportLabel = ref('')
    const clearLabel = ref('')
    const importModal = ref(null)
    const exportModal = ref(null)
    const clearModal = ref(null)
    const previewData = ref([])
    const previewHeaders = ref([])
    
    // 未保存的更改跟踪
    const modifiedContacts = ref(new Set())
    const newContacts = ref(new Set())
    const deletedContacts = ref(new Set())
    
    const hasUnsavedChanges = computed(() => {
      return modifiedContacts.value.size > 0 || 
             newContacts.value.size > 0 || 
             deletedContacts.value.size > 0
    })

    // 计算所有唯一的标签
    const uniqueLabels = computed(() => {
      const labels = new Set(contacts.value.map(contact => contact.label))
      return Array.from(labels)
    })

    // 过滤后的联系人列表
    const filteredContacts = computed(() => {
      let filtered = contacts.value

      // 标签筛选
      if (selectedLabel.value) {
        filtered = filtered.filter(contact => contact.label === selectedLabel.value)
      }

      // 关键词搜索
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filtered = filtered.filter(contact => {
          return Object.values(contact).some(value => 
            String(value).toLowerCase().includes(keyword)
          )
        })
      }

      return filtered
    })

    // 计算导入标签是否有效
    const isValidImportLabel = computed(() => {
      return importYear.value && importMonth.value
    })

    // 生成标准化的标签
    const generateLabel = (year, month) => {
      return `${year}年${month}月`
    }

    // 加载数据
    const loadContacts = async () => {
      try {
        const response = await axios.get('/api/contacts/')
        contacts.value = response.data
      } catch (error) {
        console.error('加载通讯录数据失败:', error)
      }
    }

    // 保存更改
    const saveChanges = async () => {
      try {
        // 处理修改的联系人
        for (const contactId of modifiedContacts.value) {
          const contact = contacts.value.find(c => c.id === contactId)
          if (contact) {
            const contactData = {
              postcode: contact.postcode,
              name: contact.name,
              phone: contact.phone,
              address: contact.address,
              email: contact.email,
              notes: contact.notes,
              label: contact.label
            }
            await axios.put(`/api/contacts/${contactId}/`, contactData)
          }
        }

        // 处理新增的联系人
        for (const tempId of newContacts.value) {
          const contact = contacts.value.find(c => c.id === `temp_${tempId}`)
          if (contact) {
            const contactData = {
              postcode: contact.postcode,
              name: contact.name,
              phone: contact.phone,
              address: contact.address,
              email: contact.email,
              notes: contact.notes,
              label: contact.label
            }
            const response = await axios.post('/api/contacts/', contactData)
            // 更新临时ID为实际ID
            Object.assign(contact, response.data)
          }
        }

        // 处理删除的联系人
        for (const contactId of deletedContacts.value) {
          await axios.delete(`/api/contacts/${contactId}/`)
        }

        // 清空所有更改记录
        modifiedContacts.value.clear()
        newContacts.value.clear()
        deletedContacts.value.clear()

        // 重新加载数据
        await loadContacts()
      } catch (error) {
        console.error('保存更改失败:', error)
        alert('保存更改失败，请重试')
      }
    }

    // 字段更改处理
    const handleFieldChange = (contact) => {
      if (contact.id && !contact.id.toString().startsWith('temp_')) {
        modifiedContacts.value.add(contact.id)
      } else {
        newContacts.value.add(contact.id.replace('temp_', ''))
      }
    }

    // 显示导入对话框
    const showImportModal = () => {
      if (!importModal.value) {
        importModal.value = new Modal(document.getElementById('importModal'))
      }
      importYear.value = ''
      importMonth.value = ''
      previewData.value = []
      previewHeaders.value = []
      importModal.value.show()
    }

    // 处理文件选择
    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (!file) return

      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result)
          const workbook = XLSX.read(data, { type: 'array' })
          const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
          const jsonData = XLSX.utils.sheet_to_json(firstSheet)

          // 获取表头
          previewHeaders.value = Object.keys(jsonData[0] || {})
          previewData.value = jsonData
        } catch (error) {
          console.error('解析文件失败:', error)
          alert('文件解析失败，请检查文件格式是否正确')
        }
      }
      reader.readAsArrayBuffer(file)
    }

    // 导入数据
    const importData = async () => {
      if (!isValidImportLabel.value) {
        alert('请输入完整的年份和月份')
        return
      }

      const label = generateLabel(importYear.value, importMonth.value)
      
      try {
        await axios.post('/api/contacts/batch_create/', {
          contacts: previewData.value.map(row => ({
            postcode: row['邮编'] || '',
            name: row['姓名'] || '',
            phone: row['手机'] || '',
            address: row['地址'] || '',
            email: row['邮箱'] || '',
            notes: row['备注'] || '',
            label
          }))
        })

        await loadContacts()
        importModal.value.hide()
        
        // 重置导入表单
        importYear.value = ''
        importMonth.value = ''
        previewData.value = []
        previewHeaders.value = []
      } catch (error) {
        console.error('导入数据失败:', error)
        alert('导入数据失败，请重试')
      }
    }

    // 显示导出对话框
    const showExportModal = () => {
      if (!exportModal.value) {
        exportModal.value = new Modal(document.getElementById('exportModal'))
      }
      exportLabel.value = ''
      exportModal.value.show()
    }

    // 显示清空对话框
    const showClearModal = () => {
      if (!clearModal.value) {
        clearModal.value = new Modal(document.getElementById('clearModal'))
      }
      clearLabel.value = ''
      clearModal.value.show()
    }

    // 执行导出
    const executeExport = () => {
      const dataToExport = exportLabel.value
        ? contacts.value.filter(contact => contact.label === exportLabel.value)
        : contacts.value

      const exportData = dataToExport.map(contact => ({
        '邮编': contact.postcode,
        '姓名': contact.name,
        '手机': contact.phone,
        '地址': contact.address,
        '邮箱': contact.email,
        '备注': contact.notes,
        '标签': contact.label
      }))

      const ws = XLSX.utils.json_to_sheet(exportData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, '通讯录')

      const fileName = exportLabel.value
        ? `通讯录_${exportLabel.value}.xlsx`
        : `通讯录_全部_${new Date().toLocaleDateString()}.xlsx`

      XLSX.writeFile(wb, fileName)
      exportModal.value.hide()
    }

    // 执行清空
    const executeClear = async () => {
      try {
        await axios.delete('/api/contacts/batch_delete/', {
          data: { label: clearLabel.value }
        })
        await loadContacts()
        clearModal.value.hide()
      } catch (error) {
        console.error('清空数据失败:', error)
        alert('清空数据失败，请重试')
      }
    }

    // 添加新行
    const addNewRow = () => {
      const timestamp = Date.now()
      const newContact = {
        id: `temp_${timestamp}`,
        postcode: '',
        name: '',
        phone: '',
        address: '',
        email: '',
        notes: '',
        label: ''
      }
      contacts.value.unshift(newContact)
      newContacts.value.add(timestamp.toString())
    }

    // 删除行
    const deleteRow = async (contact) => {
      if (confirm('确定要删除这条记录吗？')) {
        const index = contacts.value.findIndex(c => c === contact)
        if (index > -1) {
          contacts.value.splice(index, 1)
          if (contact.id && !contact.id.toString().startsWith('temp_')) {
            deletedContacts.value.add(contact.id)
          } else {
            newContacts.value.delete(contact.id.replace('temp_', ''))
          }
        }
      }
    }

    // 初始化加载数据
    onMounted(() => {
      loadContacts()
    })

    return {
      contacts,
      searchKeyword,
      selectedLabel,
      importYear,
      importMonth,
      exportLabel,
      clearLabel,
      hasUnsavedChanges,
      previewData,
      previewHeaders,
      showImportModal,
      handleFileSelect,
      importData,
      showExportModal,
      showClearModal,
      executeExport,
      executeClear,
      addNewRow,
      deleteRow,
      handleFieldChange,
      saveChanges,
      isValidImportLabel,
      uniqueLabels,
      filteredContacts
    }
  }
}
</script>

<style scoped>
.main-content {
  margin-left: 250px;
  padding: 20px;
}

.toolbar {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tool-group {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.form-select {
  min-width: 150px;
  max-width: 250px;
  order: 1; /* 控制显示顺序 */
}

.search-box {
  min-width: 200px;
  max-width: 300px;
  flex: 1;
  order: 2; /* 控制显示顺序 */
  position: relative;
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

.btn {
  order: 0; /* 控制显示顺序，让按钮排在最前面 */
}

.preview-section {
  margin-top: 15px;
  border-top: 1px solid #dee2e6;
  padding-top: 15px;
}

.preview-table {
  max-height: 200px;
  overflow-y: auto;
}

.table td {
  vertical-align: middle;
}

.form-control-sm {
  padding: 0.25rem 0.5rem;
}

.btn i {
  margin-right: 5px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
  
  .tool-group {
    flex-direction: column;
  }
  
  .search-box,
  .form-select {
    width: 100%;
    max-width: none;
  }
}

.unsaved-changes-alert {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  min-width: 250px;
}

.alert {
  margin-bottom: 0;
  padding: 0.5rem 1rem;
}
</style> 