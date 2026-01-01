<template>
  <div class="container py-4 email-mail-merge">
    <!-- Header -->
    <div class="mm-header rounded-3 p-3 p-md-4 mb-4 d-flex align-items-center justify-content-between">
      <div class="d-flex align-items-center">
        <!-- <img src="/logo.jpg" class="me-3 mm-logo" alt="logo" /> -->
        <div>
          <h3 class="m-0 fw-semibold">数据驱动邮件模板</h3>
          <div class="text-muted small">上传 XLSX → 字段映射 → 模板渲染预览</div>
        </div>
      </div>
      <div class="d-none d-md-flex align-items-center gap-2">
        <button class="btn btn-sm btn-outline-secondary" @click="refresh()"><i class="bi bi-arrow-repeat"></i> 重置</button>
        <button class="btn btn-sm btn-primary" @click="goto(Math.min(4, step+1))"><i class="bi bi-skip-forward"></i> 下一步</button>
      </div>
    </div>

    <!-- Stepper -->
    <div class="stepper rounded-3 p-3 mb-4 d-flex justify-content-between align-items-center">
      <div class="step" :class="{active: step>=1}">
        <div class="bullet">1</div>
        <div class="label">选择模板</div>
      </div>
      <div class="sep"></div>
      <div class="step" :class="{active: step>=2}">
        <div class="bullet">2</div>
        <div class="label">上传数据</div>
      </div>
      <div class="sep"></div>
      <div class="step" :class="{active: step>=3}">
        <div class="bullet">3</div>
        <div class="label">字段映射</div>
      </div>
      <div class="sep"></div>
      <div class="step" :class="{active: step>=4}">
        <div class="bullet">4</div>
        <div class="label">预览与校验</div>
      </div>
    </div>

    <!-- Card: Template -->
    <div class="card shadow-sm mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="card-title mb-0">1) 选择模板</h5>
          <button class="btn btn-sm btn-outline-primary" @click="useSampleTpl">使用示例模板</button>
        </div>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label fw-semibold">邮件主题模板</label>
            <input v-model="subjectTpl" type="text" class="form-control form-control-lg" placeholder="如：审稿费通知 - {{teacher_name}} 老师" />
          </div>
          <div class="col-md-6">
            <label class="form-label fw-semibold">邮件正文模板</label>
            <div class="rte-toolbar card mb-2 p-2 py-2">
              <div class="d-flex align-items-center flex-wrap gap-2">
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="applyBold"><i class="bi bi-type-bold"></i></button>
                <button type="button" class="btn btn-sm btn-outline-danger" @click="applyRed"><i class="bi bi-palette"></i></button>
                <span class="ms-2 text-muted small">支持粘贴文本、选择后设置样式</span>
              </div>
            </div>
            <div ref="editorRef"
                 class="rte form-control"
                 contenteditable="true"
                 :data-placeholder="editorPlaceholder"
                 @input="onEditorInput"
                 @paste.prevent="onEditorPaste">
            </div>
            <div class="form-text" v-pre>占位符：{{name}}；过滤器：{{amount|currency}}、{{date|date:%Y-%m-%d}}</div>
          </div>
        </div>
        <div class="text-end mt-3">
          <button class="btn btn-primary btn-lg" @click="goto(2)">下一步：上传数据</button>
        </div>
      </div>
    </div>

    <!-- Card: Upload -->
    <div class="card shadow-sm mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="card-title mb-0">2) 上传 XLSX 数据</h5>
          <a class="btn btn-sm btn-outline-secondary" :href="sampleLink" download>下载示例数据</a>
        </div>
        <div class="row g-3 align-items-center">
          <div class="col-12 col-lg-7">
            <div class="dropzone" @click="onBrowse">
              <div class="d-flex flex-column align-items-center justify-content-center gap-2">
                <i class="bi bi-cloud-arrow-up fs-3 text-primary"></i>
                <div class="text-muted"> <span class="text-primary text-decoration-underline">点击选择</span></div>
                <div class="small text-muted">支持 .xlsx / .xls</div>
              </div>
              <input ref="fileInputRef" class="visually-hidden" type="file" accept=".xlsx,.xls" @change="onFileChange" />
            </div>
          </div>
          <div class="col-12 col-lg-5">
            <div class="d-flex align-items-center flex-wrap gap-2">
              <span v-if="columns.length" class="badge bg-light text-dark">检测到 {{ columns.length }} 列</span>
              <span v-if="rowCount>0" class="badge bg-success">共 {{ rowCount }} 行</span>
              <span v-if="loadError" class="badge bg-danger">{{ loadError }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Card: Mapping -->
    <div class="card shadow-sm mb-3" v-if="columns.length">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="card-title mb-0">3) 字段映射</h5>
          <div>
            <button class="btn btn-sm btn-outline-primary me-2" @click="autoMap">智能匹配</button>
            <button class="btn btn-sm btn-outline-secondary" @click="clearMap">清空映射</button>
          </div>
        </div>
        <div class="row g-3 align-items-center mb-2">
          <div class="col-auto">
            <label class="col-form-label">收件人邮箱列</label>
          </div>
          <div class="col-auto">
            <select v-model="emailColumn" class="form-select">
              <option value="">请选择</option>
              <option v-for="c in columns" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="col-auto">
            <span :class="['badge', emailColumn? 'bg-success':'bg-secondary']">{{ emailColumn? '已选择' : '未选择' }}</span>
          </div>
        </div>

        <div class="table-responsive mm-table-wrap">
          <table class="table table-sm align-middle mb-0 mm-table">
            <thead>
              <tr>
                <th style="width:280px">模板变量</th>
                <th>映射到列</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="v in variables" :key="v.raw">
                <td><code class="text-primary">{{ displayVar(v) }}</code></td>
                <td>
                  <select v-model="fieldMap[v.name]" class="form-select">
                    <option value="">(未映射)</option>
                    <option v-for="c in columns" :key="c" :value="c">{{ c }}</option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="text-end">
          <button class="btn btn-primary btn-lg" @click="goto(4)">下一步：预览与校验</button>
        </div>
      </div>
    </div>

    <!-- Card: Preview -->
    <div class="card shadow-sm" v-if="previewRows.length">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="card-title mb-0">4) 预览与校验</h5>
          <div class="small text-muted">变量映射完成度：{{ mappedCount }}/{{ variables.length }}</div>
        </div>

        <div class="row g-3">
          <div class="col-md-6" v-for="(row, idx) in previewRows" :key="idx">
            <div class="border rounded p-3 bg-light h-100 mm-preview-item">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="fw-semibold">样本 #{{ (currentPage - 1) * pageSize + idx + 1 }}</div>
                <span class="badge" :class="resolveEmail(row)? 'bg-success':'bg-secondary'">{{ resolveEmail(row) || '未映射邮箱' }}</span>
              </div>
              <div class="mb-1"><span class="text-muted">主题：</span><span class="fw-semibold">{{ renderTemplate(subjectTpl, row) }}</span></div>
              <div class="text-muted">正文：</div>
              <div class="border bg-white rounded p-2 mb-0" style="min-height: 100px;" v-html="renderTemplate(bodyTpl, row)"></div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="d-flex justify-content-between align-items-center mt-2">
          <div class="small text-muted">共 {{ totalItems }} 条，{{ totalPages }} 页；当前第 {{ currentPage }} 页</div>
          <div class="btn-group btn-group-sm" role="group">
            <button class="btn btn-outline-secondary" :disabled="currentPage===1" @click="currentPage=1">首页</button>
            <button class="btn btn-outline-secondary" :disabled="currentPage===1" @click="currentPage--">上一页</button>
            <button class="btn btn-outline-secondary" :disabled="currentPage===totalPages || totalPages===0" @click="currentPage++">下一页</button>
            <button class="btn btn-outline-secondary" :disabled="currentPage===totalPages || totalPages===0" @click="currentPage=totalPages">末页</button>
          </div>
        </div>

        <hr />
        <div>
          <div class="fw-semibold mb-2">校验</div>
          <ul class="list-unstyled small">
            <li>
              <span class="me-2">邮箱列：</span>
              <span :class="['badge', emailColumn? 'bg-success':'bg-danger']">{{ emailColumn? '已选择' : '未选择' }}</span>
            </li>
            <li>
              <span class="me-2">映射变量：</span>
              <span class="badge bg-info">{{ mappedCount }}/{{ variables.length }}</span>
            </li>
          </ul>
        </div>

        <!-- Send Actions -->
        <div class="mt-3">
          <div class="d-flex flex-wrap align-items-center justify-content-between gap-2">
            <div class="small text-muted">
              可发送：<span class="fw-semibold">{{ sendableCount }}</span> 封
            </div>
            <div class="d-flex align-items-center gap-2">
              <button class="btn btn-success" :disabled="!canSend || isSending" @click="startSend">
                <i class="bi bi-send"></i>
                {{ isSending ? '发送中…' : '发送邮件' }}
              </button>
              <button class="btn btn-outline-secondary" :disabled="!isSending" @click="abortSend">中止</button>
            </div>
          </div>

          <!-- Progress -->
          <div class="mt-3" v-if="isSending || sentCount>0">
            <div class="d-flex justify-content-between small mb-1">
              <span>进度：{{ sentCount }}/{{ totalToSend }}</span>
              <span>{{ progressPercent }}%</span>
            </div>
            <div class="progress" style="height: 10px;">
              <div class="progress-bar" role="progressbar" :style="{width: progressPercent + '%'}" :aria-valuenow="progressPercent" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
          </div>

          <!-- Results -->
          <div class="mt-3" v-if="sendResults.length">
            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th style="width: 40%">收件人</th>
                    <th style="width: 15%">状态</th>
                    <th>错误</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(r, i) in sendResults" :key="i">
                    <td><code>{{ r.recipient }}</code></td>
                    <td>
                      <span class="badge" :class="r.success ? 'bg-success' : 'bg-danger'">{{ r.success ? '成功' : '失败' }}</span>
                    </td>
                    <td class="text-muted small">{{ r.error }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
/* global defineExpose */
import { ref, computed, onMounted, watch } from 'vue'
import * as XLSX from 'xlsx'

const step = ref(1)
function goto(s) { step.value = s }

const subjectTpl = ref('审稿费通知 - {{teacher_name}} 老师')
const bodyTpl = ref(`{{teacher_name}} 老师，您好！\n您共审稿 {{paper_count}} 篇，应发放审稿费 {{amount|currency}} 元。\n谢谢！`)
const editorRef = ref(null)
let isUserTyping = false
const editorPlaceholder = '在此输入正文模板，支持 {{变量}} 与简单样式（加粗/标红）'

onMounted(() => {
  // 确保编辑器初始 HTML 与 bodyTpl 一致
  if (editorRef.value) editorRef.value.innerHTML = toHtml(bodyTpl.value)
})

const workbookData = ref([])
const columns = ref([])
const rowCount = computed(() => workbookData.value.length)
const loadError = ref('')

const emailColumn = ref('')
const fieldMap = ref({})

const sampleLink = ref('')
const fileInputRef = ref(null)

function onBrowse () {
  if (fileInputRef.value) fileInputRef.value.click()
}

function onEditorInput () {
  isUserTyping = true
  bodyTpl.value = editorRef.value?.innerHTML || ''
  Promise.resolve().then(() => { isUserTyping = false })
}

watch(bodyTpl, (val) => {
  if (isUserTyping) return
  if (editorRef.value && editorRef.value.innerHTML !== toHtml(val)) {
    editorRef.value.innerHTML = toHtml(val)
  }
})

function onEditorPaste (evt) {
  const text = (evt.clipboardData || window.clipboardData).getData('text')
  document.execCommand && document.execCommand('insertText', false, text)
}

function applyBold () {
  if (document.execCommand) {
    document.execCommand('bold', false)
    onEditorInput()
    return
  }
}

function applyRed () {
  if (document.execCommand) {
    document.execCommand('foreColor', false, '#d14343')
    onEditorInput()
    return
  }
}

// 工具：将文本中的换行转换为 <br>，保持占位符原样
function toHtml (text) {
  return (text || '').replace(/\n/g, '<br>')
}
// 工具：清理编辑器产生的多余标签，转义不必要的样式
// function normalizeHtml (html) {
//   // 简单归一化：去除多余的 span style="color: rgb(0, 0, 0)" 等冗余
//   return (html || '')
//     .replace(/ style=""/g, '')
// }
// 构造一个简单的 CSV 下载示例（前端生成 Blob）
createSample()
function createSample() {
  const rows = [
    ['email', 'teacher_name', 'paper_count', 'amount', 'pay_date'],
    ['a@example.com', '张三', 2, 600, '2025-08-20'],
    ['b@example.com', '李四', 3, 900, '2025-08-21']
  ]
  const csv = rows.map(r => r.map(v => typeof v === 'string' && v.includes(',') ? `"${v}"` : v).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  sampleLink.value = URL.createObjectURL(blob)
}

// 解析模板变量
const variables = computed(() => {
  const set = new Map()
  const regex = /{{\s*([a-zA-Z0-9_]+)(\|[^}]+)?\s*}}/g
  const both = `${subjectTpl.value}\n${bodyTpl.value}`
  let m
  while ((m = regex.exec(both)) !== null) {
    const name = m[1]
    const filt = (m[2] || '').trim()
    const raw = m[0]
    const key = `${name}|${filt}`
    if (!set.has(key)) set.set(key, { name, filter: filt, raw })
  }
  return Array.from(set.values())
})

const mappedCount = computed(() => variables.value.filter(v => !!fieldMap.value[v.name]).length)

// Pagination state for preview
const pageSize = 6
const currentPage = ref(1)
const totalItems = computed(() => workbookData.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize))
const previewRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return workbookData.value.slice(start, start + pageSize)
})

