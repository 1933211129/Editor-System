<template>
  <div class="main-content">
    <h3>📧 邮件管理</h3>
    
    <!-- 子导航栏 -->
    <div class="sub-nav mb-4 d-flex align-items-center justify-content-between">
      <div class="d-flex gap-2">
        <button 
          class="btn" 
          :class="currentView === 'send' ? 'btn-primary active' : 'btn-outline-primary'"
          @click="currentView = 'send'"
        >
          <i class="bi bi-envelope-paper"></i> 批量发送
        </button>
        <button 
          class="btn" 
          :class="currentView === 'template' ? 'btn-primary active' : 'btn-outline-primary'"
          @click="currentView = 'template'"
        >
          <i class="bi bi-file-text"></i> 模板管理
        </button>
        <button 
          class="btn" 
          :class="currentView === 'mailmerge' ? 'btn-primary active' : 'btn-outline-primary'"
          @click="currentView = 'mailmerge'"
        >
          <i class="bi bi-table"></i> 数据驱动模板
        </button>
        <button 
          class="btn" 
          :class="currentView === 'history' ? 'btn-primary active' : 'btn-outline-primary'"
          @click="currentView = 'history'"
        >
          <i class="bi bi-clock-history"></i> 历史记录
        </button>
        <button 
          class="btn" 
          :class="currentView === 'recipients' ? 'btn-primary active' : 'btn-outline-primary'"
          @click="currentView = 'recipients'"
        >
          <i class="bi bi-people"></i> 收件人管理
        </button>
      </div>
      <div class="d-flex align-items-center gap-2">
        <button class="btn btn-outline-secondary" @click="refreshCurrent">
          <i class="bi bi-arrow-clockwise"></i> 刷新本页
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-area">
      <!-- 批量发送视图 -->
      <div v-if="currentView === 'send'">
        <!-- 生成发送框的控制区 -->
        <div class="control-section mb-4">
          <div class="input-group" style="width: 300px;">
            <input 
              type="number" 
              class="form-control" 
              v-model="recipientCount" 
              placeholder="输入收件人数量"
              min="1"
              max="50"
            >
            <button 
              class="btn btn-primary" 
              @click="generateSendBoxes"
            >
              生成发送框
            </button>
          </div>
          
          <!-- 默认主题/全局模板应用 + 通用附件（右侧） -->
          <div class="d-flex align-items-center justify-content-between gap-3 mt-3 flex-wrap">
            <div class="d-flex align-items-center gap-3 flex-wrap">
              <div class="d-flex align-items-center gap-2">
                <div class="form-floating" style="min-width: 300px;">
                  <input type="text" class="form-control" id="defaultSubject" v-model="defaultSubject" placeholder="默认主题">
                  <label for="defaultSubject">默认主题（可一键应用到所有行）</label>
                </div>
                <button class="btn btn-outline-secondary" @click="applyDefaultSubject">
                  应用到所有行
                </button>
              </div>
              <div class="d-flex align-items-center gap-2">
                <div class="form-floating" style="min-width: 300px;">
                  <select class="form-select" id="globalTemplate" v-model="globalTemplateId">
                    <option value="">选择模板（应用到所有行）</option>
                    <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">{{ tpl.title }}</option>
                  </select>
                  <label for="globalTemplate">全局模板</label>
                </div>
                <button class="btn btn-outline-secondary" :disabled="!globalTemplateId" @click="applyTemplateToAll">应用模板到所有行</button>
              </div>
            </div>
            <div class="d-flex align-items-center gap-2 flex-grow-1" style="min-width: 380px;">
              <div class="text-muted">通用附件：</div>
              <input type="file" multiple @change="handleCommonUpload" class="file-input" ref="commonFileInput">
              <button class="btn btn-sm btn-outline-secondary" @click="() => commonFileInput.click()">上传</button>
              <button class="btn btn-sm btn-outline-danger" v-if="commonAttachmentNames.length" @click="commonAttachmentNames = []">清空</button>
              <div class="flex-grow-1 overflow-auto" style="max-height: 64px;">
                <draggable 
                  v-model="commonAttachmentNames" 
                  :group="{ name: 'common-attachments', pull: false, put: false }" 
                  class="file-badges"
                  :animation="150"
                  ghost-class="drag-ghost"
                  chosen-class="drag-chosen"
                  :force-fallback="true"
                  handle=".file-item"
                >
                  <template #item="{ element }">
                    <span class="file-item draggable" title="拖拽可分配至各行">{{ element }}</span>
                  </template>
                </draggable>
              </div>
            </div>
          </div>
        </div>

        <!-- 批量发送区域（合并为按行排列：姓名、邮箱、模板、主题、附件） -->
        <div class="send-section">
          <div class="d-flex align-items-center gap-2">
            <h5 class="mb-0 me-2">发送列表</h5>
            <div class="d-flex align-items-center gap-2">
              <button 
                class="btn btn-sm btn-outline-primary" 
                @click="showBatchRecipientDialog"
                v-if="recipients.length > 0"
              >
                <i class="bi bi-people"></i> 批量添加
              </button>
              <button 
                class="btn btn-sm btn-outline-secondary" 
                @click="showImportGroupDialog"
                v-if="recipients.length >= 0"
              >
                <i class="bi bi-folder-plus"></i> 导入分组
              </button>
              <button 
                class="btn btn-sm btn-outline-primary" 
                @click="triggerBatchUpload"
                v-if="recipients.length > 0"
              >
                <i class="bi bi-upload"></i> 批量添加附件
              </button>
              <input
                type="file"
                ref="batchFileInput"
                @change="handleBatchUpload"
                multiple
                class="d-none"
              >
            </div>
          </div>

          <div class="rows-table mt-3">
            <div class="rt-row header">
              <div class="cell col-name">姓名</div>
              <div class="cell col-email">邮箱</div>
              <div class="cell col-template">模板</div>
              <div class="cell col-subject">主题</div>
              <div class="cell col-attachments">附件</div>
              <div class="cell col-actions">操作</div>
            </div>
            <draggable v-model="recipients" item-key="id" class="body">
              <template #item="{ element, index }">
                <div class="rt-row body-row">
                  <div class="cell col-name">
                    <div class="fixed-number">{{ index + 1 }}</div>
                    <input type="text" class="form-control form-control-sm" v-model="element.name" placeholder="姓名">
                  </div>
                  <div class="cell col-email">
                    <input type="email" class="form-control form-control-sm" v-model="element.email" placeholder="name@example.com">
                  </div>
                  <div class="cell col-template">
                    <select class="form-select form-select-sm" v-model="element.templateId">
                      <option value="">选择模板</option>
                      <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">{{ tpl.title }}</option>
                    </select>
                  </div>
                  <div class="cell col-subject">
                    <input type="text" class="form-control form-control-sm" v-model="element.subject" placeholder="单独主题（可留空）">
                  </div>
                  <div class="cell col-attachments">
                    <div class="d-flex align-items-start gap-2 flex-wrap">
                      <draggable 
                        v-model="element.attachmentNames" 
                        :group="{ name: 'row-attachments', pull: true, put: (to, from) => from && from.options && from.options.group && from.options.group.name === 'row-attachments' }" 
                        class="file-badges flex-grow-1"
                        :animation="150"
                        ghost-class="drag-ghost"
                        chosen-class="drag-chosen"
                        :force-fallback="true"
                        handle=".file-item"
                        :data-row-id="element.id"
                        @add="onRowAttachAdd"
                      >
                        <template #item="{ element: fname }">
                          <span class="file-item draggable" title="拖拽可排序/分配">{{ fname }}</span>
                        </template>
                      </draggable>
                    </div>
                  </div>
                  <div class="cell col-actions">
                    <input type="file" :id="'row-file-' + element.id" multiple @change="(e) => handleSingleUpload(e, element.id)" class="file-input">
                    <button class="btn btn-sm btn-outline-secondary" @click="() => singleFileClick(element.id)">上传</button>
                    <button class="btn btn-sm btn-outline-danger" v-if="element.attachmentNames.length" @click="clearAttachments(element.id)">清空</button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteGroup(index)"><i class="bi bi-trash"></i></button>
                  </div>
                </div>
              </template>
            </draggable>
          </div>

          <div class="action-buttons mt-4">
            <button class="btn btn-outline-primary me-3" @click="addNewGroup">
              <i class="bi bi-plus-circle"></i> 新增一组
            </button>
            <button class="btn btn-success" @click="sendEmails" :disabled="!canSend">
              <i class="bi bi-send"></i> 发送邮件
            </button>
          </div>
        </div>
      </div>

      <!-- 模板管理视图 -->
      <div v-if="currentView === 'template'">
        <template-manage ref="templateRef" />
      </div>

      <!-- 数据驱动模板（XLSX 映射预览） -->
      <div v-if="currentView === 'mailmerge'">
        <EmailMailMerge ref="mailMergeRef" />
      </div>

      <!-- 历史记录视图 -->
      <div v-if="currentView === 'history'">
        <HistoryRecord ref="historyRef" />
      </div>

      <!-- 收件人管理视图 -->
      <div v-if="currentView === 'recipients'">
        <RecipientManage ref="recipientsRef" />
      </div>
    </div>

    <!-- 发送进度对话框 -->
    <div class="modal send-modal" tabindex="-1" ref="sendModal">
      <div class="modal-dialog modal-xl send-modal-dialog">
        <div class="modal-content send-modal-content">
          <div class="modal-header">
            <h5 class="modal-title">发送进度</h5>
            <button type="button" class="btn-close" @click="closeSendModal" :disabled="sendingInProgress"></button>
          </div>
          <div class="modal-body send-modal-body">
            <div v-if="sendingInProgress" class="d-flex align-items-center gap-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <div>
                <div class="fw-bold">正在发送，请稍候…</div>
                <div class="text-muted small">收件人数量：{{ sendProgress.total }}</div>
              </div>
            </div>
            <div v-else>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                  <span class="badge bg-success me-2">成功 {{ summary.ok }}</span>
                  <span class="badge bg-danger">失败 {{ summary.fail }}</span>
                </div>
                <div class="text-muted small" v-if="cleanupInfo">
                  临时文件清理：删除 {{ cleanupInfo.removed }} 个，失败 {{ cleanupInfo.failed }} 个
                </div>
              </div>
              <div class="table-responsive" style="max-height: 50vh;">
                <table class="table table-sm align-middle">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>收件人邮箱</th>
                      <th>发送结果</th>
                      <th>附件状态</th>
                      <th>错误信息</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in sendResults" :key="idx">
                      <td>{{ idx + 1 }}</td>
                      <td>{{ row.recipient }}</td>
                      <td>
                        <span :class="row.success ? 'text-success' : 'text-danger'">{{ row.success ? '成功' : '失败' }}</span>
                      </td>
                      <td>
                        <div class="d-flex flex-wrap gap-2">
                          <span v-for="(att, i) in (row.attachments || [])" :key="i" class="badge" :class="att.attached ? 'bg-success' : 'bg-warning text-dark'" :title="att.error || ''">
                            {{ att.name }} {{ att.attached ? '✓' : '×' }}
                          </span>
                        </div>
                      </td>
                      <td class="small text-muted">{{ row.error || '' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeSendModal" :disabled="sendingInProgress">关闭</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加批量导入对话框 -->
    <div class="modal" tabindex="-1" ref="recipientModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">批量添加收件人</h5>
            <button type="button" class="btn-close" @click="hideBatchRecipientDialog"></button>
          </div>
          <div class="modal-body">
            <div class="form-floating">
              <textarea 
                class="form-control" 
                placeholder="请输入收件人邮箱" 
                v-model="batchRecipients"
                style="height: 150px"
              ></textarea>
              <label>请用分号间隔多个收件人</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideBatchRecipientDialog">取消</button>
            <button type="button" class="btn btn-primary" @click="processBatchRecipients">确定</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 导入分组对话框 -->
    <div class="modal" tabindex="-1" ref="groupImportModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">从分组导入收件人</h5>
            <button type="button" class="btn-close" @click="hideImportGroupDialog"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">选择分组</label>
              <select class="form-select" v-model="selectedImportGroup">
                <option value="">请选择</option>
                <option v-for="g in groups" :key="g.name" :value="g.name">{{ g.name }} ({{ g.count || 0 }})</option>
              </select>
            </div>
            <div class="form-text">将把该分组下的联系人（姓名+邮箱）追加到当前列表。</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideImportGroupDialog">取消</button>
            <button type="button" class="btn btn-primary" :disabled="!selectedImportGroup" @click="importFromGroup">导入</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import draggable from 'vuedraggable'
import TemplateManage from './email/TemplateManage.vue'
import HistoryRecord from './email/HistoryRecord.vue'
import RecipientManage from './email/RecipientManage.vue'
import EmailMailMerge from './email/MailMerge.vue'
import axios from 'axios'

// 当前视图
const currentView = ref('send')

// 子页引用，用于触发各自的 refresh()
const templateRef = ref(null)
const mailMergeRef = ref(null)
const historyRef = ref(null)
const recipientsRef = ref(null)

// 发送进度与结果
const sendModal = ref(null)
const sendingInProgress = ref(false)
const sendResults = ref([])
const summary = ref({ ok: 0, fail: 0 })
const cleanupInfo = ref(null)
const sendProgress = ref({ total: 0 })

// 收件人数量
const recipientCount = ref('')

// 收件人列表（统一数据结构：包含姓名、邮箱、模板、主题、附件名列表）
const recipients = ref([])

// 模板与分组
const templates = ref([])
const groups = ref([])

// 文件上传引用
const batchFileInput = ref(null)
const commonFileInput = ref(null)

// 批量收件人文本
const batchRecipients = ref('')
const recipientModal = ref(null)

// 生成发送框
const generateSendBoxes = () => {
  const count = parseInt(recipientCount.value)
  if (count > 0) {
    const base = Date.now()
    recipients.value = Array(count).fill(null).map((_, index) => ({
      id: base + index,
      name: '',
      email: '',
      templateId: '',
      subject: '',
      attachmentNames: []
    }))
  }

}


// 添加新增一组的方法
const addNewGroup = () => {
  const newId = Date.now()
  recipients.value.push({
    id: newId,
    name: '',
    email: '',
    templateId: '',
    subject: '',
    attachmentNames: []
  })
}

// 通用附件与单个/批量上传逻辑
const defaultSubject = ref('')
const commonAttachmentNames = ref([])
const globalTemplateId = ref('')


// 上传文件到服务器，返回保存后的文件名数组
const uploadFiles = async (files) => {
  const fd = new FormData()
  files.forEach(f => fd.append('files', f))
  const res = await fetch('/api/email/upload/', { method: 'POST', body: fd })
  const data = await res.json()
  if (!res.ok || data.status !== 'success') throw new Error(data.message || '上传失败')
  return (data.files || []).map(f => f.name)
}

// 单行上传（每行仅保留一个附件：新上传覆盖旧的）
const handleSingleUpload = async (event, id) => {
  const files = Array.from(event.target.files)
  if (!files.length) return
  try {
    const names = await uploadFiles(files)
    const r = recipients.value.find(a => a.id === id)
    if (r) r.attachmentNames = names.length ? [names[0]] : []
  } catch (e) {
    alert('上传失败：' + e.message)
  } finally {
    event.target.value = ''
  }
}

// 通用上传
const handleCommonUpload = async (event) => {
  const files = Array.from(event.target.files)
  if (!files.length) return
  try {
    const names = await uploadFiles(files)
    commonAttachmentNames.value.push(...names)
  } catch (e) {
    alert('上传失败：' + e.message)
  } finally {
    event.target.value = ''
  }
}

// 触发单行 input 点击（通过 ref 列表简化，这里用原生点击）
const singleFileClick = (id) => {
  // 查找该行下的第一个 file input 并触发
  const el = document.querySelector(`#row-file-${id}`) || null
  if (el) el.click()
}

// 判断是否可以发送
const canSend = computed(() => {
  if (!recipients.value.length) return false
  const baseOk = recipients.value.every(r => r.email && r.templateId)
  if (!baseOk) return false
  // 主题：允许默认主题或逐行主题至少满足一种
  const hasDefault = !!defaultSubject.value.trim()
  const allRowSubject = recipients.value.every(r => (r.subject || '').trim())
  return hasDefault || allRowSubject
})

// 应用全局模板到所有行
const applyTemplateToAll = () => {
  if (!globalTemplateId.value) return
  recipients.value.forEach(r => { r.templateId = globalTemplateId.value })
}

// 发送邮件
const sendEmails = async () => {
  try {
    // 发送前强制刷新模板，确保使用最新内容
    await loadTemplates()
    if (!recipients.value.length) {
      alert('请先添加收件人')
      return
    }

    // 要求所有行选择相同模板（正文按单模板获取）
    const chosenTemplateIds = Array.from(new Set(recipients.value.map(r => r.templateId).filter(Boolean)))
    if (chosenTemplateIds.length !== 1) {
      alert('请确保所有收件人选择相同的邮件模板')
      return
    }
    const tplId = chosenTemplateIds[0]

    // 获取模板内容（上面已刷新，这里直接读取）
    const tpl = templates.value.find(t => String(t.id) === String(tplId))
    if (!tpl) {
      alert('未找到所选模板内容，请重试')
      return
    }
    const html_body = tpl.content || ''

    // 构建主题数组
    const default_subject = defaultSubject.value || ''
    const subjects = recipients.value.map(r => (r.subject || ''))

    const receiver_emails = recipients.value.map(r => (r.email || '').trim()).filter(Boolean)
    if (!receiver_emails.length) {
      alert('请填写有效的收件人邮箱')
      return
    }

    // 按文件名映射
    const unique_attachment_names = recipients.value.map(r => r.attachmentNames || [])
    const common_attachment_names = commonAttachmentNames.value || []

    const payload = {
      default_subject,
      subjects,
      html_body,
      receiver_emails,
      unique_attachment_names,
      common_attachment_names
    }

    // 打开发送进度弹窗
    sendResults.value = []
    cleanupInfo.value = null
    summary.value = { ok: 0, fail: 0 }
    sendingInProgress.value = true
    sendProgress.value = { total: receiver_emails.length }
    showSendModal()

    const resp = await fetch('/api/email/send-bulk/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const result = await resp.json()
    if (resp.ok && result.status === 'success') {
      sendResults.value = result.results || []
      const okCount = sendResults.value.filter(r => r.success).length
      const failCount = (sendResults.value.length - okCount)
      summary.value = { ok: okCount, fail: failCount }
      cleanupInfo.value = result.cleanup || null
    } else {
      sendResults.value = []
      summary.value = { ok: 0, fail: 0 }
      cleanupInfo.value = null
      alert('发送失败：' + (result.message || resp.statusText))
    }
  } catch (e) {
    console.error(e)
    alert('发送过程中发生错误，请稍后再试')
  } finally {
    sendingInProgress.value = false
  }
}

// 刷新当前子页数据（不跳转、不重载父页）
const refreshCurrent = () => {
  if (currentView.value === 'template') {
    templateRef.value && typeof templateRef.value.refresh === 'function' && templateRef.value.refresh()
  } else if (currentView.value === 'mailmerge') {
    mailMergeRef.value && typeof mailMergeRef.value.refresh === 'function' && mailMergeRef.value.refresh()
  } else if (currentView.value === 'history') {
    historyRef.value && typeof historyRef.value.refresh === 'function' && historyRef.value.refresh()
  } else if (currentView.value === 'recipients') {
    recipientsRef.value && typeof recipientsRef.value.refresh === 'function' && recipientsRef.value.refresh()
  } else {
    // send 视图暂不提供刷新逻辑
  }
}

// 触发批量上传文件选择
const triggerBatchUpload = () => {
  batchFileInput.value && batchFileInput.value.click()
}

// 批量上传：数量不能超过收件人数；每行仅分配一个附件，覆盖旧的
const handleBatchUpload = async (event) => {
  const files = Array.from(event.target.files)
  if (!files.length) return
  try {
    const maxCount = recipients.value.length
    const limitedFiles = files.slice(0, maxCount)
    if (files.length > maxCount) {
      alert(`已超出收件人数量，仅分配前 ${maxCount} 个文件。其余文件请到对应行单独上传。`)
    }
    const names = await uploadFiles(limitedFiles)
    const m = Math.min(names.length, maxCount)
    for (let i = 0; i < m; i++) {
      recipients.value[i].attachmentNames = [names[i]]
    }
  } catch (e) {
    alert('上传失败：' + e.message)
  } finally {
    event.target.value = ''
  }
}

// 拖拽到某行附件区时：只保留一个，若目标已有则与来源交换
const onRowAttachAdd = (evt) => {
  try {
    const toId = Number(evt.to.getAttribute('data-row-id'))
    const fromId = Number(evt.from.getAttribute('data-row-id'))
    const toRow = recipients.value.find(r => Number(r.id) === toId)
    const fromRow = recipients.value.find(r => Number(r.id) === fromId)

    if (!toRow) return

    // 目标行仅保留最新放入的那个
    const incoming = toRow.attachmentNames[evt.newIndex]
    const prev = toRow.attachmentNames.find((_, i) => i !== evt.newIndex)
    toRow.attachmentNames = incoming ? [incoming] : []

    // 若来自其他行，则放回被挤出的文件，实现“交换”效果
    if (fromRow && fromRow !== toRow) {
      if (prev) {
        fromRow.attachmentNames = [prev]
      } else {
        fromRow.attachmentNames = []
      }
    }
  } catch (e) {
    console.warn('onRowAttachAdd error:', e)
  }
}

// 添加清空附件的方法
const clearAttachments = (recipientId) => {
  const r = recipients.value.find(a => a.id === recipientId)
  if (r) r.attachmentNames = []
}

// 添加删除组的方法
const deleteGroup = (index) => {
  recipients.value.splice(index, 1)
}

// 应用默认主题到所有行
const applyDefaultSubject = () => {
  recipients.value.forEach(r => { r.subject = defaultSubject.value })
}

// 显示批量添加对话框
const showBatchRecipientDialog = () => {
  recipientModal.value.style.display = 'block'
  recipientModal.value.classList.add('show')
}

// 隐藏批量添加对话框
const hideBatchRecipientDialog = () => {
  recipientModal.value.style.display = 'none'
  recipientModal.value.classList.remove('show')
  batchRecipients.value = ''
}

// 处理批量添加收件人
const processBatchRecipients = () => {
  // 分割收件人列表（支持中文分号和英文分号）
  const emailList = batchRecipients.value.split(/[;；]/).filter(email => email.trim())
  
  if (emailList.length === 0) {
    alert('请输入有效的收件人邮箱')
    return
  }

  // 计算需要新增的发送框数量
  const currentBoxCount = recipients.value.length
  const needNewBoxes = Math.max(0, emailList.length - currentBoxCount)
  
  // 如果需要新增发送框，先创建新的发送框
  if (needNewBoxes > 0) {
    for (let i = 0; i < needNewBoxes; i++) {
      const newId = Date.now() + i
      recipients.value.push({
        id: newId,
        name: '',
        email: '',
        templateId: '',
        subject: '',
        attachmentNames: []
      })
    }
    alert(`因收件人数量超出，已自动新增 ${needNewBoxes} 个发送框`)
  }

  // 填充邮箱地址
  emailList.forEach((email, index) => {
    if (index < recipients.value.length) {
      recipients.value[index].email = email.trim()
    }
  })

  hideBatchRecipientDialog()
}

// 分组导入对话框控制
const groupImportModal = ref(null)
const selectedImportGroup = ref('')
const showImportGroupDialog = async () => {
  await loadGroups()
  groupImportModal.value.style.display = 'block'
  groupImportModal.value.classList.add('show')
}
const hideImportGroupDialog = () => {
  groupImportModal.value.style.display = 'none'
  groupImportModal.value.classList.remove('show')
  selectedImportGroup.value = ''
}
const importFromGroup = async () => {
  if (!selectedImportGroup.value) return
  try {
    const resp = await axios.get('/api/recipients/', { params: { page: 1, page_size: 200, search: '', group_name: selectedImportGroup.value } })
    if (resp.data && resp.data.status === 'success') {
      const list = resp.data.data.recipients || []
      list.forEach(r => {
        recipients.value.push({
          id: Date.now() + Math.floor(Math.random() * 100000),
          name: r.name || '',
          email: r.email || '',
          templateId: '',
          subject: '',
          attachmentNames: []
        })
      })
    } else {
      alert('导入失败：' + (resp.data && resp.data.message ? resp.data.message : '未知错误'))
    }
  } catch (e) {
    console.error(e)
    alert('导入分组失败，请重试')
  } finally {
    hideImportGroupDialog()
  }
}


// 加载模板与分组
const loadTemplates = async () => {
  try {
    const res = await fetch(`/api/email-templates/?_ts=${Date.now()}`, { cache: 'no-store' })
    const data = await res.json()
    if (data.status === 'success') {
      templates.value = data.data || []
    }
  } catch (e) {
    console.error('加载模板失败', e)
  }
}
const loadGroups = async () => {
  try {
    const resp = await axios.get('/api/groups/')
    if (resp.status === 200 && resp.data && resp.data.status === 'success') {
      groups.value = resp.data.data || []
    }
  } catch (e) {
    console.error('加载分组失败', e)
  }
}

onMounted(() => {
  loadTemplates()
})

// 切换回发送视图时，强制刷新模板列表，避免使用旧缓存
watch(currentView, (v) => {
  if (v === 'send') {
    loadTemplates()
  }
})

// 发送进度弹窗控制
const showSendModal = () => {
  if (sendModal.value) {
    sendModal.value.style.display = 'block'
    sendModal.value.classList.add('show')
  }
}
const closeSendModal = () => {
  if (sendingInProgress.value) return
  if (sendModal.value) {
    sendModal.value.style.display = 'none'
    sendModal.value.classList.remove('show')
  }
}

</script>

<style scoped>
.main-content {
  margin-left: 250px;
  padding: 20px;
}

/* 放大发送进度弹窗尺寸（仅限发送进度弹窗） */
.send-modal { /* 使弹窗覆盖整个视口，避免受父容器限制 */
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1055;
  padding: 16px;
  overflow: auto;
}
.send-modal .send-modal-dialog { max-width: 95vw; width: 95vw; margin: 32px auto; }
.send-modal .send-modal-content { height: 90vh; display: flex; flex-direction: column; }
.send-modal .send-modal-body { overflow: auto; }

.sub-nav {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.send-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-top: 20px;
  min-height: 500px;
}

.recipients-column,
.emails-column,
.templates-column,
.subjects-column,
.attachments-column {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 扩大附件列的可视宽度（桌面端占两列） */
.attachments-column {
  grid-column: span 2;
}

.recipients-list,
.templates-list,
.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 15px;
}

.recipient-item,
.template-item,
.attachment-item {
  position: relative;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  margin-bottom: 15px;
  min-height: 80px;
  height: auto;
}

.fixed-number {
  position: absolute;
  left: -10px;
  top: 50%;
  transform: translateY(-50%);
  background: #0d6efd;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  z-index: 1;
}

.file-upload {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #dee2e6;
  border-radius: 4px;
  cursor: pointer;
}

.file-names {
  margin-top: 8px;
  height: 30px;
  overflow-x: auto;
}

.file-item {
  display: inline-block;
  padding: 2px 8px;
  font-size: 0.9em;
  background: #f8f9fa;
  border-radius: 3px;
  margin-right: 8px;
}

.remove-btn {
  border: none;
  background: none;
  color: #dc3545;
  padding: 0 4px;
  cursor: pointer;
  margin-left: 4px;
}

.file-input {
  display: none;
}

.upload-label {
  width: 100%;
  text-align: center;
  cursor: pointer;
  color: #666;
}

.list-container {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 100%;
  min-height: 400px;
}

/* 附件徽章换行显示 */
.file-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.drag-handle {
  cursor: grab;
  user-select: none;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.attachments-column h5 {
  display: flex;
  align-items: center;
}

.clear-all {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #dc3545;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 2;
}

.clear-all:hover {
  background: #bb2d3b;
  transform: translateY(-50%) scale(1.1);
}

.delete-group {
  position: absolute;
  left: -32px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
  color: #dc3545;
  transition: all 0.2s;
}

.delete-group:hover {
  transform: translateY(-50%) scale(1.1);
  color: #bb2d3b;
}

.delete-group i {
  font-size: 20px;
}

/* ====== 新的按行布局样式 ====== */
.rows-table {
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  width: 100%;
}
.rows-table .header {
  display: grid;
  width: 100%;
  grid-template-columns:
    minmax(100px, 1fr)     /* 姓名 */
    minmax(200px, 2fr)     /* 邮箱 */
    minmax(120px, 1.1fr)   /* 模板 */
    minmax(160px, 1.5fr)   /* 主题 */
    minmax(220px, 2fr)     /* 附件（稍宽）*/
    minmax(120px, 0.9fr);  /* 操作 */
  gap: 10px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-weight: 600;
  color: #555;
}
.rows-table .body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}
.rows-table .body-row {
  display: grid;
  width: 100%;
  grid-template-columns:
    minmax(100px, 1fr)
    minmax(200px, 2fr)
    minmax(120px, 1.1fr)
    minmax(160px, 1.5fr)
    minmax(220px, 2fr)
    minmax(120px, 0.9fr);
  gap: 10px;
  padding: 10px 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}
.rows-table .cell {
  display: flex;
  align-items: center;
}
.rows-table .col-name { align-items: center; gap: 6px; }
.rows-table .col-name .fixed-number {
  position: static;
  transform: none;
  width: 20px;
  height: 20px;
  font-size: 12px;
}
.rows-table .col-attachments { align-items: flex-start; }
.rows-table .col-actions { gap: 6px; justify-content: flex-end; }

/* 输入控件尺寸优化 */
.rows-table input.form-control-sm,
.rows-table select.form-select-sm {
  height: 32px;
  padding: 4px 8px;
}

/* 响应式：窄屏改为更紧凑布局 */
@media (max-width: 1200px) {
  .rows-table .header,
  .rows-table .body-row {
    grid-template-columns:
      minmax(90px, 1fr)
      minmax(160px, 1.6fr)
      minmax(110px, 1fr)
      minmax(140px, 1.3fr)
      minmax(200px, 1.8fr)
      minmax(110px, 0.8fr);
  }
}
@media (max-width: 768px) {
  .rows-table .header { display: none; }
  .rows-table .body-row {
    grid-template-columns: 1fr;
  }
  .rows-table .cell { align-items: stretch; }
  .rows-table .col-actions { justify-content: flex-start; }
}

/* 拖拽视觉提示 */
.drag-ghost {
  opacity: 0.6 !important;
  background: #e7f1ff !important;
}
.drag-chosen {
  outline: 2px dashed #0d6efd;
  background: #f0f7ff;
}
.file-item.draggable {
  cursor: grab;
}
.file-item.draggable:active {
  cursor: grabbing;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
  
  .send-grid {
    grid-template-columns: 1fr;
  }
}

/* 添加模态框样式 */
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

.modal-dialog {
  margin: 1.75rem auto;
  max-width: 500px;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

</style> 
 