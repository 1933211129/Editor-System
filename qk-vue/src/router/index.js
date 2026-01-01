import { createRouter, createWebHistory } from 'vue-router'
import JournalProgress from '../components/JournalProgress.vue'
import ArticleSchedule from '../components/ArticleSchedule.vue'
import NotificationGenerator from '../components/notification/NotificationGenerator.vue'
import WechatArticle from '../components/WechatArticle.vue'
import EmailManage from '../components/EmailManage.vue'
import EmailMailMerge from '@/components/email/MailMerge.vue'
import ReferenceCheck from '../components/GrammarCheck.vue'
import EmailSenderDemo from '@/components/demo/EmailSenderDemo.vue'
import LoginPage from '../components/auth/LoginPage.vue'
import InvoiceManage from '@/components/invoice/InvoiceManage.vue'
import ContactsManage from '@/components/contacts/ContactsManage.vue'
import ReviewersManage from '@/components/reviewers/ReviewersManage.vue'
import TodoList from '@/components/TodoList.vue'
import ProgressHistory from '@/components/ProgressHistory.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/progress',
    name: 'progress',
    component: JournalProgress
  },
  {
    path: '/progress-history',
    name: 'progress-history',
    component: ProgressHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: ArticleSchedule
  },
  {
    path: '/wechat',
    name: 'wechat',
    component: WechatArticle
  },
  {
    path: '/email',
    name: 'email',
    component: EmailManage
  },
  {
    path: '/reference',
    name: 'reference',
    component: ReferenceCheck
  },
  {
    path: '/invoice',
    name: 'Invoice',
    component: InvoiceManage,
    meta: { requiresAuth: true }
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: ContactsManage,
    meta: { requiresAuth: true }
  },
  {
    path: '/reviewers',
    name: 'Reviewers',
    component: ReviewersManage,
    meta: { requiresAuth: true }
  },
  {
    path: '/notification',
    name: 'Notification',
    component: NotificationGenerator,
    meta: { requiresAuth: true }
  },
  {
    path: '/todos',
    name: 'Todos',
    component: TodoList,
    meta: { requiresAuth: true }
  }
  ,
  {
    path: '/demo/email-mail-merge',
    name: 'EmailMailMerge',
    component: EmailMailMerge,
    meta: { requiresAuth: false }
  }
  ,
  {
    path: '/demo/email-sender',
    name: 'EmailSenderDemo',
    component: EmailSenderDemo,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory('/xuebao/'),
  routes
})

// 路由守卫：除登录页外其余页面都需要登录
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isLoginPage = to.path === '/login'

  // 未登录，且目标不是登录页 -> 跳转登录并记录来源
  if (!token && !isLoginPage) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // 已登录，访问登录页 -> 跳转到默认首页
  if (token && isLoginPage) {
    return next('/progress')
  }

  next()
})

export default router 