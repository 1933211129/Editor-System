<template>
  <div class="main-content">
    <h3>👨‍⚖️ 责编管理</h3>

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
            <h5 class="modal-title">导入责编数据</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">选择文件（支持 Excel/CSV）</label>
              <input type="file" class="form-control" @change="handleFileSelect" accept=".xlsx,.xls,.csv">
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
            <button type="button" class="btn btn-primary" @click="importData" :disabled="!previewData.length">确认导入</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出对话框 -->
    <div class="modal fade" id="exportModal" tabindex="-1" ref="exportModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">导出责编数据</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">选择要导出的标签</label>
              <select class="form-select" v-model="exportLabel">
                <option value="">导出全部数据</option>
                <option v-for="year in uniqueYears" :key="year" :value="year">
                  {{ year }}
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
            <h5 class="modal-title">清空责编数据</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-danger">
              此操作将清空所有责编数据，且不可恢复，请谨慎操作！
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
        <select class="form-select" v-model="selectedYear">
          <option value="">全部年份</option>
          <option v-for="year in uniqueYears" :key="year" :value="year">
            {{ year }}
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
        <div class="calc-box">
          <select class="form-select form-select-sm" v-model="calcYear">
            <option value="">选择年份</option>
            <option v-for="year in uniqueYears" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
          <button class="btn btn-sm btn-outline-primary" @click="calculateYearlyTotal" :disabled="!calcYear">
            计算年度总额
          </button>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-responsive">
      <table class="table table-bordered">
        <thead class="table-light">
          <tr>
            <th>#</th>
            <th style="min-width: 85px">年份</th>
            <th style="min-width: 100px">期次</th>
            <th style="min-width: 120px">姓名</th>
            <th>工作单位</th>
            <th>身份证号</th>
            <th>银行卡号</th>
            <th>开户行</th>
            <th>手机</th>
            <th>应发</th>
            <th>税金</th>
            <th>实发</th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(reviewer, index) in filteredReviewers" :key="reviewer.id">
            <td>{{ index + 1 }}</td>
            <td>
              <input type="number" class="form-control form-control-sm" 
                v-model="reviewer.year"
                min="2000" max="2100"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="number" class="form-control form-control-sm" 
                v-model="reviewer.period"
                min="1" max="12"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="reviewer.name"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="reviewer.workplace"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="reviewer.id_card"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="reviewer.bank_account"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="reviewer.bank_name"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="reviewer.phone"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="number" class="form-control form-control-sm" 
                v-model="reviewer.gross_pay"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="number" class="form-control form-control-sm" 
                v-model="reviewer.tax"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="number" class="form-control form-control-sm" 
                v-model="reviewer.net_pay"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <input type="text" class="form-control form-control-sm" 
                v-model="reviewer.notes"
                @input="handleFieldChange(reviewer)">
            </td>
            <td>
              <button class="btn btn-sm btn-danger" @click="deleteRow(reviewer)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 计算结果弹窗 -->
    <div class="modal fade" id="calcModal" tabindex="-1" ref="calcModal">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ calcYear }}年度统计</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="calc-result">
              <div class="calc-item">
                <span class="label">应发总额：</span>
                <span class="value">{{ calcResult.grossPay }}元</span>
              </div>
              <div class="calc-item">
                <span class="label">税金总额：</span>
                <span class="value">{{ calcResult.tax }}元</span>
              </div>
              <div class="calc-item">
                <span class="label">实发总额：</span>
                <span class="value">{{ calcResult.netPay }}元</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">我已知晓</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { Modal } from 'bootstrap'
import axios from 'axios'