// 发送状态与进度
const isSending = ref(false)
const abortFlag = ref(false)
const sentCount = ref(0)
const totalToSend = ref(0)
const sendResults = ref([])
const sendableCount = computed(() => workbookData.value.filter(r => !!resolveEmail(r)).length)
const canSend = computed(() => !!emailColumn.value && sendableCount.value > 0 && mappedCount.value > 0)
const progressPercent = computed(() => totalToSend.value ? Math.round(sentCount.value / totalToSend.value * 100) : 0)

function useSampleTpl() {
  subjectTpl.value = '审稿费通知 - {{teacher_name}} 老师'
  bodyTpl.value = `{{teacher_name}} 老师，您好！\n您共审稿 {{paper_count}} 篇，应发放审稿费 {{amount|currency}} 元。\n发放日期：{{pay_date|date:%Y-%m-%d}}\n谢谢！`
}

function onFileChange (e) {
  loadError.value = ''
  const f = e.target.files?.[0]
  if (!f) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    try {
      const data = new Uint8Array(evt.target.result)
      const wb = XLSX.read(data, { type: 'array' })
      const sheetName = wb.SheetNames[0]
      const sheet = wb.Sheets[sheetName]
      const json = XLSX.utils.sheet_to_json(sheet, { defval: '' })
      workbookData.value = json
      columns.value = Object.keys(json[0] || {})
      // 重置映射
      emailColumn.value = guessEmailColumn(columns.value)
      fieldMap.value = autoMapFields(columns.value)
      currentPage.value = 1
      step.value = Math.max(step.value, 3)
    } catch (err) {
      console.error(err)
      loadError.value = '解析失败：' + err.message
    }
  }
  reader.readAsArrayBuffer(f)
}

