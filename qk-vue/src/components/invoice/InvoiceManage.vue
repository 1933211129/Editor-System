<template>
  <div class="main-content">
    <h4>📋 发票登记管理</h4>
    
    <!-- 文本识别框 -->
    <div class="mb-3">
      <div class="recognition-box">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="mb-0">📝 发票信息自动识别</h5>
          <button class="btn btn-primary btn-sm" @click="recognizeInvoice">
            <i class="bi bi-magic"></i> 识别并新增
          </button>
        </div>
        <textarea
          class="form-control recognition-textarea"
          v-model="recognitionText"
          rows="6"
          placeholder="请粘贴如下格式的发票信息：
————————版面费回执————————
论文编号：2024-0287
论文题目：基于原型学习的事件关系抽取框架
金额：4800元
缴费时间：2025年5月27日
缴纳方式：支付宝转账
————————发票领取回执————————
发票抬头：中国科学院计算技术研究所
纳税人识别号：12100000400012342E
姓名：胡志磊
收信邮箱：herberthu@126.com
手机号：18801161179"
        ></textarea>
      </div>
    </div>

    <!-- 顶部按钮组 -->
    <div class="mb-3 d-flex align-items-center gap-2">
      <button class="btn btn-primary" @click="triggerFileInput">
        <i class="bi bi-file-earmark-excel"></i> 导入Excel[覆盖当前数据]
      </button>
      <button class="btn btn-primary" @click="triggerAppendFileInput">
        <i class="bi bi-file-earmark-plus"></i> 导入Excel[追加数据]
      </button>
      <button class="btn btn-primary" @click="exportToExcel">
        <i class="bi bi-download"></i> 导出Excel
      </button>
      <button class="btn btn-danger" @click="clearAllData">
        <i class="bi bi-trash"></i> 一键清空
      </button>
      <button class="btn btn-success" @click="addNewRowToTop">
        <i class="bi bi-plus-circle"></i> 新增一行
      </button>
      <button class="btn btn-success" @click="saveAllChanges">
        <i class="bi bi-save"></i> 保存修改
      </button>
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
        @change="handleFileImport"
        style="display: none"
        accept=".xlsx,.xls"
      >
      <input
        type="file"
        ref="appendFileInput"
        @change="handleAppendFileImport"
        style="display: none"
        accept=".xlsx,.xls"
      >
    </div>

    <!-- 发票数据表格 -->
    <table class="table table-bordered mt-3">
      <thead class="table-light">
        <tr>
          <th>#</th>
          <th>稿件编号</th>
          <th>文章</th>
          <th>金额</th>
          <th class="sortable" @click="handleSort('invoiceDate')">
            支付时间
            <i class="bi" :class="{
              'bi-arrow-down': sortState.invoiceDate === 'desc',
              'bi-arrow-up': sortState.invoiceDate === 'asc',
              'bi-arrow-down-up': !sortState.invoiceDate
            }"></i>
          </th>
          <th>支付方式</th>
          <th>类型</th>
          <th class="sortable" @click="handleSort('tag')">
            标签
            <i class="bi" :class="{
              'bi-arrow-down': sortState.tag === 'desc',
              'bi-arrow-up': sortState.tag === 'asc',
              'bi-arrow-down-up': !sortState.tag
            }"></i>
          </th>
          <th>单位</th>
          <th>识别号</th>
          <th>联系人</th>
          <th>邮箱</th>
          <th>手机</th>
          <th>备注</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in filteredList" :key="item.id">
          <td>
            {{ index + 1 }}
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.manuscriptId"
              class="form-control form-control-sm"
              @mouseenter="showTooltip($event, item.manuscriptId)"
              @mouseleave="hideTooltip"
              @change="debounceSave(item, 'manuscriptId', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.article"
              class="form-control form-control-sm"
              @mouseenter="showTooltip($event, item.article)"
              @mouseleave="hideTooltip"
              @change="debounceSave(item, 'article', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="number" 
              v-model="item.amount"
              class="form-control form-control-sm"
              @change="debounceSave(item, 'amount', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="date" 
              v-model="item.invoiceDate"
              class="form-control form-control-sm"
              @change="debounceSave(item, 'invoiceDate', $event.target.value)"
            >
          </td>
          <td>
            <div class="editable-select">
              <input 
                type="text" 
                v-model="item.paymentMethod"
                class="form-control form-control-sm"
                @input="debounceSave(item, 'paymentMethod', $event.target.value)"
              >
              <select 
                class="form-select form-select-sm" 
                @change="e => { item.paymentMethod = e.target.value; debounceSave(item, 'paymentMethod', e.target.value); }"
              >
                <option value="">选择支付方式</option>
                <option value="支付宝">支付宝</option>
                <option value="银行转账">银行转账</option>
                <option value="现金">现金</option>
                <option value="刷卡">刷卡</option>
                <option value="其他">其他</option>
              </select>
            </div>
          </td>
          <td>
            <div class="editable-select">
              <input 
                type="text" 
                v-model="item.type"
                class="form-control form-control-sm"
                @input="debounceSave(item, 'type', $event.target.value)"
              >
              <select 
                class="form-select form-select-sm" 
                @change="e => { item.type = e.target.value; debounceSave(item, 'type', e.target.value); }"
              >
                <option value="">选择类型</option>
                <option value="版面费">版面费</option>
                <option value="会议费">会议费</option>
                <option value="其他">其他</option>
              </select>
            </div>
          </td>
          <td>
            <div class="editable-select">
              <input 
                type="text" 
                v-model="item.tag"
                class="form-control form-control-sm"
                @input="debounceSave(item, 'tag', $event.target.value)"
              >
              <select 
                class="form-select form-select-sm" 
                @change="e => { item.tag = e.target.value; debounceSave(item, 'tag', e.target.value); }"
              >
                <option value="">选择标签</option>
                <option v-for="month in 12" :key="month" :value="`${month}月`">{{ month }}月</option>
                <option value="其他">其他</option>
              </select>
            </div>
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.company"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'company', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.taxId"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'taxId', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.contact"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'contact', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="email" 
              v-model="item.email"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'email', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="tel" 
              v-model="item.phone"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'phone', $event.target.value)"
            >
          </td>
          <td>
            <input 
              type="text" 
              v-model="item.notes"
              class="form-control form-control-sm"
              @input="debounceSave(item, 'notes', $event.target.value)"
            >
          </td>
          <td class="text-center">
            <button class="btn btn-outline-danger btn-sm delete-btn" @click="deleteRow(index)" title="删除此行">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 添加保存状态提示 -->
    <div v-if="saveStatus" :class="['save-status', {
      'saving': saveStatus === '保存中...',
      'saved': saveStatus === '已保存',
      'error': saveStatus === '保存失败' || saveStatus === '创建失败'
    }]">
      {{ saveStatus }}
    </div>

    <!-- 自定义悬浮提示框 -->
    <div 
      v-if="tooltip.show" 
      class="custom-tooltip"
      :style="{ 
        left: tooltip.x + 'px', 
        top: tooltip.y + 'px' 
      }"
    >
      {{ tooltip.text }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import * as XLSX from 'xlsx'
import axios from 'axios'

const invoiceList = ref([])
const fileInput = ref(null)
const appendFileInput = ref(null)
const saveStatus = ref('')
// let saveTimeout = null
const searchKeyword = ref('')

// 排序状态
const sortState = ref({
  invoiceDate: null, // null: 不排序, 'asc': 升序, 'desc': 降序
  tag: null
})

// 排序后的列表
const sortedInvoiceList = computed(() => {
  let sorted = [...invoiceList.value]

  if (sortState.value.invoiceDate) {
    sorted.sort((a, b) => {
      const dateA = a.invoiceDate ? new Date(a.invoiceDate) : new Date(0)
      const dateB = b.invoiceDate ? new Date(b.invoiceDate) : new Date(0)
      return sortState.value.invoiceDate === 'asc' 
        ? dateA - dateB 
        : dateB - dateA
    })
  }

  if (sortState.value.tag) {
    sorted.sort((a, b) => {
      // 提取月份数字进行比较
      const getMonthNum = (tag) => {
        const match = tag?.match(/(\d+)月/)
        return match ? parseInt(match[1]) : 13 // 非月份标签放到最后
      }
      const monthA = getMonthNum(a.tag)
      const monthB = getMonthNum(b.tag)
      return sortState.value.tag === 'asc' 
        ? monthA - monthB 
        : monthB - monthA
    })
  }

  return sorted
})

// 搜索过滤后的列表
const filteredList = computed(() => {
  if (!searchKeyword.value) return sortedInvoiceList.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return sortedInvoiceList.value.filter(item => {
    // 搜索所有字段
    return Object.values(item).some(value => 
      String(value).toLowerCase().includes(keyword)
    )
  })
})

// 处理排序点击
const handleSort = (column) => {
  if (sortState.value[column] === null) {
    // 清除其他列的排序状态
    Object.keys(sortState.value).forEach(key => {
      sortState.value[key] = null
    })
    sortState.value[column] = 'asc'
  } else if (sortState.value[column] === 'asc') {
    sortState.value[column] = 'desc'
  } else {
    sortState.value[column] = null
  }
}

// 从后端加载数据
const loadData = async () => {
  try {
    const response = await axios.get('/api/invoice/data/')
    invoiceList.value = response.data
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})

// 用于存储未保存的修改
const pendingChanges = ref(new Map())

// 修改输入处理函数，不再立即保存
const debounceSave = (item, field, value) => {
  try {
    const key = `${item.id}-${field}`
    console.log(`Saving field ${field} with value ${value}`) // 添加调试日志
    pendingChanges.value.set(key, { id: item.id, field, value })
    saveStatus.value = '❌有未保存的修改'
  } catch (error) {
    console.error('保存失败:', error)
    saveStatus.value = '保存失败'
  }
}

// 修改保存函数
const saveAllChanges = async () => {
  try {
    if (pendingChanges.value.size === 0) {
      saveStatus.value = '没有需要保存的修改'
      return
    }
    
    saveStatus.value = '保存中...'
    
    // 按记录ID分组待保存的修改
    const changesByRecord = new Map()
    for (const change of pendingChanges.value.values()) {
      const { id, field, value } = change
      if (!changesByRecord.has(id)) {
        changesByRecord.set(id, {})
      }
      console.log(`Grouping change for record ${id}: ${field} = ${value}`) // 添加调试日志
      changesByRecord.get(id)[field] = value
    }
    
    const promises = []
    
    for (const [id, updates] of changesByRecord) {
      console.log(`Saving updates for record ${id}:`, updates) // 添加调试日志
      const invoice = invoiceList.value.find(item => item.id === id)
      if (!invoice) {
        throw new Error(`未找到ID为 ${id} 的发票记录`)
      }
      
      promises.push(
        axios.post('/api/invoice/update/', {
          id,
          updates
        })
      )
    }
    
    await Promise.all(promises)
    await loadData()
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

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}

// 处理文件导入
const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
      const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 })

      // 跳过表头，从第二行开始处理数据
      const rows = jsonData.slice(1)
      
      // 转换Excel数据为我们需要的格式
      const importData = rows.map(row => ({
        manuscriptId: row[0] || generateRandomId(),  // 如果没有稿件编号，生成一个
        article: row[1] || '',
        amount: row[2] || '',
        invoiceDate: row[3] || '',
        paymentMethod: row[4] || '',
        type: row[5] || '',
        tag: row[6] || '',
        company: row[7] || '',
        taxId: row[8] || '',
        contact: row[9] || '',
        email: row[10] || '',
        phone: row[11] || '',
        notes: row[12] || ''
      }))

      // 调用后端批量导入接口
      const response = await axios.post('/api/invoice/import/', { data: importData })
      
      if (response.data.status === 'success') {
        // 重新加载数据
        await loadData()
        saveStatus.value = '导入成功'
      } else {
        throw new Error(response.data.message)
      }
    } catch (error) {
      console.error('导入失败:', error)
      saveStatus.value = '导入失败'
    } finally {
      event.target.value = '' // 清空文件输入
      setTimeout(() => {
        saveStatus.value = ''
      }, 2000)
    }
  }
  reader.readAsArrayBuffer(file)
}

