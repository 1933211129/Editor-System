<template>
  <div id="app">
    <SideBar />
    <router-view></router-view>
  </div>
</template>

<script setup>
import SideBar from './components/SideBar.vue'
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 主内容区域样式 - 确保不被侧边栏遮挡 */
.router-view,
router-view {
  margin-left: 250px; /* 默认侧边栏宽度 */
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

/* 响应式主内容区域 */
@media (max-width: 1200px) {
  .router-view,
  router-view {
    margin-left: 220px; /* 中等屏幕 */
  }
}

@media (max-width: 992px) {
  .router-view,
  router-view {
    margin-left: 200px; /* 小屏幕 */
  }
}

@media (max-width: 768px) {
  .router-view,
  router-view {
    margin-left: 70px; /* 移动端图标模式 */
  }
}

@media (max-width: 576px) {
  .router-view,
  router-view {
    margin-left: 60px; /* 超小屏幕 */
  }
}

/* 为了兼容一些组件可能使用的类名 */
.main-content {
  margin-left: 250px;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

@media (max-width: 1200px) {
  .main-content {
    margin-left: 220px;
  }
}

@media (max-width: 992px) {
  .main-content {
    margin-left: 200px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 70px;
  }
}

@media (max-width: 576px) {
  .main-content {
    margin-left: 60px;
  }
}
</style>
