<template>
  <div class="container py-4">
    <h2 class="mb-3">邮件批量发送示例页（不入导航）</h2>
    <p class="text-muted">此页用于演示调用后端批量发信接口。请按需填写 SMTP 参数与邮件内容。</p>

    <div class="card mb-4">
      <div class="card-header">SMTP 配置（可修改）</div>
      <div class="card-body row g-3">
        <div class="col-md-4">
          <label class="form-label">SMTP 服务器</label>
          <input class="form-control" v-model="form.smtp_server" placeholder="mail.cstnet.cn" />
        </div>
        <div class="col-md-2">
          <label class="form-label">端口</label>
          <input class="form-control" type="number" v-model.number="form.smtp_port" placeholder="465" />
        </div>
        <div class="col-md-3">
          <label class="form-label">发件人邮箱</label>
          <input class="form-control" v-model="form.sender_email" placeholder="example@domain.com" />
        </div>
        <div class="col-md-3">
          <label class="form-label">发件人密码/授权码</label>
          <input class="form-control" v-model="form.sender_password" type="password" placeholder="邮箱密码或授权码" />
        </div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between">
        <span>邮件内容</span>
        <div>
          <button class="btn btn-sm btn-outline-secondary me-2" @click="prefillSample">填充示例</button>
          <button class="btn btn-sm btn-outline-danger" @click="clearAll">清空</button>
        </div>
      </div>
      <div class="card-body row g-3">
        <div class="col-md-12">
          <label class="form-label">主题</label>
          <input class="form-control" v-model="form.subject" />
        </div>
        <div class="col-md-12">
          <label class="form-label">HTML 正文</label>
          <textarea class="form-control" rows="10" v-model="form.html_body"></textarea>
        </div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-header">收件人与附件</div>
      <div class="card-body row g-3">
        <div class="col-md-6">
          <label class="form-label">收件人邮箱（每行一个）</label>
          <textarea class="form-control" rows="6" v-model="receiversText" placeholder="a@x.com\nb@y.com"></textarea>
        </div>
        <div class="col-md-6">
          <label class="form-label">个性化附件（与收件人逐行对应；多附件用逗号分隔）</label>
          <textarea class="form-control" rows="6" v-model="uniqueAttachmentsText" placeholder="./email/1甲.pdf,./email/1回执.xlsx\n./email/2乙.pdf"></textarea>
        </div>
        <div class="col-md-12">
          <label class="form-label">通用附件（逗号分隔，可为空）</label>
          <input class="form-control" v-model="commonAttachmentsText" placeholder="./email/通用说明.pdf,./email/回执模板.xlsx" />
        </div>
      </div>
    </div>

    <div class="d-flex align-items-center gap-2">
      <button class="btn btn-primary" :disabled="loading" @click="submitSend">
        <span v-if="!loading">提交发送</span>
        <span v-else class="spinner-border spinner-border-sm"></span>
      </button>
      <span class="text-muted">提交后会逐个发送，请耐心等待返回结果。</span>
    </div>

    <div v-if="results.length" class="card mt-4">
      <div class="card-header">发送结果</div>
      <div class="list-group list-group-flush">
        <div v-for="(r, idx) in results" :key="idx" class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <strong>{{ r.recipient }}</strong>
            <span v-if="r.success" class="badge bg-success ms-2">成功</span>
            <span v-else class="badge bg-danger ms-2">失败</span>
          </div>
          <div class="text-muted small" v-if="!r.success">{{ r.error }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* global defineExpose */
import { ref } from 'vue'
import axios from 'axios'

const form = ref({
  smtp_server: '',
  smtp_port: 465,
  sender_email: '',
  sender_password: '',
  subject: '',
  html_body: ''
})

const receiversText = ref('')
const uniqueAttachmentsText = ref('')
const commonAttachmentsText = ref('')

const loading = ref(false)
const results = ref([])

function parseList(text) {
  return text
    .split(/\r?\n/)
    .map(s => s.trim())
    .filter(Boolean)
}

function parseCommaList(text) {
  return text
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
}

function prefillSample() {
  form.value.smtp_server = 'mail.cstnet.cn'
  form.value.smtp_port = 465
  form.value.sender_email = 'jcip@iscas.ac.cn'
  form.value.sender_password = 'GtVkDjHbcH8^@sFc'
  form.value.subject = '中文信息学报-2025年6期3校'
  form.value.html_body = `
<p>作者您好！</p>
<p>&nbsp;&nbsp;现将稿件三校版本发给您，请您再次仔细检查。</p>
<p>&nbsp;&nbsp;因排版厂为人工誊样复核，因此修改后的稿件仍然可能存在标注出的地方未被正确修改的情况，本次核查请您尤其注意<strong><u>论文前两次修改的地方是否已被正确更改</u></strong>，同时再通读论文核查是否还有需要修订的地方；如有问题请及时反馈。</p>
<p>&nbsp;&nbsp;由于时间紧迫，请最晚于<strong><u>6月23日上午10点前</u></strong>回复是否有需要修改的地方。谢谢！</p>
<p><mark style="color: red;"><strong>此邮件为自动化程序批量发送，如您发现附件缺失、错误或无法打开，敬请谅解，并请及时联系编辑部。</strong></mark></p>
<p>《中文信息学报》编辑部</p>
<p>2025年6月19日</p>
<hr style="border: none; border-top: 1px solid #ccc; margin-top:20px; margin-bottom:10px;" />
<p><a href="mailto:jcip@iscas.ac.cn">jcip@iscas.ac.cn</a></p>`

  receiversText.value = 'zhuq22@m.fudan.edu.cn\nkongyuanbo@mail.las.ac.cn'
  uniqueAttachmentsText.value = './email/17朱秦.pdf\n./email/18测试.pdf'
  commonAttachmentsText.value = ''
}

function clearAll() {
  form.value = {
    smtp_server: '',
    smtp_port: 465,
    sender_email: '',
    sender_password: '',
    subject: '',
    html_body: ''
  }
  receiversText.value = ''
  uniqueAttachmentsText.value = ''
  commonAttachmentsText.value = ''
  results.value = []
}

async function submitSend() {
  const receiver_emails = parseList(receiversText.value)
  const unique_lines = parseList(uniqueAttachmentsText.value)
  const unique_attachments = unique_lines.map(line => parseCommaList(line))
  const common_attachments = parseCommaList(commonAttachmentsText.value)

  if (!form.value.smtp_server || !form.value.smtp_port || !form.value.sender_email || !form.value.sender_password) {
    alert('请完整填写 SMTP 配置')
    return
  }
  if (receiver_emails.length === 0) {
    alert('请至少填写一个收件人')
    return
  }
  if (receiver_emails.length !== unique_attachments.length) {
    alert('收件人与个性化附件行数不一致')
    return
  }

  loading.value = true
  results.value = []
  try {
    const resp = await axios.post('/api/email/send-bulk/', {
      smtp_server: form.value.smtp_server,
      smtp_port: form.value.smtp_port,
      sender_email: form.value.sender_email,
      sender_password: form.value.sender_password,
      subject: form.value.subject,
      html_body: form.value.html_body,
      receiver_emails,
      unique_attachments,
      common_attachments
    })
    if (resp.data && resp.data.results) {
      results.value = resp.data.results
    } else {
      alert('发送完成，但返回数据格式异常')
    }
  } catch (e) {
    alert('发送失败: ' + (e?.response?.data?.message || e.message))
  } finally {
    loading.value = false
  }
}

// 暴露刷新钩子（若从父级调用）
function refresh() {}

defineExpose({ refresh })
</script>

<style scoped>
.container { max-width: 1100px; }
</style>