function guessEmailColumn(cols) {
  const lower = cols.map(c => c.toLowerCase())
  const idx = lower.findIndex(c => ['email','邮箱','mail','e-mail'].includes(c))
  return idx >= 0 ? cols[idx] : ''
}

function autoMapFields(cols) {
  const map = {}
  const lower = cols.map(c => c.toLowerCase())
  const prefer = (names) => {
    for (const n of names) {
      const i = lower.indexOf(n)
      if (i >= 0) return cols[i]
    }
    return ''
  }
  const varNames = variables.value.map(v => v.name)
  for (const v of varNames) {
    map[v] = prefer([v, v.replace(/_/g, ''), v.replace(/_/g, ' '),
      v === 'amount' ? '金额' : v,
      v === 'teacher_name' ? '姓名' : v,
      v === 'paper_count' ? '篇数' : v]) || ''
  }
  return map
}

function autoMap() {
  fieldMap.value = autoMapFields(columns.value)
}
function clearMap() { fieldMap.value = {}; emailColumn.value = '' }

function resolveEmail (row) {
  if (!emailColumn.value) return ''
  return (row[emailColumn.value] || '').toString().trim()
}

function applyFilter (val, filterStr) {
  if (!filterStr) return val
  const f = filterStr.replace(/^\|/, '')
  if (f === 'currency') {
    const num = Number(val)
    if (isNaN(num)) return val
    return num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
  if (f.startsWith('date:')) {
    const fmt = f.slice('date:'.length)
    const d = new Date(val)
    if (isNaN(d.getTime())) return val
    if (fmt === '%Y-%m-%d') {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const dd = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${dd}`
    }
    return d.toISOString()
  }
  return val
}

function renderTemplate (tpl, row) {
  if (!tpl) return ''
  return tpl.replace(/{{\s*([a-zA-Z0-9_]+)(\|[^}]+)?\s*}}/g, (_, name, filter) => {
    const col = fieldMap.value[name]
    const raw = col ? row[col] : ''
    const val = raw == null ? '' : raw
    return applyFilter(val, filter || '')
  })
}

function displayVar(v) {
  const varPart = `{{${v.name}}}`
  return v.filter ? `${varPart}${v.filter}` : varPart
}

// 刷新：重置步骤与数据（不清空当前模板文案）
function refresh () {
  step.value = 1
  workbookData.value = []
  columns.value = []
  loadError.value = ''
  emailColumn.value = ''
  fieldMap.value = {}
  // 重置预览编辑器显示
  if (editorRef.value) {
    editorRef.value.innerHTML = toHtml(bodyTpl.value)
  }
  // 重置发送状态
  isSending.value = false
  abortFlag.value = false
  sentCount.value = 0
  totalToSend.value = 0
  sendResults.value = []
}
// 向父组件暴露刷新方法
defineExpose({ refresh })

// 开始发送（逐条调用后端以支持模板个性化）
async function startSend () {
  if (!canSend.value || isSending.value) return
  isSending.value = true
  abortFlag.value = false
  sendResults.value = []
  sentCount.value = 0

  const rows = workbookData.value.slice() // 保持当前顺序
  const recipients = rows.map(r => resolveEmail(r)).filter(Boolean)
  totalToSend.value = recipients.length

  for (const row of rows) {
    if (abortFlag.value) break
    const to = resolveEmail(row)
    if (!to) { continue }
    const subject = renderTemplate(subjectTpl.value, row)
    const html = renderTemplate(bodyTpl.value, row)
    const payload = {
      default_subject: subject,
      subjects: [],
      html_body: html,
      receiver_emails: [to],
      unique_attachment_names: [[]],
      common_attachment_names: []
    }
    try {
      const resp = await fetch('/api/email/send-bulk/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await resp.json().catch(() => ({}))
      if (resp.ok && data && data.status === 'success' && Array.isArray(data.results) && data.results[0]) {
        const r = data.results[0]
        sendResults.value.push({ recipient: r.recipient || to, success: !!r.success, error: r.error || '' })
      } else {
        sendResults.value.push({ recipient: to, success: false, error: (data && data.message) || '发送失败' })
      }
    } catch (e) {
      sendResults.value.push({ recipient: to, success: false, error: e?.message || String(e) })
    }
    sentCount.value++
  }
  isSending.value = false
}

function abortSend () {
  if (!isSending.value) return
  abortFlag.value = true
}
</script>

<style scoped>
.email-mail-merge :where(.card){ border:1px solid #eef0f3; }

/* Modern header */
.mm-header{
  background: linear-gradient(135deg, rgba(13,110,253,.12), rgba(32,201,151,.12));
  border: 1px solid rgba(0,0,0,.04);
}
.mm-logo{ width:38px; height:38px; border-radius:8px; object-fit:cover; box-shadow:0 2px 6px rgba(0,0,0,.1); }

/* Stepper */
.stepper{ background:#f8f9fa; border:1px dashed #e6e8eb; }
.stepper .step{ display:flex; flex-direction:column; align-items:center; gap:6px; }
.stepper .bullet{ width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:600; background:#e9ecef; color:#495057; box-shadow: inset 0 0 0 2px #fff; }
.stepper .step.active .bullet{ background:#0d6efd; color:#fff; box-shadow:none; }
.stepper .label{ font-size:12px; color:#6c757d; font-weight:600; }
.stepper .sep{ flex:1; height:2px; background:linear-gradient(90deg,#e9ecef,#e9ecef); margin:0 8px; border-radius:2px; }

/* 简易富文本编辑器样式 */
.rte{
  min-height: 140px;
  overflow-y: auto;
}
.rte[contenteditable="true"]:empty:before{
  content: attr(data-placeholder);
  color:#6c757d;
}
.rte b, .rte strong{ font-weight:700; }

.rte-toolbar{ border:1px solid #eef0f3; background:#fafbfc; }
.rte-toolbar .btn{ min-width:34px; }

/* Table */
.mm-table-wrap{ max-height: 50vh; }
.mm-table thead th{ position: sticky; top:0; background:#f8f9fa; z-index:1; }
.mm-table tbody tr:hover{ background:#fafbff; }
.table code{ font-size: 12px; }

/* Dropzone */
.dropzone{ border:2px dashed #cbd5e1; border-radius:12px; padding:24px; background:#fbfdff; cursor:pointer; transition: all .2s ease; }
.dropzone:hover{ border-color:#0d6efd; background:#f7fbff; }

/* Preview card */
.mm-preview-item{ transition: box-shadow .2s ease, transform .2s ease; }
.mm-preview-item:hover{ box-shadow:0 6px 20px rgba(0,0,0,.08); transform: translateY(-1px); }
</style>
