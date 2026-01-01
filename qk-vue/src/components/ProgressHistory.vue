<template>
  <div class="main-content">
    <h3>📊 进度历史</h3>
    <div class="coming-soon">
      <div class="coming-soon-content">
        <i class="bi bi-tools"></i>
        <h4>正在开发中...</h4>
        <p>该功能即将上线，敬请期待！</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// 进度历史页面组件
</script>

<style scoped>
.main-content {
  margin-left: 0;
  padding: 40px;
  min-height: 100vh;
  background: #f8f9fa;
}

.coming-soon {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
}

.coming-soon-content {
  text-align: center;
  padding: 60px 40px;
}

.coming-soon-content i {
  font-size: 64px;
  color: #6c757d;
  margin-bottom: 20px;
  display: block;
}

.coming-soon-content h4 {
  font-size: 28px;
  color: #495057;
  margin-bottom: 15px;
  font-weight: 600;
}

.coming-soon-content p {
  font-size: 16px;
  color: #6c757d;
  margin: 0;
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px;
  }
  
  .coming-soon-content {
    padding: 40px 20px;
  }
  
  .coming-soon-content i {
    font-size: 48px;
  }
  
  .coming-soon-content h4 {
    font-size: 24px;
  }
}
</style>

