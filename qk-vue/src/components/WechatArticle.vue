<template>
  <div class="main-content">
    <h3>💡公众号文章生成</h3>
    
    <div class="action-bar mb-3">
      <button class="btn btn-primary me-2" @click="importSampleContent">
        <i class="bi bi-file-earmark-text"></i> 导入示例内容
      </button>
      <button 
        class="btn btn-success" 
        @click="fetchJournalContent"
        :disabled="loading"
      >
        <i class="bi bi-cloud-download"></i>
        {{ loading ? '获取中...' : '获取期刊内容' }}
      </button>
    </div>

    <!-- 嵌入项目 B -->
    <div class="embedded-section">
      <iframe
        ref="editorIframe"
        src="/md/index.html"
        style="width: 100%; height: 100vh; border: none;"
        title="Markdown编辑器"
        @load="handleIframeLoad"
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const editorIframe = ref(null);
const loading = ref(false);

// 示例内容
const sampleContent = `# 示例文章标题

## 1. 引言
这是一篇示例文章，用于演示Markdown编辑器的功能。

## 2. 主要特点
- 支持Markdown语法
- 实时预览
- 一键导出

## 3. 使用说明
1. 在左侧编辑框输入内容
2. 右侧可以实时预览效果
3. 编辑完成后可以导出

> 这是一个引用示例

### 代码示例
\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`

## 4. 总结
这是一个简单的示例文章，您可以基于此进行修改和扩展。
`;

// iframe加载完成后的处理
const handleIframeLoad = () => {
  console.log('Iframe loaded');
  // 检查 iframe 内部的编辑器
  const iframeWindow = editorIframe.value.contentWindow;
  const checkEditor = setInterval(() => {
    const cmElement = iframeWindow.document.querySelector('.CodeMirror');
    console.log('Checking editor:', cmElement);
    if (cmElement && cmElement.CodeMirror) {
      console.log('Found editor instance:', cmElement.CodeMirror);
      clearInterval(checkEditor);
      // 尝试直接设置内容
      try {
        cmElement.CodeMirror.setValue(sampleContent);
        cmElement.CodeMirror.refresh();
        console.log('Test content set');
      } catch (error) {
        console.error('Error setting test content:', error);
      }
    }
  }, 1000);
};

// 导入示例内容
const importSampleContent = () => {
  console.log('Import button clicked');
  const iframeWindow = editorIframe.value.contentWindow;
  const cmElement = iframeWindow.document.querySelector('.CodeMirror');
  console.log('Found editor on import:', cmElement);
  if (cmElement && cmElement.CodeMirror) {
    try {
      cmElement.CodeMirror.setValue(sampleContent);
      cmElement.CodeMirror.refresh();
      console.log('Content set directly');
    } catch (error) {
      console.error('Error setting content directly:', error);
    }
  } else {
    console.error('Editor not found on import');
  }
};

// 获取期刊内容
const fetchJournalContent = async () => {
  loading.value = true;
  try {
    const response = await fetch('http://127.0.0.1:8000/api/journal/');
    const data = await response.json();
    
    if (data.status === 'success') {
      const iframeWindow = editorIframe.value.contentWindow;
      const cmElement = iframeWindow.document.querySelector('.CodeMirror');
      if (cmElement && cmElement.CodeMirror) {
        cmElement.CodeMirror.setValue(data.data.markdown);
        cmElement.CodeMirror.refresh();
      }
    } else {
      console.error('Failed to fetch journal content:', data.message);
      alert('获取期刊内容失败');
    }
  } catch (error) {
    console.error('Error fetching journal content:', error);
    alert('获取期刊内容失败');
  } finally {
    loading.value = false;
  }
};

// 监听来自 iframe 的消息
window.addEventListener('message', (event) => {
  console.log('Received message from iframe:', event.data);
});
</script>

<style scoped>
.main-content {
  margin-left: 250px;
  padding: 20px;
  max-width: 1200px;
}

.action-bar {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.embedded-section {
  background: white;
  padding: 0;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
