<template>
  <div class="recipient-manage">
    <!-- 页面标题和操作栏 -->
    <div class="header-section">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="page-title">
          <i class="fas fa-address-book me-2"></i>
          收件人管理
        </h2>
        <div class="header-actions">
          <button class="btn btn-outline-primary me-2" @click="showImportModal">
            <i class="fas fa-file-import me-1"></i>批量导入
          </button>
          <button class="btn btn-primary" @click="showAddModal">
            <i class="fas fa-plus me-1"></i>添加收件人
          </button>
        </div>
      </div>

      <!-- 搜索和筛选栏 -->
      <div class="filter-section mb-4">
        <div class="row">
          <div class="col-md-4">
            <div class="search-box">
              <i class="fas fa-search search-icon"></i>
              <input 
                type="text" 
                class="form-control ps-5" 
                placeholder="搜索姓名或邮箱..."
                v-model="searchQuery"
                @input="handleSearch"
              >
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="selectedGroup" @change="filterByGroup">
              <option value="">所有分组</option>
              <option v-for="group in groups" :key="group.name" :value="group.name">
                {{ group.name }} ({{ group.count }})
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="fas fa-undo me-1"></i>重置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分组管理区域 -->
    <div class="groups-section mb-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="section-title">分组管理</h5>
        <button class="btn btn-sm btn-outline-primary" @click="showGroupModal">
          <i class="fas fa-plus me-1"></i>新建分组
        </button>
      </div>
      <div class="groups-container">
        <div 
          v-for="group in groups" 
          :key="group.name"
          class="group-card"
          :class="{ active: selectedGroup === group.name }"
          @click="selectGroup(group.name)"
        >
          <div class="group-info">
            <h6 class="group-name">{{ group.name }}</h6>
            <span class="group-count">{{ group.count }} 人</span>
          </div>
          <div class="group-actions">
            <button class="btn btn-sm btn-link text-primary py-0 me-1" @click.stop="editGroup(group)">
              <i class="fas fa-edit me-1"></i>编辑
            </button>
            <button class="btn btn-sm btn-link text-danger py-0" @click.stop="deleteGroup(group.name)">
              <i class="fas fa-trash me-1"></i>删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 收件人列表 -->
    <div class="recipients-section">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="results-info">
          <div class="d-flex align-items-center">
            <span class="text-muted me-3">共 {{ totalCount }} 个收件人</span>
          </div>
          <span v-if="selectedRecipients.length > 0" class="ms-3 text-primary">
            已选择 {{ selectedRecipients.length }} 个
          </span>
        </div>
        <div class="batch-actions" v-if="selectedRecipients.length > 0">
          <button class="btn btn-sm btn-outline-danger" @click="batchDelete">
            <i class="fas fa-trash me-1"></i>批量删除
          </button>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th width="50">
                <input 
                  type="checkbox" 
                  class="form-check-input"
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                >
              </th>
              <th>姓名</th>
              <th>邮箱</th>
              <th>分组</th>
              <th>备注</th>
              <th width="120">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="recipient in recipients" :key="recipient.id">
              <td>
                <input 
                  type="checkbox" 
                  class="form-check-input"
                  :value="recipient.id"
                  v-model="selectedRecipients"
                >
              </td>
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar-circle me-2">
                    {{ recipient.name.charAt(0).toUpperCase() }}
                  </div>
                  <strong>{{ recipient.name }}</strong>
                </div>
              </td>
              <td>
                <a :href="`mailto:${recipient.email}`" class="text-decoration-none">
                  {{ recipient.email }}
                </a>
              </td>
              <td class="align-middle" style="min-width: 150px;">
                <!-- 多分组展示（只读chips） -->
                <div v-if="recipient.groups && recipient.groups.length" class="mb-2 d-flex flex-wrap gap-1">
                  <span
                    v-for="g in recipient.groups"
                    :key="g"
                    class="badge rounded-pill bg-secondary me-1 mb-1"
                    :title="g"
                  >
                    {{ g }}
                  </span>
                </div>
                <!-- 已取消行内分组选择，改由“分组管理”对话框统一维护 -->
              </td>
              <td>
                <span class="text-muted" :title="recipient.remark">
                  {{ recipient.remark ? (recipient.remark.length > 20 ? recipient.remark.substring(0, 20) + '...' : recipient.remark) : '-' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-link text-primary me-2" @click="editRecipient(recipient)">
                  <i class="fas fa-edit me-1"></i>编辑
                </button>
                <button class="btn btn-sm btn-link text-danger" @click="deleteRecipient(recipient.id)">
                  <i class="fas fa-trash me-1"></i>删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <nav v-if="totalPages > 1" class="mt-4">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="changePage(1)">首页</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="changePage(currentPage - 1)">上一页</button>
          </li>
          <li 
            v-for="page in visiblePages" 
            :key="page"
            class="page-item" 
            :class="{ active: currentPage === page }"
          >
            <button class="page-link" @click="changePage(page)">{{ page }}</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link" @click="changePage(currentPage + 1)">下一页</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link" @click="changePage(totalPages)">尾页</button>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 添加/编辑收件人模态框 -->
    <div class="modal fade" tabindex="-1" ref="recipientModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? '编辑收件人' : '添加收件人' }}</h5>
            <button type="button" class="btn-close" @click="hideRecipientModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveRecipient">
              <div class="mb-3">
                <label class="form-label">姓名 <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="currentRecipient.name"
                  placeholder="请输入姓名"
                  required
                >
              </div>
              <div class="mb-3">
                <label class="form-label">邮箱 <span class="text-danger">*</span></label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="currentRecipient.email"
                  placeholder="请输入邮箱地址"
                  required
                >
              </div>
              <!-- 取消在联系人编辑中选择分组，统一在“分组管理”中维护成员关系 -->
              <div class="mb-3">
                <label class="form-label">备注</label>
                <textarea 
                  class="form-control" 
                  rows="3"
                  v-model="currentRecipient.remark"
                  placeholder="请输入备注信息"
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideRecipientModal">取消</button>
            <button type="button" class="btn btn-primary" @click="saveRecipient">保存</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量导入模态框 -->
    <div class="modal fade" tabindex="-1" ref="importModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-file-import me-2"></i>批量导入收件人
            </h5>
            <button type="button" class="btn-close" @click="hideImportModal"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <h6>1. 粘贴数据</h6>
                <p class="text-muted small">
                  支持从 Excel, CSV, TXT 文件中直接复制粘贴。
                  <br />
                  格式: <strong>中文姓名 + 邮箱</strong>（可带备注）
                  <br />
                  分隔符: 逗号, 分号或制表符(Tab)。
                  <br />
                  注意：<strong>姓名必须是中文</strong>，系统会将“中文部分”识别为姓名，将其后的内容识别为邮箱。
                </p>
                <textarea
                  class="form-control"
                  rows="10"
                  v-model="importText"
                  placeholder="张三,zhangsan@example.com\n李四 lisi@example.com"
                ></textarea>
                <div class="mt-3">
                  <h6>2. 选择分组 (可选)</h6>
                  <select class="form-select" v-model="importGroupId">
                    <option :value="null">不指定分组</option>
                    <option v-for="group in groups" :key="group.name" :value="group.name">
                      {{ group.name }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-md-6">
                <h6>3. 数据预览</h6>
                <div class="table-responsive" style="max-height: 300px;">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>姓名</th>
                        <th>邮箱</th>
                        <th>备注</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="parsedData.length === 0">
                        <td colspan="3" class="text-center text-muted">待粘贴数据...</td>
                      </tr>
                      <tr
                        v-for="(item, index) in parsedData"
                        :key="index"
                        :class="{ 'table-danger': !item.isValid }"
                      >
                        <td>{{ item.name }}</td>
                        <td>
                          {{ item.email }}
                          <span v-if="!item.isValid" class="text-danger small ms-1">
                            (邮箱格式错误)
                          </span>
                        </td>
                        <td>{{ item.remark }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-if="importReport" class="alert mt-3" :class="importReport.success > 0 ? 'alert-success' : 'alert-warning'">
                  {{ importReport.message }}
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideImportModal">关闭</button>
            <button
              type="button"
              class="btn btn-primary"
              @click="importRecipients"
              :disabled="validImportCount === 0"
            >
              <i class="fas fa-check me-1"></i>
              导入 {{ validImportCount }} 条有效数据
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建联系人并添加到分组模态框 -->
    <div class="modal fade" tabindex="-1" ref="newMemberModal" style="z-index: 1060;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">新建联系人到 "{{ currentGroup.name }}"</h5>
            <button type="button" class="btn-close" @click="hideNewMemberModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveNewMember">
              <div class="mb-3">
                <label class="form-label">姓名 <span class="text-danger">*</span></label>
                <input type="text" class="form-control" v-model="newMemberForm.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">邮箱 <span class="text-danger">*</span></label>
                <input type="email" class="form-control" v-model="newMemberForm.email" required>
              </div>
              <div class="mb-3">
                <label class="form-label">备注</label>
                <textarea class="form-control" rows="2" v-model="newMemberForm.remark"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideNewMemberModal">取消</button>
            <button type="button" class="btn btn-primary" @click="saveNewMember">确认添加</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 已移除批量分组模态框 -->

    <!-- 分组管理模态框 -->
    <div class="modal fade" tabindex="-1" ref="groupModal" style="z-index: 1050;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditingGroup ? '编辑分组' : '新建分组' }}</h5>
            <button type="button" class="btn-close" @click="hideGroupModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">分组名称 <span class="text-danger">*</span></label>
              <input 
                type="text" 
                class="form-control" 
                v-model="currentGroup.name"
                placeholder="请输入分组名称"
                required
              >
            </div>

            <!-- 成员管理 -->
            <div v-if="isEditingGroup" class="mt-4">
              <h6>成员管理</h6>
              <!-- 搜索添加 -->
              <div class="search-box mb-2">
                <i class="fas fa-search search-icon"></i>
                <input 
                  type="text" 
                  class="form-control ps-5" 
                  placeholder="搜索姓名或邮箱添加成员..."
                  v-model="groupMemberSearch"
                >
              </div>
              <ul v-if="groupMemberSearch && filteredAddableMembers.length" class="list-group mb-2" style="max-height: 150px; overflow-y: auto;">
                <li v-for="r in filteredAddableMembers" :key="r.id" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" @click="addMemberToGroup(r)">
                  <span>{{ r.name }} ({{ r.email }})</span>
                  <button class="btn btn-sm btn-outline-primary"><i class="fas fa-plus"></i></button>
                </li>
              </ul>

              <div class="d-flex justify-content-between align-items-center">
                <p class="text-muted small mb-1">当前成员 ({{ currentGroupMembers.length }}人)</p>
                <button class="btn btn-sm btn-outline-secondary" @click="showNewMemberModal">
                  <i class="fas fa-user-plus me-1"></i>新建并添加
                </button>
              </div>
              <ul class="list-group" style="max-height: 200px; overflow-y: auto;">
                 <li v-if="!currentGroupMembers.length" class="list-group-item text-center text-muted">暂无成员</li>
                 <li v-for="member in currentGroupMembers" :key="member.id" class="list-group-item d-flex justify-content-between align-items-center">
                  <span>{{ member.name }}</span>
                  <button class="btn btn-sm btn-outline-danger" @click="removeMemberFromGroup(member)">
                    <i class="fas fa-times"></i>
                  </button>
                </li>
              </ul>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary me-auto" :disabled="isCleaning" @click="cleanupUngrouped">
              <i class="fas fa-broom me-1"></i>{{ isCleaning ? '清理中...' : '一键清理默认分组冲突' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="hideGroupModal">取消</button>
            <button type="button" class="btn btn-primary" @click="saveGroup">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* global defineExpose */
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

// 响应式数据
const recipients = ref([])
const groups = ref([])
const groupsEtag = ref('') // 用于 If-None-Match 条件请求

const searchQuery = ref('')
const selectedGroup = ref('')
const selectedRecipients = ref([])
const currentPage = ref(1)
const pageSize = ref(10) // 保守分页 10~20，默认 10
const totalPages = ref(1)
const totalCount = ref(0)
const isLoading = ref(false)

// 模态框相关
const recipientModal = ref(null)
const groupModal = ref(null)
const importModal = ref(null)
// 已移除批量分组模态框
const newMemberModal = ref(null)
const isEditing = ref(false)
const isEditingGroup = ref(false)
const isCleaning = ref(false)

// 批量导入相关
const importText = ref('')
const importGroupId = ref(null)
const importReport = ref(null)

// 已移除批量分组相关

// 分组成员管理相关
const groupMemberSearch = ref('')
const addableCandidates = ref([]) // 来自后端的可添加候选
const newMemberForm = ref({ name: '', email: '', remark: '' })

const currentRecipient = ref({
  id: '',
  name: '',
  email: '',
  remark: '',
  createTime: ''
})

const currentGroup = ref({
  id: '',
  name: '',
  description: ''
})


// 计算属性
// 服务端分页，直接渲染 recipients，分页数据由后端返回

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const parsedData = computed(() => {
  if (!importText.value.trim()) return []

  const lines = importText.value.trim().split(/\r?\n/)
  // 邮箱匹配：允许常见字符与任意长度 TLD（全局用于查找首个邮箱）
  const emailRegex = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/
  // 中文姓名（支持中日韩统一表意文字与常见间隔点“·•・”），用于在邮箱前文本中优先提取
  const chineseNameAtStart = /^[\s\u3000]*([\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF·•・]+)[\s\u3000]*/
  // 更宽松的分隔符集合：制表、逗号、分号、中文分隔符、竖线、破折号、冒号等
  const splitter = /[\t,;，；、|:\-—\s\u3000]+/

  const stripPunctuation = (text) => {
    // 去除常见包裹符号
    return (text || '').replace(/^[<(\u005B【『（]+/, '').replace(/[>)(\u005D】』）]+$/, '')
  }

  const removeInvisibleSpaces = (text) => {
    // 移除零宽字符与常见不可见空白
    return (text || '').replace(/[\u200B-\u200D\uFEFF\u00A0\u202F\u205F]/g, '')
  }

  const results = []
  for (let raw of lines) {
    // 归一化 + 移除不可见空白
    let line = (raw || '').normalize('NFKC')
    line = removeInvisibleSpaces(line).trim()
    if (!line) continue

    let name = ''
    let email = ''
    let remark = ''

    // 1) 总是先在整行中抓取首个邮箱
    const emailMatch = line.match(emailRegex)
    if (emailMatch) {
      email = emailMatch[0]
      const emailIndex = line.indexOf(email)
      const before = line.slice(0, emailIndex).trim()
      const after = line.slice(emailIndex + email.length).trim()

      // 2) 从邮箱前文本推断姓名：优先整段中文姓名；否则取前文本最后一个片段
      if (before) {
        const nameMatch = before.match(chineseNameAtStart)
        if (nameMatch) {
          name = (nameMatch[1] || '').trim()
        }
        if (!name) {
          const parts = before.split(splitter).filter(Boolean)
          name = parts.length > 0 ? parts[parts.length - 1] : ''
        }
      }
      if (!name) {
        name = email.split('@')[0]
      }

      // 3) 邮箱后的文本作为备注，去除包裹符号
      if (after) {
        remark = stripPunctuation(after)
      }
    }

    const isValid = Boolean(email && emailRegex.test(email))
    results.push({ name, email, remark, isValid })
  }

  return results
})

const validImportCount = computed(() => {
  return parsedData.value.filter(item => item.isValid).length
})

const currentGroupMembers = computed(() => {
  if (!currentGroup.value || !currentGroup.value.name) return []
  return recipients.value.filter(r => (r.groupName || '默认分组') === currentGroup.value.name)
})

const filteredAddableMembers = computed(() => {
  if (!groupMemberSearch.value) return []
  const currentGroupName = currentGroup.value.name
  // 过滤掉已在该组的成员，并做去重
  const seen = new Set()
  const list = []
  for (const r of addableCandidates.value) {
    const notMember = (r.groupName || '默认分组') !== currentGroupName
    if (notMember && !seen.has(r.id)) {
      seen.add(r.id)
      list.push(r)
    }
    if (list.length >= 10) break
  }
  return list
})

// 监听搜索框，向后端全局查询可添加成员（包括中文）
let searchTimer = null
watch(groupMemberSearch, (val) => {
  if (searchTimer) clearTimeout(searchTimer)
  if (!val || !val.trim()) {
    addableCandidates.value = []
    return
  }
  // 简单防抖
  searchTimer = setTimeout(async () => {
    try {
      const resp = await axios.get('/api/recipients/', {
        params: {
          page: 1,
          page_size: 50, // 仅取 Top 50
          search: val.trim(),
          group_name: ''
        }
      })
      if (resp.data && resp.data.status === 'success') {
        const data = resp.data.data
        addableCandidates.value = (data.recipients || []).map(r => ({ ...r, groupName: r.groupName || '默认分组' }))
      } else {
        addableCandidates.value = []
      }
    } catch (e) {
      console.error('搜索候选失败', e)
      addableCandidates.value = []
    }
  }, 300)
})


const isAllSelected = computed(() => {
  return recipients.value.length > 0 && 
         selectedRecipients.value.length === recipients.value.length
})


// 方法
const loadRecipients = async () => {
  try {
    isLoading.value = true
    const response = await axios.get('/api/recipients/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value,
        group_name: selectedGroup.value
      }
    })
    if (response.data.status === 'success') {
      const data = response.data.data
      recipients.value = data.recipients.map(r => ({...r, groupName: r.groupName || '默认分组'}))
      totalPages.value = data.totalPages
      totalCount.value = data.total
    } else {
      alert('加载联系人失败: ' + response.data.message)
    }
  } catch (error) {
    console.error('加载联系人异常:', error)
    alert('加载联系人异常，请查看控制台')
  } finally {
    isLoading.value = false
  }
}

// 分组列表条件请求（ETag）
const loadGroups = async () => {
  try {
    const headers = {}
    if (groupsEtag.value) headers['If-None-Match'] = groupsEtag.value
    const resp = await axios.get('/api/groups/', { headers })
    // 200 正常返回
    if (resp.status === 200 && resp.data && resp.data.status === 'success') {
      groups.value = resp.data.data || []
      const etag = resp.headers && (resp.headers.etag || resp.headers.ETag)
      if (etag) groupsEtag.value = etag
    }
  } catch (e) {
    // 304 Not Modified 时，axios 会抛错或进入 catch，需判断响应码
    if (e.response && e.response.status === 304) {
      // 未修改：沿用现有 groups
      return
    }
    console.error('加载分组失败', e)
  }
}

const showAddModal = () => {
  isEditing.value = false
  currentRecipient.value = {
    id: '',
    name: '',
    email: '',
    remark: '',
    createTime: ''
  }
  showRecipientModal()
}

const editRecipient = (recipient) => {
  isEditing.value = true
  currentRecipient.value = { ...recipient }
  showRecipientModal()
}

const showRecipientModal = async () => {
  recipientModal.value.style.display = 'block'
  recipientModal.value.classList.add('show')
}

const hideRecipientModal = () => {
  recipientModal.value.style.display = 'none'
  recipientModal.value.classList.remove('show')
}

const saveRecipient = async () => {
  if (!currentRecipient.value.name.trim() || !currentRecipient.value.email.trim()) {
    alert('请填写必填字段')
    return
  }

  try {
    if (isEditing.value) {
      await axios.put(`/api/recipients/${currentRecipient.value.id}/update/`, {
        name: currentRecipient.value.name,
        email: currentRecipient.value.email,
        remark: currentRecipient.value.remark || ''
      })
    } else {
      await axios.post('/api/recipients/create/', {
        name: currentRecipient.value.name,
        email: currentRecipient.value.email,
        remark: currentRecipient.value.remark || ''
      })
    }
    await loadRecipients()
    hideRecipientModal()
  } catch (e) {
    alert('保存失败，请检查表单或重试')
    console.error(e)
  }
}

const deleteRecipient = async (id) => {
  if (!confirm('确定要删除这个收件人吗？')) return
  try {
    await axios.delete(`/api/recipients/${id}/delete/`)
    await loadRecipients()
  } catch (e) {
    alert('删除失败')
    console.error(e)
  }
}


const showNewMemberModal = () => {
  newMemberForm.value = { name: '', email: '', remark: '' }
  newMemberModal.value.style.display = 'block'
  newMemberModal.value.classList.add('show')
}

const hideNewMemberModal = () => {
  newMemberModal.value.style.display = 'none'
  newMemberModal.value.classList.remove('show')
}

const saveNewMember = async () => {
  const { name, email, remark } = newMemberForm.value
  if (!name.trim() || !email.trim()) {
    alert('姓名和邮箱不能为空')
    return
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    alert('请输入有效的邮箱地址')
    return
  }
  try {
    await axios.post('/api/recipients/create/', {
      name,
      email,
      remark,
      groupName: currentGroup.value.name || '默认分组'
    })
    await loadRecipients()
    hideNewMemberModal()
  } catch (e) {
    alert('创建成员失败')
    console.error(e)
  }
}

const addMemberToGroup = async (recipient) => {
  try {
    await axios.post('/api/recipients/append-to-group/', {
      ids: [recipient.id],
      groupName: currentGroup.value.name || '默认分组'
    })
    groupMemberSearch.value = ''
    await loadRecipients()
  } catch (e) {
    alert('添加到分组失败')
    console.error(e)
  }
}

const removeMemberFromGroup = async (recipient) => {
  try {
    await axios.post('/api/recipients/remove-from-group/', {
      ids: [recipient.id],
      groupName: currentGroup.value.name
    })
    await loadRecipients()
  } catch (e) {
    alert('移出分组失败')
    console.error(e)
  }
}

// 已移除行内更新分组逻辑，统一在“分组管理”处理

const showGroupModal = () => {
  isEditingGroup.value = false
  currentGroup.value = { id: '', name: '', description: '' }
  groupMemberSearch.value = ''
  groupModal.value.style.display = 'block'
  groupModal.value.classList.add('show')
}

const originalGroupName = ref('')
const editGroup = (group) => {
  isEditingGroup.value = true
  currentGroup.value = { ...group }
  originalGroupName.value = group.name
  groupMemberSearch.value = ''
  groupModal.value.style.display = 'block'
  groupModal.value.classList.add('show')
}

const hideGroupModal = () => {
  groupModal.value.style.display = 'none'
  groupModal.value.classList.remove('show')
}

const saveGroup = async () => {
  if (!currentGroup.value.name.trim()) {
    alert('请输入分组名称')
    return
  }
  try {
    if (isEditingGroup.value) {
      // 仅当名称有变更时才重命名；否则不调用后端重命名
      if (currentGroup.value.name !== originalGroupName.value) {
        await axios.post('/api/groups/rename/', {
          oldName: originalGroupName.value,
          newName: currentGroup.value.name
        })
      }
      // 若当前有搜索结果，保存时将这些候选批量加入该分组
      if (filteredAddableMembers.value && filteredAddableMembers.value.length > 0) {
        const ids = filteredAddableMembers.value.map(m => m.id)
        await axios.post('/api/recipients/append-to-group/', {
          ids,
          groupName: currentGroup.value.name
        })
      }
    } else {
      // 新建分组：先在后端显式创建分组（支持空分组显示）
      await axios.post('/api/groups/create/', { name: currentGroup.value.name })
      // 如果当前选择有成员，批量移动到新分组
      const ids = currentGroupMembers.value.map(m => m.id)
      if (ids.length > 0) {
        await axios.post('/api/recipients/batch-update-group/', {
          ids,
          groupName: currentGroup.value.name
        })
      }
    }
    await loadRecipients()
    hideGroupModal()
  } catch (e) {
    alert('保存分组失败')
    console.error(e)
  }
}

// 一键清理：“默认分组”仅在联系人没有其它分组时才保留
const cleanupUngrouped = async () => {
  if (!confirm('执行清理将移除那些“已在其它分组仍挂默认分组”的关系，并给完全无分组的联系人加上默认分组。确认继续？')) return
  try {
    isCleaning.value = true
    const resp = await axios.post('/api/recipients/cleanup-ungrouped-invariant/', {})
    if (resp.data && resp.data.status === 'success') {
      const d = resp.data.data || {}
      alert(`清理完成：\n移除默认分组：${d.removed_default || 0}\n补充默认分组：${d.added_default || 0}`)
      await loadRecipients()
    } else {
      alert('清理失败：' + (resp.data && resp.data.message ? resp.data.message : '未知错误'))
    }
  } catch (e) {
    console.error('清理异常', e)
    alert('清理异常，请查看控制台')
  } finally {
    isCleaning.value = false
  }
}

const deleteGroup = async (groupName) => {
  if (!confirm('确定要删除这个分组吗？分组下的收件人将移至默认分组。')) return
  try {
    await axios.delete('/api/groups/delete/', { data: { groupName } })
    await loadRecipients()
  } catch (e) {
    alert('删除分组失败')
    console.error(e)
  }
}

const selectGroup = (groupName) => {
  selectedGroup.value = selectedGroup.value === groupName ? '' : groupName
  filterByGroup()
}

const filterByGroup = () => {
  currentPage.value = 1
  loadRecipients()
}


// 主列表搜索 300ms 防抖，仅服务端搜索
let mainSearchTimer = null
const handleSearch = () => {
  if (mainSearchTimer) clearTimeout(mainSearchTimer)
  mainSearchTimer = setTimeout(() => {
    currentPage.value = 1
    loadRecipients()
  }, 300)
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedGroup.value = ''
  currentPage.value = 1
  loadRecipients()
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedRecipients.value = []
  } else {
    selectedRecipients.value = recipients.value.map(r => r.id)
  }
}

const batchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedRecipients.value.length} 个收件人吗？`)) return
  try {
    await axios.post('/api/recipients/batch-delete/', { ids: selectedRecipients.value })
    selectedRecipients.value = []
    await loadRecipients()
  } catch (e) {
    alert('批量删除失败')
    console.error(e)
  }
}


const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadRecipients()
  }
}

// 向父组件暴露刷新方法：保持当前筛选与分页，重新加载列表与分组
defineExpose({
  refresh: () => {
    if (typeof loadGroups === 'function') {
      loadGroups()
    }
    if (typeof loadRecipients === 'function') {
      loadRecipients()
    }
  }
})

const hideImportModal = () => {
  importModal.value.style.display = 'none'
  importModal.value.classList.remove('show')
}

const importRecipients = async () => {
  const validData = parsedData.value.filter(item => item.isValid)
  if (validData.length === 0) {
    importReport.value = { success: 0, message: '没有有效的收件人可导入。' }
    return
  }
  try {
    const payload = {
      recipients: validData.map(item => ({ name: item.name, email: item.email, remark: item.remark })),
      groupName: importGroupId.value || '默认分组'
    }
    const res = await axios.post('/api/recipients/import/', payload)
    await loadRecipients()
    // 移除未使用变量 total，避免 ESLint no-unused-vars 报错
    const data = res.data?.data || {}
    const created = data.createdCount || 0
    const updated = data.updatedCount || 0
    const errors = Array.isArray(data.errors) ? data.errors : []
    const failureCount = data.errorCount || errors.length

    let message = `导入完成：新增 ${created} 条，更新 ${updated} 条。`
    if (failureCount > 0) {
      message += ` 忽略 ${failureCount} 条（缺失必填或格式问题）。`
      // 附带部分后端错误以便定位
      const previewErrors = errors.slice(0, 5)
      if (previewErrors.length > 0) {
        message += ` 例如：${previewErrors.join('；')}。`
      }
    }
    if (payload.groupName && payload.groupName !== '默认分组') {
      message += ` 已加入分组 “${payload.groupName}”（不移除原分组）。`
    }
    importReport.value = { success: created + updated, message }
  } catch (e) {
    alert('导入失败')
    console.error(e)
  }
}

const showImportModal = () => {
  importReport.value = null
  importText.value = ''
  importGroupId.value = null
  importModal.value.style.display = 'block'
  importModal.value.classList.add('show')
}

onMounted(() => {
  // 首屏仅加载第一页联系人 + 分组清单
  currentPage.value = 1
  loadRecipients()
  loadGroups()
})
</script>

<style scoped>
.recipient-manage {
  padding: 20px;
}

.page-title {
  color: #2c3e50;
  font-weight: 600;
  margin: 0;
}

.header-actions .btn {
  border-radius: 6px;
  font-weight: 500;
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 10;
}

.groups-container {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.group-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  min-width: 180px;
  cursor: pointer;
  transition: all 0.2s;
}

.group-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.1);
}

.group-card.active {
  border-color: #007bff;
  background: #f8f9ff;
}

.group-info {
  margin-bottom: 10px;
}

.group-name {
  margin: 0 0 5px 0;
  font-weight: 600;
  color: #2c3e50;
}

.group-count {
  color: #6c757d;
  font-size: 0.9em;
}

.group-actions {
  display: flex;
  gap: 5px;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9em;
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

.btn {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.modal {
  background: rgba(0,0,0,0.5);
}

.results-info {
  font-size: 0.9em;
}

.section-title {
  color: #2c3e50;
  font-weight: 600;
  margin: 0;
}

@media (max-width: 768px) {
  .recipient-manage {
    padding: 15px;
  }
  
  .header-section .d-flex {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-section .row > div {
    margin-bottom: 10px;
  }
  
  .groups-container {
    flex-direction: column;
  }
  
  .group-card {
    min-width: auto;
  }
}
</style>