// 生成随机稿件编号
const generateRandomId = () => {
  // 创建字符集
  const upperLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const lowerLetters = 'abcdefghijklmnopqrstuvwxyz'
  const numbers = '0123456789'
  
  // 随机决定字母和数字的数量（总共8位）
  const letterCount = Math.floor(Math.random() * 7) + 1  // 1-7个字母
  const numberCount = 8 - letterCount  // 剩余为数字
  
  // 生成字母部分（随机大小写）
  let result = []
  for (let i = 0; i < letterCount; i++) {
    // 随机决定是大写还是小写
    const isUpper = Math.random() < 0.5
    const letters = isUpper ? upperLetters : lowerLetters
    result.push(letters[Math.floor(Math.random() * letters.length)])
  }
  
  // 生成数字部分
  for (let i = 0; i < numberCount; i++) {
    result.push(numbers[Math.floor(Math.random() * numbers.length)])
  }
  
  // 打乱数组顺序
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  
  return result.join('')
}

// 在顶部添加新行
const addNewRowToTop = async () => {
  const newRow = {
    manuscriptId: generateRandomId(),
    article: '',
    amount: '',
    invoiceDate: '',
    paymentMethod: '',
    type: '',
    tag: '',
    company: '',
    taxId: '',
    contact: '',
    email: '',
    phone: '',
    notes: ''
  }
  
  try {
    const response = await axios.post('/api/invoice/create/', newRow)
    if (response.data.status === 'success') {
      newRow.id = response.data.id
      invoiceList.value.unshift(newRow)
      saveStatus.value = '已保存'
      setTimeout(() => {
        saveStatus.value = ''
      }, 2000)
    }
  } catch (error) {
    console.error('创建失败:', error)
    saveStatus.value = '创建失败'
  }
}

