<template>
  <!-- 左侧悬停检测区域 -->
  <div class="hover-trigger" 
       @mouseenter="showSidebar" 
       @mouseleave="hideSidebar"
       :class="{ 'active': isSidebarVisible }"
       title="悬停显示导航">
    <div class="hover-indicator" v-if="!isSidebarVisible">
      <i class="bi bi-chevron-right"></i>
    </div>
  </div>
  
  <!-- 侧边栏主体 -->
  <div class="sidebar" 
       :class="{ 'sidebar-visible': isSidebarVisible }"
       @mouseenter="showSidebar" 
       @mouseleave="hideSidebar">
    <div class="logo">
      <div class="logo-content">
        <img src="../assets/zw.png" alt="中文信息学报" class="logo-img">
        <div class="logo-text">中文信息学报<br>期刊管理系统</div>
      </div>
    </div>
    <nav class="nav flex-column">
      <!-- 小屏幕下的展开/收起按钮 -->
      <div class="nav-toggle" @click="toggleNav" v-if="isSmallScreen">
        <i class="bi" :class="isNavCollapsed ? 'bi-chevron-down' : 'bi-chevron-up'"></i>
        <span v-if="!isNavCollapsed">收起导航</span>
        <span v-if="isNavCollapsed">展开导航</span>
      </div>
      
      <div class="nav-content">
        <!-- 核心看板 -->
        <router-link to="/progress" class="nav-link" active-class="active">
          <i class="bi bi-kanban"></i>
          <span>期刊文章进度管理</span>
        </router-link>
        <router-link to="/progress-history" class="nav-link" active-class="active">
          <i class="bi bi-clock-history"></i>
          <span>进度管理历史记录</span>
        </router-link>
        <router-link to="/statistics" class="nav-link" active-class="active">
          <i class="bi bi-bar-chart"></i>
          <span>文章预排期管理</span>
        </router-link>
        <router-link to="/reference" class="nav-link" active-class="active">
          <i class="bi bi-book"></i>
          <span>参考文献纠错</span>
        </router-link>
        <router-link to="/wechat" class="nav-link" active-class="active">
          <i class="bi bi-newspaper"></i>
          <span>公众号文章生成</span>
        </router-link>

        <div class="divider" aria-hidden="true"></div>

        <!-- 人员管理 -->
        <router-link to="/contacts" class="nav-link" active-class="active">
          <i class="bi bi-person-lines-fill"></i>
          <span>作者通讯录管理</span>
        </router-link>
        <router-link to="/reviewers" class="nav-link" active-class="active">
          <i class="bi bi-people"></i>
          <span>责编管理</span>
        </router-link>

        <div class="divider" aria-hidden="true"></div>

        <!-- 通讯与文档 -->
        <router-link to="/email" class="nav-link" active-class="active">
          <i class="bi bi-envelope"></i>
          <span>邮件批量发送</span>
        </router-link>
        <router-link to="/notification" class="nav-link" active-class="active">
          <i class="bi bi-file-earmark-text"></i>
          <span>通知文件生成</span>
        </router-link>

        <div class="divider" aria-hidden="true"></div>

        <!-- 其他 -->
        <router-link to="/invoice" class="nav-link" active-class="active">
          <i class="bi bi-receipt"></i>
          <span>发票登记</span>
        </router-link>
        <router-link to="/todos" class="nav-link" active-class="active">
          <i class="bi bi-check2-square"></i>
          <span>待办事项</span>
        </router-link>
      </div>
    </nav>

    <!-- 用户信息模块 -->
    <div class="user-info">
      <div class="user-welcome" v-if="isAuthenticated">
        <span class="welcome-text">👋 欢迎！{{ username }}</span>
        <button class="nav-link logout-btn" @click="handleLogout">
          <i class="bi bi-box-arrow-right"></i>
          <span>退出登录</span>
        </button>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="footer-info">
      <p>
        ®InsightLens<br>
        <a target="_blank" href="https://beian.miit.gov.cn/">京ICP备2024093370号-2</a>
      </p>
      <p class="support">
        技术支持：<br>
        <a href="mailto:kongyuanbo@mail.las.ac.cn">kongyuanbo@mail.las.ac.cn</a>
      </p>
    </div>
  </div>
</template>

<script>
import mitt from 'mitt'  // 需要安装: npm install mitt

// 创建事件总线
export const emitter = mitt()

