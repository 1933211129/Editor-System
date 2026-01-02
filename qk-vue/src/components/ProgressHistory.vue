<template>
  <div class="main-content">
    <h3>📊 进度管理历史记录</h3>
    
    <!-- 筛选区域 -->
    <div class="filter-section mb-3">
      <div class="card">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-2">
              <label class="form-label">年份</label>
              <select class="form-select form-select-sm" v-model="filters.year">
                <option value="">全部</option>
                <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}年</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">月份</label>
              <select class="form-select form-select-sm" v-model="filters.month">
                <option value="">全部</option>
                <option v-for="m in monthOptions" :key="m" :value="m">{{ m }}月</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">关键词搜索</label>
              <input 
                type="text" 
                class="form-control form-control-sm" 
                v-model="filters.keyword" 
                placeholder="文件名、责编、备注"
              >
            </div>
            <div class="col-md-2 d-flex align-items-end">
              <button class="btn btn-primary btn-sm w-100" @click="loadData">
                <i class="bi bi-search"></i> 查询
              </button>
            </div>
            <div class="col-md-2 d-flex align-items-end">
              <button class="btn btn-outline-secondary btn-sm w-100" @click="resetFilters">
                <i class="bi bi-arrow-clockwise"></i> 重置
              </button>
            </div>
          </div>
          <div class="row mt-2">
            <div class="col-12">
              <button class="btn btn-success btn-sm" @click="exportToExcel" :disabled="loading || filteredData.length === 0">
                <i class="bi bi-file-earmark-excel"></i> 导出Excel
              </button>
              <span class="ms-3 text-muted">共 {{ filteredData.length }} 条记录</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-section">
      <div class="card">
        <div class="card-body">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-2">正在加载数据...</p>
          </div>
          <div v-else-if="filteredData.length === 0" class="text-center py-5">
            <i class="bi bi-inbox" style="font-size: 48px; color: #6c757d;"></i>
            <p class="mt-2 text-muted">暂无数据</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-bordered table-hover table-sm">
              <thead class="table-light">
                <tr>
                  <th>#</th>
                  <th>归档时间</th>
                  <th>版次</th>
                  <th>文件名</th>
                  <th>责编</th>
                  <th>版面费</th>
                  <th>校对情况</th>
                  <th>一、二校编辑</th>
                  <th>三校编辑</th>
                  <th>终校编辑</th>
                  <th>责编时间</th>
                  <th>校对时间</th>
                  <th>备注</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in filteredData" :key="item.id">
                  <td>{{ index + 1 }}</td>
                  <td>{{ item.archived_at }}</td>
                  <td>{{ item.edition || '-' }}</td>
                  <td>{{ item.filename }}</td>
                  <td>{{ item.editor_in_charge || '-' }}</td>
                  <td>{{ item.page_fee }}</td>
                  <td>{{ item.proof_status }}</td>
                  <td>{{ item.first_second_proof_editor || '-' }}</td>
                  <td>{{ item.third_proof_editor || '-' }}</td>
                  <td>{{ item.final_proof_editor || '-' }}</td>
                  <td>{{ item.editor_time || '-' }}</td>
                  <td>{{ item.proof_time || '-' }}</td>
                  <td>{{ item.remarks || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'

// 响应式数据
const dataList = ref([])
const loading = ref(false)
const filters = ref({
  year: '',
  month: '',
  keyword: ''
})

// 生成年份选项（当前年份往前1年，往后10年）
const currentYear = new Date().getFullYear()
const yearOptions = ref([])
for (let i = currentYear + 10; i >= currentYear - 1; i--) {
  yearOptions.value.push(i)
}

// 月份选项
const monthOptions = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

// 过滤后的数据
const filteredData = computed(() => {
  return dataList.value
})

// 重置筛选
const resetFilters = () => {
  filters.value = {
    year: '',
    month: '',
    keyword: ''
  }
  loadData()
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const params = {}
    
    if (filters.value.year) {
      params.year = filters.value.year
    }
    if (filters.value.month) {
      params.month = filters.value.month
    }
    if (filters.value.keyword) {
      params.keyword = filters.value.keyword
    }
    
    const response = await axios.get('/api/journal-progress-summary/', { params })
    
    if (response.data.status === 'success') {
      dataList.value = response.data.data
    } else {
      console.error('加载数据失败:', response.data.message)
      alert('加载数据失败: ' + response.data.message)
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    alert('加载数据失败，请重试')
  } finally {
    loading.value = false
  }
}

// 导出到Excel
const exportToExcel = () => {
  try {
    if (filteredData.value.length === 0) {
      alert('没有数据可导出')
      return
    }
    
    // 准备导出数据
    const exportData = filteredData.value.map(item => ({
      '归档时间': item.archived_at,
      '版次': item.edition || '',
      '文件名': item.filename,
      '责编': item.editor_in_charge || '',
      '版面费': item.page_fee,
      '校对情况': item.proof_status,
      '一、二校编辑': item.first_second_proof_editor || '',
      '三校编辑': item.third_proof_editor || '',
      '终校编辑': item.final_proof_editor || '',
      '责编时间': item.editor_time || '',
      '校对时间': item.proof_time || '',
      '备注': item.remarks || ''
    }))
    
    // 创建工作簿
    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '进度历史')
    
    // 设置列宽
    const colWidths = [
      { wch: 20 },  // 归档时间
      { wch: 12 },  // 版次
      { wch: 30 },  // 文件名
      { wch: 10 },  // 责编
      { wch: 10 },  // 版面费
      { wch: 10 },  // 校对情况
      { wch: 12 },  // 一、二校编辑
      { wch: 10 },  // 三校编辑
      { wch: 10 },  // 终校编辑
      { wch: 12 },  // 责编时间
      { wch: 12 },  // 校对时间
      { wch: 20 }   // 备注
    ]
    ws['!cols'] = colWidths
    
    // 导出文件
    const dateStr = new Date().toLocaleDateString().replace(/\//g, '-')
    const fileName = `期刊进度历史_${dateStr}.xlsx`
    XLSX.writeFile(wb, fileName)
    
    alert('导出成功！')
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.main-content {
  margin-left: 0;
  padding: 20px;
  min-height: 100vh;
  background: #f8f9fa;
}

.filter-section {
  margin-top: 20px;
}

.filter-section .card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-section {
  margin-top: 20px;
}

.table-section .card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table {
  font-size: 14px;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 10;
}

.table td {
  vertical-align: middle;
}

.table-responsive {
  max-height: 70vh;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
  
  .table {
    font-size: 12px;
  }
  
  .table th,
  .table td {
    padding: 4px;
  }
}
</style>