// 删除行
const deleteRow = async (index) => {
  if (confirm('确定要删除这一行吗？')) {
    try {
      const item = invoiceList.value[index]
      await axios.post('/api/invoice/delete/', {
        manuscriptId: item.manuscriptId
      })
      invoiceList.value.splice(index, 1)
      saveStatus.value = '已删除'
      setTimeout(() => {
        saveStatus.value = ''
      }, 2000)
    } catch (error) {
      console.error('删除失败:', error)
      saveStatus.value = '删除失败'
    }
  }
}

// 清空所有数据
const clearAllData = async () => {
  if (confirm('确定要清空所有数据吗？此操作不可恢复！')) {
    try {
      // 调用后端清空接口
      await axios.post('/api/invoice/clear/')
      invoiceList.value = []
      saveStatus.value = '已清空'
      setTimeout(() => {
        saveStatus.value = ''
      }, 2000)
    } catch (error) {
      console.error('清空失败:', error)
      saveStatus.value = '清空失败'
    }
  }
}

// 导出到Excel
const exportToExcel = () => {
  try {
    // 准备导出数据
    const exportData = filteredList.value.map(item => ({
      '稿件编号': item.manuscriptId,
      '文章': item.article,
      '金额': item.amount,
      '支付时间': item.invoiceDate,
      '支付方式': item.paymentMethod,
      '类型': item.type,
      '标签': item.tag,
      '单位': item.company,
      '识别号': item.taxId,
      '联系人': item.contact,
      '邮箱': item.email,
      '手机': item.phone,
      '备注': item.notes
    }))

    // 创建工作簿
    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '发票数据')

    // 导出文件
    const fileName = `发票数据_${new Date().toLocaleDateString()}.xlsx`
    XLSX.writeFile(wb, fileName)

    saveStatus.value = '导出成功'
    setTimeout(() => {
      saveStatus.value = ''
    }, 2000)
  } catch (error) {
    console.error('导出失败:', error)
    saveStatus.value = '导出失败'
  }
}