export default {
  name: 'SideBar',
  data() {
    return {
      isAuthenticated: false,
      username: '',
      isNavCollapsed: false,
      isSmallScreen: false,
      isSidebarVisible: false,
      hideTimeout: null
    }
  },
  created() {
    this.checkAuthStatus()
    // 监听登录成功事件
    emitter.on('loginSuccess', this.checkAuthStatus)
    // 监听窗口大小变化
    window.addEventListener('resize', this.checkScreenSize)
  },
  mounted() {
    // 组件挂载后再次检查
    this.$nextTick(() => {
      this.checkScreenSize()
      console.log('Component mounted, checking nav content...')
      const navContent = document.querySelector('.nav-content')
      if (navContent) {
        console.log('Nav content found:', navContent)
        console.log('Nav content style:', window.getComputedStyle(navContent))
      } else {
        console.log('Nav content NOT found!')
      }
    })
  },
  beforeUnmount() {
    // 清理事件监听
    emitter.off('loginSuccess', this.checkAuthStatus)
    window.removeEventListener('resize', this.checkScreenSize)
  },
  methods: {
    checkAuthStatus() {
      const token = localStorage.getItem('token')
      const username = localStorage.getItem('username')
      this.isAuthenticated = !!token
      this.username = username || ''
    },
    handleLogout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.isAuthenticated = false
      this.username = ''
      this.$router.push('/login')
    },
    checkScreenSize() {
      this.isSmallScreen = window.innerWidth <= 992
      // 小屏幕默认展开导航，让用户能看到内容
      if (this.isSmallScreen) {
        this.isNavCollapsed = false
      } else {
        this.isNavCollapsed = false
      }
      // 调试信息
      console.log('Screen width:', window.innerWidth, 'isSmallScreen:', this.isSmallScreen, 'isNavCollapsed:', this.isNavCollapsed)
      
      // 只在DOM元素存在时检查
      const navContent = document.querySelector('.nav-content')
      if (navContent) {
        console.log('Nav content element:', navContent)
        console.log('Nav content classes:', navContent.className)
        console.log('Nav content computed style:', window.getComputedStyle(navContent))
      } else {
        console.log('Nav content element not found yet')
      }
    },
    toggleNav() {
      this.isNavCollapsed = !this.isNavCollapsed
      console.log('Toggle nav clicked, isNavCollapsed:', this.isNavCollapsed)
      // 强制重新渲染
      this.$forceUpdate()
    },
    showSidebar() {
      // 清除隐藏定时器
      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout)
        this.hideTimeout = null
      }
      this.isSidebarVisible = true
    },
    hideSidebar() {
      // 延迟隐藏，给用户时间移动鼠标
      this.hideTimeout = setTimeout(() => {
        this.isSidebarVisible = false
      }, 300)
    }
  }
}
</script>

<style scoped>
/* 左侧悬停触发区域 */
.hover-trigger {
  position: fixed;
  top: 0;
  left: 0;
  width: 20px;
  height: 100vh;
  z-index: 1001;
  background: transparent;
  transition: all 0.3s ease;
  cursor: pointer;
}

.hover-trigger:hover {
  background: rgba(52, 73, 94, 0.1);
  width: 30px;
}

.hover-trigger.active {
  width: 30px;
  background: rgba(52, 73, 94, 0.2);
}

/* 悬停指示器 */
.hover-indicator {
  position: absolute;
  top: 50%;
  right: 5px;
  transform: translateY(-50%);
  color: #b8c7ce;
  font-size: 12px;
  opacity: 0.6;
  transition: all 0.3s ease;
  animation: pulse 2s infinite;
}

.hover-trigger:hover .hover-indicator {
  opacity: 1;
  color: #3498db;
  transform: translateY(-50%) scale(1.2);
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* 侧边栏主体 */
.sidebar {
  position: fixed;
  top: 0;
  left: -250px; /* 默认隐藏 */
  height: 100vh;
  width: 250px;
  background: #2c3e50;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); /* 更流畅的动画 */
  z-index: 1000;
  overflow: hidden;
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.15);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-visible {
  left: 0; /* 显示时移入视窗 */
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.25);
}

.sidebar .logo {
  padding: 20px 25px;
  flex-shrink: 0; /* 防止logo被压缩 */
}

.sidebar .logo-text {
  color: white;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.3;
}

.nav {
  flex: 1; /* 占据剩余空间 */
  display: flex;
  flex-direction: column;
  padding: 10px 0;
  overflow-y: auto; /* 导航项过多时可滚动 */
  overflow-x: hidden; /* 防止水平滚动条 */
  min-height: 0; /* 允许flex子项收缩 */
  max-height: calc(100vh - 200px); /* 限制最大高度，确保滚动 */
  width: 100%; /* 确保宽度占满 */
}

