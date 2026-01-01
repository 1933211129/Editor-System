<template>
  <div class="todo-container">
    <div class="todo-header">
      <h2><i class="bi bi-check2-square"></i> 待办事项管理</h2>
    </div>

    <!-- 添加新待办事项 -->
    <div class="add-todo-section">
      <div class="add-todo-form">
        <div class="form-row">
          <div class="form-group">
            <label>任务内容</label>
            <input 
              type="text" 
              v-model="newTodo.content" 
              placeholder="请输入待办事项内容..."
              class="form-control"
              @keyup.enter="addTodo"
            >
          </div>
          <div class="form-group">
            <label>添加人</label>
            <select v-model="newTodo.assignee" class="form-control">
              <option value="">请选择添加人</option>
              <option v-for="user in users" :key="user" :value="user">{{ user }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>优先级</label>
            <select v-model="newTodo.priority" class="form-control">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </div>
          <div class="form-group">
            <label>截止日期</label>
            <input 
              type="date" 
              v-model="newTodo.dueDate" 
              class="form-control"
            >
          </div>
        </div>
        <button @click="addTodo" class="btn btn-primary add-btn">
          <i class="bi bi-plus-circle"></i> 添加待办事项
        </button>
      </div>
    </div>

    <!-- 筛选和统计 -->
    <div class="filter-section">
      <div class="filter-controls">
        <div class="filter-group">
          <label>筛选状态：</label>
          <select v-model="filterStatus" class="form-control-sm">
            <option value="">全部</option>
            <option value="in_progress">进行中</option>
            <option value="completed">已完成</option>
          </select>
        </div>
        <div class="filter-group">
          <label>筛选人员：</label>
          <select v-model="filterAssignee" class="form-control-sm">
            <option value="">全部人员</option>
            <option v-for="user in users" :key="user" :value="user">{{ user }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>优先级：</label>
          <select v-model="filterPriority" class="form-control-sm">
            <option value="">全部</option>
            <option value="high">高</option>
            <option value="medium">中</option>
            <option value="low">低</option>
          </select>
        </div>
      </div>
      <div class="stats">
        <span class="stat-item">总计: {{ totalTodos }}</span>
        <span class="stat-item in-progress">进行中: {{ inProgressTodos }}</span>
        <span class="stat-item completed">已完成: {{ completedTodos }}</span>
      </div>
    </div>

    <!-- 待办事项列表 -->
    <div class="todo-list">
      <div v-if="filteredTodos.length === 0" class="empty-state">
        <i class="bi bi-inbox"></i>
        <p>暂无待办事项</p>
      </div>
      
      <div 
        v-for="todo in filteredTodos" 
        :key="todo.id" 
        class="todo-item"
        :class="{ 
          'completed': todo.status === 'completed',
          'overdue': isOverdue(todo.dueDate) && todo.status !== 'completed'
        }"
      >
        <div class="todo-content">
          <div class="todo-main">
            <div class="todo-checkbox">
              <input 
                type="checkbox" 
                :checked="todo.status === 'completed'"
                @change="toggleTodoStatus(todo)"
                class="form-check-input"
              >
            </div>
            <div class="todo-info">
              <div class="todo-text" :class="{ 'completed-text': todo.status === 'completed' }">
                {{ todo.content }}
              </div>
              <div class="todo-meta">
                <span class="assignee" :class="'assignee-' + getAssigneeColorClass(todo.assignee)">
                  <i class="bi bi-person"></i> {{ todo.assignee }}
                </span>
                <span class="priority" :class="'priority-' + todo.priority">
                  <i class="bi bi-flag"></i> {{ getPriorityText(todo.priority) }}
                </span>
                <span class="status" :class="'status-' + todo.status">
                  <i class="bi" :class="getStatusIcon(todo.status)"></i> 
                  {{ getStatusText(todo.status) }}
                </span>
                <span v-if="todo.dueDate" class="due-date" :class="{ 'overdue': isOverdue(todo.dueDate) && todo.status !== 'completed' }">
                  <i class="bi bi-calendar"></i> {{ formatDate(todo.dueDate) }}
                </span>
                <span class="created-time">
                  <i class="bi bi-clock"></i> {{ formatDateTime(todo.createdAt) }}
                </span>
              </div>
            </div>
          </div>
          <div class="todo-actions">
            <button 
              @click="editTodo(todo)" 
              class="btn btn-sm btn-outline-primary"
              title="编辑"
            >
              <i class="bi bi-pencil"></i>
            </button>
            <button 
              @click="updateTodoStatus(todo)" 
              class="btn btn-sm btn-outline-success"
              title="更新状态"
            >
              <i class="bi bi-arrow-repeat"></i>
            </button>
            <button 
              @click="deleteTodo(todo.id)" 
              class="btn btn-sm btn-outline-danger"
              title="删除"
            >
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑模态框 -->
    <div class="modal" v-if="editingTodo" @click.self="cancelEdit">
      <div class="modal-content">
        <div class="modal-header">
          <h5>编辑待办事项</h5>
          <button @click="cancelEdit" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>任务内容</label>
            <input 
              type="text" 
              v-model="editingTodo.content" 
              class="form-control"
            >
          </div>
          <div class="form-group">
            <label>添加人</label>
            <select v-model="editingTodo.assignee" class="form-control">
              <option v-for="user in users" :key="user" :value="user">{{ user }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>优先级</label>
            <select v-model="editingTodo.priority" class="form-control">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="editingTodo.status" class="form-control">
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          <div class="form-group">
            <label>截止日期</label>
            <input 
              type="date" 
              v-model="editingTodo.dueDate" 
              class="form-control"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button @click="cancelEdit" class="btn btn-secondary">取消</button>
          <button @click="saveEdit" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TodoList',
  data() {
    return {
      users: ['孙航', '李彦燕', '陈玉忠', '孔源博', '新用户1', '新用户2'],
      newTodo: {
        content: '',
        assignee: '',
        priority: 'medium',
        dueDate: ''
      },
      todos: [],
      editingTodo: null,
      filterStatus: '',
      filterAssignee: '',
      filterPriority: '',
      loading: false,
      error: null
    }
  },
  computed: {
    filteredTodos() {
      return this.todos.filter(todo => {
        const statusMatch = !this.filterStatus || todo.status === this.filterStatus
        const assigneeMatch = !this.filterAssignee || todo.assignee === this.filterAssignee
        const priorityMatch = !this.filterPriority || todo.priority === this.filterPriority
        return statusMatch && assigneeMatch && priorityMatch
      }).sort((a, b) => {
        // 优先级排序：高 > 中 > 低
        const priorityOrder = { high: 3, medium: 2, low: 1 }
        if (priorityOrder[b.priority] !== priorityOrder[a.priority]) {
          return priorityOrder[b.priority] - priorityOrder[a.priority]
        }
        // 状态排序：进行中 > 已完成
        const statusOrder = { in_progress: 2, completed: 1 }
        if (statusOrder[b.status] !== statusOrder[a.status]) {
          return statusOrder[b.status] - statusOrder[a.status]
        }
        // 创建时间排序：新的在前
        return new Date(b.createdAt) - new Date(a.createdAt)
      })
    },
    totalTodos() {
      return this.todos.length
    },
    inProgressTodos() {
      return this.todos.filter(todo => todo.status === 'in_progress').length
    },
    completedTodos() {
      return this.todos.filter(todo => todo.status === 'completed').length
    }
  },
  mounted() {
    this.fetchTodos()
  },
  methods: {
    async addTodo() {
      if (!this.newTodo.content.trim()) {
        alert('请输入待办事项内容')
        return
      }
      if (!this.newTodo.assignee) {
        alert('请选择添加人')
        return
      }

      this.loading = true
      try {
        const response = await axios.post('/api/todos/', {
          content: this.newTodo.content.trim(),
          assignee: this.newTodo.assignee,
          priority: this.newTodo.priority,
          dueDate: this.newTodo.dueDate || null
        })
        
        if (response.data.success) {
          // 重新获取列表
          await this.fetchTodos()
          
          // 重置表单
          this.newTodo = {
            content: '',
            assignee: '',
            priority: 'medium',
            dueDate: ''
          }
        } else {
          alert(response.data.error || '添加失败')
        }
      } catch (error) {
        console.error('添加待办事项失败:', error)
        alert('添加失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    async deleteTodo(id) {
      if (confirm('确定要删除这个待办事项吗？')) {
        this.loading = true
        try {
          const response = await axios.delete(`/api/todos/${id}/`)
          
          if (response.data.success) {
            // 重新获取列表
            await this.fetchTodos()
          } else {
            alert(response.data.error || '删除失败')
          }
        } catch (error) {
          console.error('删除待办事项失败:', error)
          alert('删除失败，请稍后重试')
        } finally {
          this.loading = false
        }
      }
    },
    editTodo(todo) {
      this.editingTodo = { ...todo }
    },
    cancelEdit() {
      this.editingTodo = null
    },
    async saveEdit() {
      if (!this.editingTodo.content.trim()) {
        alert('请输入待办事项内容')
        return
      }

      this.loading = true
      try {
        const response = await axios.put(`/api/todos/${this.editingTodo.id}/`, {
          content: this.editingTodo.content.trim(),
          assignee: this.editingTodo.assignee,
          priority: this.editingTodo.priority,
          status: this.editingTodo.status,
          dueDate: this.editingTodo.dueDate || null
        })
        
        if (response.data.success) {
          // 重新获取列表
          await this.fetchTodos()
          this.editingTodo = null
        } else {
          alert(response.data.error || '更新失败')
        }
      } catch (error) {
        console.error('更新待办事项失败:', error)
        alert('更新失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    async toggleTodoStatus(todo) {
      const newStatus = todo.status === 'completed' ? 'in_progress' : 'completed'
      await this.updateTodoStatusById(todo.id, newStatus)
    },
    async updateTodoStatus(todo) {
      const newStatus = todo.status === 'completed' ? 'in_progress' : 'completed'
      await this.updateTodoStatusById(todo.id, newStatus)
    },
    async updateTodoStatusById(id, status) {
      this.loading = true
      try {
        const response = await axios.patch(`/api/todos/${id}/status/`, {
          status: status
        })
        
        if (response.data.success) {
          // 重新获取列表
          await this.fetchTodos()
        } else {
          alert(response.data.error || '状态更新失败')
        }
      } catch (error) {
        console.error('更新状态失败:', error)
        alert('状态更新失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    getPriorityText(priority) {
      const priorityMap = {
        high: '高',
        medium: '中',
        low: '低'
      }
      return priorityMap[priority] || priority
    },
    getStatusText(status) {
      const statusMap = {
        in_progress: '进行中',
        completed: '已完成'
      }
      return statusMap[status] || status
    },
    getStatusIcon(status) {
      const iconMap = {
        in_progress: 'bi-arrow-repeat',
        completed: 'bi-check-circle'
      }
      return iconMap[status] || 'bi-circle'
    },
    getAssigneeColorClass(assignee) {
      const colorMap = {
        '孙航': 'sunhang',
        '李彦燕': 'liyanyan',
        '陈玉忠': 'chenyuzhong',
        '孔源博': 'kongyuanbo',
        '新用户1': 'newuser1',
        '新用户2': 'newuser2'
      }
      return colorMap[assignee] || 'default'
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    isOverdue(dueDate) {
      if (!dueDate) return false
      const today = new Date()
      const due = new Date(dueDate)
      return due < today
    },
    async fetchTodos() {
      this.loading = true
      this.error = null
      
      try {
        const params = new URLSearchParams()
        if (this.filterStatus) params.append('status', this.filterStatus)
        if (this.filterAssignee) params.append('assignee', this.filterAssignee)
        if (this.filterPriority) params.append('priority', this.filterPriority)
        
        const response = await axios.get(`/api/todos/?${params.toString()}`)
        
        if (response.data.success) {
          this.todos = response.data.data
        } else {
          this.error = response.data.error || '获取数据失败'
        }
      } catch (error) {
        console.error('获取待办事项失败:', error)
        this.error = '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.todo-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  margin-left: 250px; /* 默认侧边栏宽度 */
  transition: margin-left 0.3s ease;
}

.todo-header {
  text-align: center;
  margin-bottom: 30px;
}

.todo-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 16px;
}

.add-todo-section {
  background: #f8f9fa;
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 30px;
  border: 1px solid #e9ecef;
}

.form-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 5px;
  color: #495057;
}

.form-control {
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 5px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.add-btn {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-btn:hover {
  background: #0056b3;
  transform: translateY(-1px);
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.filter-controls {
  display: flex;
  gap: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 600;
  color: #495057;
}

.form-control-sm {
  padding: 5px 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 13px;
}

.stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 13px;
  font-weight: 600;
  background: #e9ecef;
  color: #495057;
}

.stat-item.in-progress {
  background: #d1ecf1;
  color: #0c5460;
}

.stat-item.completed {
  background: #d4edda;
  color: #155724;
}

.todo-list {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 15px;
}

.todo-item {
  border-bottom: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.todo-item:hover {
  background: #f8f9fa;
}

.todo-item.completed {
  opacity: 0.7;
  background: #f8f9fa;
}

.todo-item.overdue {
  border-left: 4px solid #dc3545;
  background: #fff5f5;
}

.todo-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
}

.todo-main {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  flex: 1;
}

.todo-checkbox input {
  transform: scale(1.2);
}

.todo-info {
  flex: 1;
}

.todo-text {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
  line-height: 1.4;
}

.completed-text {
  text-decoration: line-through;
  color: #6c757d;
}

.todo-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  font-size: 13px;
}

.todo-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #f8f9fa;
  color: #495057;
}

.assignee {
  font-weight: 600;
}

.assignee.assignee-sunhang {
  background: #e3f2fd !important;
  color: #1565c0 !important;
}

.assignee.assignee-liyanyan {
  background: #f3e5f5 !important;
  color: #7b1fa2 !important;
}

.assignee.assignee-chenyuzhong {
  background: #e8f5e8 !important;
  color: #2e7d32 !important;
}

.assignee.assignee-kongyuanbo {
  background: #fff3e0 !important;
  color: #ef6c00 !important;
}

.assignee.assignee-newuser1 {
  background: #ffebee !important;
  color: #c62828 !important;
}

.assignee.assignee-newuser2 {
  background: #f1f8e9 !important;
  color: #558b2f !important;
}

.assignee.assignee-default {
  background: #f5f5f5 !important;
  color: #616161 !important;
}

.priority-high {
  background: #ffebee;
  color: #c62828;
}

.priority-medium {
  background: #fff3e0;
  color: #ef6c00;
}

.priority-low {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-in_progress {
  background: #d1ecf1;
  color: #0c5460;
}

.status-completed {
  background: #d4edda;
  color: #155724;
}

.due-date.overdue {
  background: #ffebee;
  color: #c62828;
  font-weight: 600;
}

.todo-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: 1px solid;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.btn-sm {
  padding: 4px 8px;
}

.btn-outline-primary {
  color: #007bff;
  border-color: #007bff;
  background: transparent;
}

.btn-outline-primary:hover {
  background: #007bff;
  color: white;
}

.btn-outline-success {
  color: #28a745;
  border-color: #28a745;
  background: transparent;
}

.btn-outline-success:hover {
  background: #28a745;
  color: white;
}

.btn-outline-danger {
  color: #dc3545;
  border-color: #dc3545;
  background: transparent;
}

.btn-outline-danger:hover {
  background: #dc3545;
  color: white;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h5 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
}

.modal-body {
  padding: 20px;
}

.modal-body .form-group {
  margin-bottom: 15px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e9ecef;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
}

.btn-primary {
  background: #007bff;
  color: white;
  border: none;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .todo-container {
    margin-left: 220px; /* 中等屏幕 */
  }
}

@media (max-width: 992px) {
  .todo-container {
    margin-left: 200px; /* 小屏幕 */
  }
}

@media (max-width: 768px) {
  .todo-container {
    margin-left: 70px; /* 移动端图标模式 */
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .filter-controls {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .stats {
    flex-direction: column;
    gap: 5px;
  }
  
  .todo-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .todo-actions {
    align-self: flex-end;
  }
}

@media (max-width: 576px) {
  .todo-container {
    margin-left: 60px; /* 超小屏幕 */
  }
}
</style>