// 触发追加文件选择
const triggerAppendFileInput = () => {
  appendFileInput.value.click()
}

// 处理追加文件导入
const handleAppendFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
      const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 })

      // 跳过表头，从第二行开始处理数据
      const rows = jsonData.slice(1)
      
      // 创建新行并添加到数据库
      for (const row of rows) {
        const newInvoice = {
          manuscriptId: row[0] || generateRandomId(),
          article: row[1] || '',
          amount: row[2] || '',
          invoiceDate: row[3] || '',
          paymentMethod: row[4] || '',
          type: row[5] || '',
          tag: row[6] || '',
          company: row[7] || '',
          taxId: row[8] || '',
          contact: row[9] || '',
          email: row[10] || '',
          phone: row[11] || '',
          notes: row[12] || ''
        }

        // 调用后端创建接口
        await axios.post('/api/invoice/create/', newInvoice)
      }

      // 重新加载数据
      await loadData()
      saveStatus.value = '导入成功'
      setTimeout(() => {
        saveStatus.value = ''
      }, 2000)
    } catch (error) {
      console.error('导入失败:', error)
      saveStatus.value = '导入失败'
    } finally {
      event.target.value = '' // 清空文件输入
    }
  }
  reader.readAsArrayBuffer(file)
}

// 悬浮提示相关
const tooltip = ref({
  show: false,
  text: '',
  x: 0,
  y: 0
})
let showTimer = null
let hideTimer = null