/* 导航切换按钮 */
.nav-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  color: #b8c7ce;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 14px;
  flex-shrink: 0;
}

.nav-toggle:hover {
  color: white;
  background: #34495e;
}

.nav-toggle i {
  font-size: 16px;
}

/* 导航内容容器 */
.nav-content {
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow: visible;
  max-height: none;
  opacity: 1;
  visibility: visible;
  position: relative;
  z-index: 1;
}

/* 大屏幕下隐藏切换按钮 */
@media (min-width: 993px) {
  .nav-toggle {
    display: none;
  }
  
  .nav-content {
    max-height: none;
    opacity: 1;
    visibility: visible;
    overflow: visible;
  }
}

.sidebar .nav-link {
  padding: 12px 25px;
  color: #b8c7ce;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0; /* 防止导航项被压缩 */
  white-space: nowrap; /* 防止文字换行 */
  overflow: hidden; /* 隐藏溢出内容 */
  width: 100%; /* 确保宽度占满 */
  box-sizing: border-box; /* 包含padding和border */
}

.sidebar .nav-link:hover {
  color: white;
  background: #34495e;
  padding-left: 30px;
}

.sidebar .nav-link.active {
  color: white;
  background: #34495e;
  border-left: 4px solid #3498db;
}

/* 用户信息模块 */
.user-info {
  flex-shrink: 0; /* 防止用户信息被压缩 */
  padding: 15px 25px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-welcome {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.welcome-text {
  color: #fff;
  font-size: 13px;
  text-align: center;
  word-break: break-word; /* 防止用户名过长 */
}

.logout-btn {
  width: 85%;
  color: #b8c7ce !important;
  background: none;
  border: none;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 4px;
  font-size: 13px;
}

.logout-btn:hover {
  color: white !important;
  background: #34495e;
}

/* 视觉分隔线 */
.divider {
  margin: 8px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
}

/* 底部信息样式 */
.footer-info {
  flex-shrink: 0; /* 防止底部信息被压缩 */
  text-align: center;
  padding: 15px 20px;
  font-size: 11px;
  color: #6c757d;
  line-height: 1.4;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-info a {
  color: #6c757d;
  text-decoration: none;
}

.footer-info a:hover {
  color: #0d6efd;
}

.support {
  margin-top: 8px;
  font-size: 11px;
}

.logo-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-img {
  width: 35px;
  height: auto;
  object-fit: contain;
}

/* 新功能标记样式 */
.new-badge {
  font-size: 11px;
  color: #ff4444;
  margin-left: 6px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.3; }
  100% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar {
    width: 220px; /* 中等屏幕稍微收窄 */
    left: -220px; /* 调整隐藏位置 */
  }
  
  .sidebar-visible {
    left: 0;
  }
  
  .sidebar .logo-text {
    font-size: 16px;
  }
  
  .footer-info {
    font-size: 10px;
  }
  
  .nav {
    overflow-y: auto; /* 确保中等屏幕也能滚动 */
    max-height: calc(100vh - 180px); /* 调整最大高度 */
  }
}

@media (max-width: 992px) {
  .sidebar {
    width: 200px; /* 小屏幕进一步收窄 */
    left: -200px; /* 调整隐藏位置 */
  }
  
  .sidebar-visible {
    left: 0;
  }
  
  .sidebar .nav-link {
    padding: 10px 20px;
    font-size: 14px;
    width: 100%; /* 确保宽度占满 */
  }
  
  .sidebar .logo {
    padding: 15px 20px;
  }
  
  .user-info {
    padding: 12px 20px;
  }
  
  .nav {
    overflow-y: auto; /* 小屏幕确保垂直滚动 */
    overflow-x: hidden; /* 防止水平滚动 */
    max-height: calc(100vh - 180px); /* 减少最大高度，确保有滚动条 */
    width: 100%; /* 确保宽度占满 */
    flex: 1; /* 占据剩余空间 */
  }
  
  /* 小屏幕下显示切换按钮 */
  .nav-toggle {
    display: flex;
  }
  
  /* 小屏幕下默认展开导航内容 */
  .nav-content {
    max-height: none;
    opacity: 1;
    overflow: visible;
    visibility: visible;
    display: flex;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 70px; /* 移动端收缩为图标模式 */
    left: -70px; /* 调整隐藏位置 */
    padding: 0;
  }
  
  .sidebar-visible {
    left: 0;
  }
  
  .sidebar .logo-text {
    display: none;
  }
  
  .sidebar .nav-link span {
    display: none;
  }
  
  .sidebar .nav-link {
    padding: 15px;
    justify-content: center;
    width: 100%; /* 确保宽度占满 */
  }
  
  .sidebar .nav-link:hover {
    padding-left: 15px; /* 移动端不需要左移效果 */
  }
  
  .logo-img {
    display: none;
  }
  
  .user-info {
    padding: 10px 5px;
  }
  
  .welcome-text {
    display: none; /* 移动端隐藏欢迎文字 */
  }
  
  .logout-btn {
    width: 50px;
    height: 50px;
    padding: 0;
    border-radius: 50%;
  }
  
  .logout-btn span {
    display: none; /* 只显示图标 */
  }
  
  .footer-info {
    display: none; /* 移动端隐藏底部信息 */
  }
  
  .new-badge {
    display: none;
  }
  
  .divider {
    margin: 5px 10px;
  }
  
  .nav {
    overflow-y: auto; /* 移动端确保垂直滚动 */
    overflow-x: hidden; /* 防止水平滚动 */
    max-height: calc(100vh - 120px); /* 减少最大高度，确保有滚动条 */
    width: 100%; /* 确保宽度占满 */
    flex: 1; /* 占据剩余空间 */
  }
  
  /* 移动端切换按钮样式 */
  .nav-toggle {
    padding: 10px 5px;
    font-size: 12px;
  }
  
  .nav-toggle span {
    display: none; /* 移动端只显示图标 */
  }
  
  .nav-toggle i {
    font-size: 14px;
  }
  
  /* 移动端导航内容默认展开 */
  .nav-content {
    max-height: none;
    opacity: 1;
    overflow: visible;
    visibility: visible;
    display: flex;
  }
}

@media (max-width: 576px) {
  .sidebar {
    width: 60px; /* 超小屏幕进一步收窄 */
    left: -60px; /* 调整隐藏位置 */
  }
  
  .sidebar-visible {
    left: 0;
  }
  
  .sidebar .nav-link {
    padding: 12px 8px;
    width: 100%; /* 确保宽度占满 */
  }
  
  .logout-btn {
    width: 45px;
    height: 45px;
  }
  
  .nav {
    overflow-y: auto; /* 超小屏幕确保垂直滚动 */
    overflow-x: hidden; /* 防止水平滚动 */
    max-height: calc(100vh - 100px); /* 减少最大高度，确保有滚动条 */
    width: 100%; /* 确保宽度占满 */
    flex: 1; /* 占据剩余空间 */
  }
}

/* 高度较小的屏幕优化 */
@media (max-height: 700px) {
  .sidebar .logo {
    padding: 15px 25px;
  }
  
  .sidebar .nav-link {
    padding: 10px 25px;
    width: 100%; /* 确保宽度占满 */
  }
  
  .footer-info {
    font-size: 10px;
    padding: 10px 15px;
  }
  
  .user-info {
    padding: 10px 25px;
  }
  
  .nav {
    overflow-y: auto; /* 高度不足时确保垂直滚动 */
    overflow-x: hidden; /* 防止水平滚动 */
    max-height: calc(100vh - 120px); /* 减少最大高度，确保有滚动条 */
    width: 100%; /* 确保宽度占满 */
    flex: 1; /* 占据剩余空间 */
  }
}

/* 为悬停式侧边栏添加全局样式 */
:global(.main-content) {
  margin-left: 0 !important; /* 移除固定左边距 */
  transition: margin-left 0.3s ease;
}

:global(.main-content.sidebar-visible) {
  margin-left: 0 !important; /* 悬停式侧边栏不占用主内容空间 */
}

@media (max-height: 600px) {
  .sidebar .logo {
    padding: 10px 25px;
  }
  
  .sidebar .nav-link {
    padding: 8px 25px;
    font-size: 13px;
    width: 100%; /* 确保宽度占满 */
  }
  
  .footer-info {
    display: none; /* 高度不够时隐藏底部信息 */
  }
  
  .nav {
    overflow-y: auto; /* 高度严重不足时确保垂直滚动 */
    overflow-x: hidden; /* 防止水平滚动 */
    max-height: calc(100vh - 120px); /* 调整最大高度 */
    width: 100%; /* 确保宽度占满 */
  }
}
</style> 
