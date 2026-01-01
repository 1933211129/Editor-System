<template>
  <div class="main-content">
    <h3>📚参考文献纠错</h3>
    <div class="reference-container">
      <div class="input-section">
        <h4>输入参考文献</h4>
        <textarea
          v-model="inputReferences"
          placeholder="请粘贴参考文献内容，每条文献占一行..."
          rows="15"
          class="reference-input"
        ></textarea>
        <div class="button-group">
          <button @click="checkReferences" class="check-btn" :disabled="loading">
            {{ loading ? '检查中...' : '开始检查' }}
          </button>
          <button @click="clearInput" class="clear-btn">清空输入</button>
        </div>
      </div>
      
      <div class="output-section">
        <h4>检查结果</h4>
        <div class="result-container">
          <div v-if="loading" class="loading">
            <div class="spinner"></div>
            正在检查参考文献格式...
          </div>
          <div v-else-if="checkResult" class="result-content">
            <pre>{{ checkResult }}</pre>
          </div>
          <div v-else class="placeholder-result">
            检查结果将在此显示...
          </div>
        </div>
        <div class="button-group" v-if="checkResult">
          <button @click="copyResult" class="copy-btn">一键复制</button>
          <button @click="exportResult" class="export-btn">导出TXT</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ReferenceCheck',
  data() {
    return {
      inputReferences: '',
      checkResult: '',
      loading: false
    }
  },
  methods: {
    async checkReferences() {
      if (!this.inputReferences.trim()) {
        alert('请输入参考文献内容')
        return
      }
      
      this.loading = true
      try {
        const response = await axios.post('/api/reference/check/', {
          references: this.inputReferences
        })
        
        if (response.data.status === 'success') {
          this.checkResult = response.data.result
        } else {
          alert('检查失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('检查参考文献时出错:', error)
        alert('检查失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    clearInput() {
      this.inputReferences = ''
      this.checkResult = ''
    },
    
    copyResult() {
      if (this.checkResult) {
        navigator.clipboard.writeText(this.checkResult).then(() => {
          alert('结果已复制到剪贴板')
        }).catch(() => {
          // 备用复制方法
          const textArea = document.createElement('textarea')
          textArea.value = this.checkResult
          document.body.appendChild(textArea)
          textArea.select()
          document.execCommand('copy')
          document.body.removeChild(textArea)
          alert('结果已复制到剪贴板')
        })
      }
    },
    
    exportResult() {
      if (this.checkResult) {
        const now = new Date()
        const datetime = now.getFullYear() + 
          String(now.getMonth() + 1).padStart(2, '0') + 
          String(now.getDate()).padStart(2, '0') + '_' +
          String(now.getHours()).padStart(2, '0') + 
          String(now.getMinutes()).padStart(2, '0') + 
          String(now.getSeconds()).padStart(2, '0')
        
        const filename = `参考文献纠错_${datetime}.txt`
        const blob = new Blob([this.checkResult], { type: 'text/plain;charset=utf-8' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        link.click()
        window.URL.revokeObjectURL(url)
      }
    }
  }
}
</script>

<style scoped>
.main-content {
  margin-left: 250px;
  padding: 20px;
}

.reference-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 120px);
}

.input-section, .output-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.input-section h4, .output-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.reference-input {
  flex: 1;
  width: 100%;
  padding: 15px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  transition: border-color 0.3s;
}

.reference-input:focus {
  border-color: #007bff;
}

.result-container {
  flex: 1;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  padding: 15px;
  background: #f8f9fa;
  overflow-y: auto;
}

.result-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.placeholder-result {
  color: #666;
  text-align: center;
  padding: 50px 20px;
  font-style: italic;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.check-btn, .clear-btn, .copy-btn, .export-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.check-btn {
  background: #007bff;
  color: white;
}

.check-btn:hover:not(:disabled) {
  background: #0056b3;
}

.check-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.clear-btn {
  background: #6c757d;
  color: white;
}

.clear-btn:hover {
  background: #545b62;
}

.copy-btn {
  background: #28a745;
  color: white;
}

.copy-btn:hover {
  background: #1e7e34;
}

.export-btn {
  background: #17a2b8;
  color: white;
}

.export-btn:hover {
  background: #117a8b;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
  
  .reference-container {
    flex-direction: column;
    height: auto;
  }
  
  .reference-input {
    min-height: 200px;
  }
  
  .result-container {
    min-height: 300px;
  }
}
</style> 