export default {
  name: 'ReviewersManage',
  setup() {
    const reviewers = ref([])
    const searchKeyword = ref('')
    const selectedLabel = ref('')
    const selectedYear = ref('')
    const selectedPeriod = ref('')
    const importYear = ref('')
    const importMonth = ref('')
    const exportLabel = ref('')
    const clearLabel = ref('')
    const importModal = ref(null)
    const exportModal = ref(null)
    const clearModal = ref(null)
    const previewData = ref([])
    const previewHeaders = ref([])
    const calcYear = ref('')
    const calcModal = ref(null)
    const calcResult = ref({
      grossPay: '0',
      tax: '0',
      netPay: '0'
    })
    
    // 未保存的更改跟踪
    const modifiedReviewers = ref(new Set())
    const newReviewers = ref(new Set())
    const deletedReviewers = ref(new Set())
    
    const hasUnsavedChanges = computed(() => {
      return modifiedReviewers.value.size > 0 || 
             newReviewers.value.size > 0 || 
             deletedReviewers.value.size > 0
    })

    // 计算所有唯一的年份
    const uniqueYears = computed(() => {
      const years = new Set(reviewers.value.map(reviewer => reviewer.year))
      return Array.from(years).filter(Boolean).sort((a, b) => b - a)
    })

    // 过滤后的责编列表
    const filteredReviewers = computed(() => {
      let filtered = reviewers.value

      // 年份筛选
      if (selectedYear.value) {
        filtered = filtered.filter(reviewer => reviewer.year === selectedYear.value)
      }

      // 关键词搜索
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filtered = filtered.filter(reviewer => {
          return Object.values(reviewer).some(value => 
            String(value).toLowerCase().includes(keyword)
          )
        })
      }

      return filtered
    })

    // 计算导入按钮是否可用
    const isValidImportLabel = computed(() => {
      return previewData.value.length > 0
    })

    // 加载数据
    const loadReviewers = async () => {
      try {
        const response = await axios.get('/api/reviewers/')
        reviewers.value = response.data
      } catch (error) {
        console.error('加载责编数据失败:', error)
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
      clearModal.value.show()
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
      try {
        await axios.post('/api/reviewers/batch_create/', {
          reviewers: previewData.value.map(row => ({
            year: row['年份'] || '',
            period: row['期次'] || '',
            name: row['姓名'] || '',
            workplace: row['工作单位'] || '',
            id_card: row['身份证号'] || '',
            bank_account: row['银行卡号'] || '',
            bank_name: row['开户行'] || '',
            phone: row['手机'] || '',
            gross_pay: row['应发'] || 0,
            tax: row['税金'] || 0,
            net_pay: row['实发'] || 0,
            notes: row['备注'] || ''
          }))
        })

        await loadReviewers()
        importModal.value.hide()
        
        // 重置导入表单
        previewData.value = []
        previewHeaders.value = []
      } catch (error) {
        console.error('导入数据失败:', error)
        alert('导入数据失败，请重试')
      }
    }

    // 执行导出
    const executeExport = () => {
      const dataToExport = exportLabel.value
        ? reviewers.value.filter(reviewer => String(reviewer.year) === String(exportLabel.value))
        : reviewers.value

      const exportData = dataToExport.map(reviewer => ({
        '年份': reviewer.year,
        '期次': reviewer.period,
        '姓名': reviewer.name,
        '工作单位': reviewer.workplace,
        '身份证号': reviewer.id_card,
        '银行卡号': reviewer.bank_account,
        '开户行': reviewer.bank_name,
        '手机': reviewer.phone,
        '应发': reviewer.gross_pay,
        '税金': reviewer.tax,
        '实发': reviewer.net_pay,
        '备注': reviewer.notes
      }))

      const ws = XLSX.utils.json_to_sheet(exportData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, '责编信息')

      const fileName = exportLabel.value
        ? `责编信息_${exportLabel.value}.xlsx`
        : `责编信息_全部_${new Date().toLocaleDateString()}.xlsx`

      XLSX.writeFile(wb, fileName)
      exportModal.value.hide()
    }

    // 执行清空
    const executeClear = async () => {
      try {
        await axios.delete('/api/reviewers/batch_delete/')
        await loadReviewers()
        clearModal.value.hide()
      } catch (error) {
        console.error('清空数据失败:', error)
        alert('清空数据失败，请重试')
      }
    }

    // 添加新行
    const addNewRow = () => {
      const timestamp = Date.now()
      const newReviewer = {
        id: `temp_${timestamp}`,
        year: new Date().getFullYear(),
        period: '',
        name: '',
        workplace: '',
        id_card: '',
        bank_account: '',
        bank_name: '',
        phone: '',
        gross_pay: 1050,  // 默认应发
        tax: 50,          // 默认税金
        net_pay: 1000,    // 默认实发
        notes: ''
      }
      reviewers.value.unshift(newReviewer)
      newReviewers.value.add(timestamp.toString())
    }

    // 删除行
    const deleteRow = async (reviewer) => {
      if (confirm('确定要删除这条记录吗？')) {
        const index = reviewers.value.findIndex(r => r === reviewer)
        if (index > -1) {
          reviewers.value.splice(index, 1)
          if (reviewer.id && !reviewer.id.toString().startsWith('temp_')) {
            deletedReviewers.value.add(reviewer.id)
          } else {
            newReviewers.value.delete(reviewer.id.replace('temp_', ''))
          }
        }
      }
    }

    // 字段更改处理
    const handleFieldChange = (reviewer) => {
      if (reviewer.id && !reviewer.id.toString().startsWith('temp_')) {
        modifiedReviewers.value.add(reviewer.id)
      } else {
        newReviewers.value.add(reviewer.id.replace('temp_', ''))
      }
    }

    // 保存更改
    const saveChanges = async () => {
      try {
        // 处理修改的责编
        for (const reviewerId of modifiedReviewers.value) {
          const reviewer = reviewers.value.find(r => r.id === reviewerId)
          if (reviewer) {
            const reviewerData = {
              year: reviewer.year,
              period: reviewer.period,
              name: reviewer.name,
              workplace: reviewer.workplace,
              id_card: reviewer.id_card,
              bank_account: reviewer.bank_account,
              bank_name: reviewer.bank_name,
              phone: reviewer.phone,
              gross_pay: reviewer.gross_pay,
              tax: reviewer.tax,
              net_pay: reviewer.net_pay,
              notes: reviewer.notes
            }
            await axios.put(`/api/reviewers/${reviewerId}/`, reviewerData)
          }
        }

        // 处理新增的责编
        for (const tempId of newReviewers.value) {
          const reviewer = reviewers.value.find(r => r.id === `temp_${tempId}`)
          if (reviewer) {
            const reviewerData = {
              year: reviewer.year,
              period: reviewer.period,
              name: reviewer.name,
              workplace: reviewer.workplace,
              id_card: reviewer.id_card,
              bank_account: reviewer.bank_account,
              bank_name: reviewer.bank_name,
              phone: reviewer.phone,
              gross_pay: reviewer.gross_pay,
              tax: reviewer.tax,
              net_pay: reviewer.net_pay,
              notes: reviewer.notes
            }
            const response = await axios.post('/api/reviewers/', reviewerData)
            Object.assign(reviewer, response.data)
          }
        }

        // 处理删除的责编
        for (const reviewerId of deletedReviewers.value) {
          await axios.delete(`/api/reviewers/${reviewerId}/`)
        }

        // 清空所有更改记录
        modifiedReviewers.value.clear()
        newReviewers.value.clear()
        deletedReviewers.value.clear()

        // 重新加载数据
        await loadReviewers()
      } catch (error) {
        console.error('保存更改失败:', error)
        alert('保存更改失败，请重试')
      }
    }

    // 计算年度总额
    const calculateYearlyTotal = () => {
      if (!calcYear.value) return

      const yearData = reviewers.value.filter(r => r.year === calcYear.value)
      const stats = yearData.reduce((acc, curr) => {
        acc.grossPay += Number(curr.gross_pay) || 0
        acc.tax += Number(curr.tax) || 0
        acc.netPay += Number(curr.net_pay) || 0
        return acc
      }, { grossPay: 0, tax: 0, netPay: 0 })

      calcResult.value = {
        grossPay: stats.grossPay.toLocaleString(),
        tax: stats.tax.toLocaleString(),
        netPay: stats.netPay.toLocaleString()
      }

      if (!calcModal.value) {
        calcModal.value = new Modal(document.getElementById('calcModal'))
      }
      calcModal.value.show()
    }

    // 初始化加载数据
    onMounted(() => {
      loadReviewers()
    })

    return {
      reviewers,
      searchKeyword,
      selectedLabel,
      selectedYear,
      selectedPeriod,
      importYear,
      importMonth,
      exportLabel,
      clearLabel,
      hasUnsavedChanges,
      uniqueYears,
      filteredReviewers,
      previewData,
      previewHeaders,
      isValidImportLabel,
      calcYear,
      calcResult,
      calculateYearlyTotal,
      showImportModal,
      showExportModal,
      showClearModal,
      handleFileSelect,
      importData,
      executeExport,
      executeClear,
      addNewRow,
      deleteRow,
      handleFieldChange,
      saveChanges
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
  order: 1;
}

.search-box {
  min-width: 200px;
  max-width: 300px;
  flex: 1;
  order: 2;
  position: relative;
  margin-right: 20px;
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

.calc-box {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 0 0 auto;
  order: 3;
}

.calc-box .form-select {
  width: 120px;
}

.calc-result {
  padding: 10px 0;
}

.calc-item {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calc-item:last-child {
  margin-bottom: 0;
}

.calc-item .label {
  color: #666;
}

.calc-item .value {
  color: #0d6efd;
  font-weight: 500;
}

.btn {
  order: 0;
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
</style> 