// 显示悬浮提示
const showTooltip = (event, text) => {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  
  showTimer = setTimeout(() => {
    tooltip.value = {
      show: true,
      text: text,
      x: event.clientX + 10,
      y: event.clientY + 10
    }
  }, 500)
}

// 隐藏悬浮提示
const hideTooltip = () => {
  if (showTimer) {
    clearTimeout(showTimer)
    showTimer = null
  }
  
  hideTimer = setTimeout(() => {
    tooltip.value.show = false
  }, 100)
}

// 组件卸载时清理定时器
onUnmounted(() => {
  if (showTimer) clearTimeout(showTimer)
  if (hideTimer) clearTimeout(hideTimer)
})

// 识别文本
const recognitionText = ref('')

// 识别发票信息
const recognizeInvoice = async () => {
  const text = recognitionText.value
  if (!text.trim()) {
    alert('请先粘贴发票信息文本')
    return
  }
  
  // 定义正则表达式
  const patterns = {
    manuscriptId: /论文编号：(\d{4}-\d{4})/,
    article: /论文题目：(.*?)(?=\n|$)/,
    amount: /金额：(\d+)元/,
    invoiceDate: /缴费时间[（(]年月日[）)]：(\d{4})年(\d{1,2})月(\d{1,2})日/,
    paymentMethod: /缴费方式[（(].*?[）)]：(.*?)(?=\n|$)/,
    company: /发票抬头：(.*?)(?=\n|$)/,
    taxId: /纳税人识别号：(.*?)(?=\n|$)/,
    contact: /姓名[（(].*?[）)]：(.*?)(?=\n|$)/,
    email: /收信邮箱[（(].*?[）)]：(.*?)(?=\n|$)/,
    phone: /手机号[（(].*?[）)]：(.*?)(?=\n|$)/
  }
  
  // 提取信息
  const extractInfo = {}
  for (const [field, pattern] of Object.entries(patterns)) {
    const match = text.match(pattern)
    if (match) {
      if (field === 'invoiceDate') {
        // 格式化日期
        const [, year, month, day] = match
        extractInfo[field] = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
      } else if (field === 'amount') {
        // 提取数字
        extractInfo[field] = match[1]
      } else {
        extractInfo[field] = match[1]
      }
    }
  }
  
  // 检查是否识别到任何信息
  if (Object.keys(extractInfo).length === 0) {
    alert('未能识别到任何有效信息，请检查文本格式')
    return
  }
  
  // 准备新行数据
  const newRowData = {
    manuscriptId: extractInfo.manuscriptId || '',
    article: extractInfo.article || '',
    amount: extractInfo.amount || '',
    invoiceDate: extractInfo.invoiceDate || '',
    paymentMethod: extractInfo.paymentMethod || '',
    type: '版面费', // 默认类型
    tag: '', // 空标签
    company: extractInfo.company || '',
    taxId: extractInfo.taxId || '',
    contact: extractInfo.contact || '',
    email: extractInfo.email || '',
    phone: extractInfo.phone || '',
    notes: ''
  }
  
  try {
    // 调用后端创建接口
    const response = await axios.post('/api/invoice/create/', newRowData)
    
    if (response.data.status === 'success') {
      // 使用后端返回的ID创建新行
      const newRow = {
        ...newRowData,
        id: response.data.id
      }
      
      // 添加到列表顶部
      invoiceList.value.unshift(newRow)
      
      // 清空识别文本
      recognitionText.value = ''
      
      // 显示成功提示
      alert('已成功识别并新增一行数据，需确认后手动保存')
    } else {
      throw new Error(response.data.message || '创建记录失败')
    }
  } catch (error) {
    console.error('创建记录失败:', error)
    alert('创建记录失败: ' + (error.response?.data?.message || error.message))
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

/* 可编辑下拉框样式 */
.editable-select {
  position: relative;
}

.editable-select input {
  width: 100%;
}

.editable-select select {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  opacity: 0;
  height: 100%;
  cursor: pointer;
}

.editable-select select:focus {
  width: 100%;
  opacity: 1;
}

.editable-select:hover select {
  width: 100%;
  opacity: 1;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
}

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

/* 排序列样式 */
.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
  padding-right: 25px !important;
}

.sortable:hover {
  background-color: #e9ecef;
}

.sortable i {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
}

/* 排序图标颜色 */
.bi-arrow-up,
.bi-arrow-down {
  color: #0d6efd;
}

.bi-arrow-down-up {
  color: #6c757d;
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

/* 导出按钮样式 */
.btn i {
  margin-right: 5px;
}

/* 导入按钮组样式 */
.btn-primary + .btn-primary {
  margin-left: -1px;  /* 让两个导入按钮紧贴 */
}

/* 修改未保存提示的样式 */
.save-status:contains('有未保存的修改') {
  color: #dc3545;
  font-weight: bold;
  background-color: #fff3cd;
  border: 2px solid #dc3545;
}

/* 自定义悬浮提示框样式 */
.custom-tooltip {
  position: fixed;
  z-index: 9999;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  max-width: 300px;
  word-wrap: break-word;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 添加单元格文本溢出处理 */
.form-control {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recognition-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.recognition-textarea {
  font-family: monospace;
  resize: vertical;
  min-height: 120px;
  max-height: 400px;
  overflow-y: auto;
}

/* 美化滚动条 */
.recognition-textarea::-webkit-scrollbar {
  width: 8px;
}

.recognition-textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.recognition-textarea::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.recognition-textarea::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.recognition-textarea::placeholder {
  white-space: pre;
  font-family: monospace;
}
</style> 