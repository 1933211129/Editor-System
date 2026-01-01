<template>
    <div class="body">
      <div class="main-box">
        <div :class="['container', 'container-register', { 'is-txl': isLogin }]">
          <form @submit.prevent="handleRegister">
            <h2 class="title">注册</h2>
            <span class="text"></span>
            <div class="input-group">
              <span class="input-icon">👤</span>
              <input 
                class="form__input" 
                type="text" 
                v-model="registerForm.username" 
                placeholder="请输入用户名"
                required
              />
            </div>
            <div class="input-group">
              <span class="input-icon">📧</span>
              <input 
                class="form__input" 
                type="email" 
                v-model="registerForm.email" 
                placeholder="请输入邮箱"
                required
              />
            </div>
            <div class="input-group">
              <span class="input-icon">🔒</span>
              <input 
                class="form__input" 
                type="password" 
                v-model="registerForm.password" 
                placeholder="请输入密码"
                required
              />
            </div>
            <div class="input-group">
              <span class="input-icon">🔐</span>
              <input 
                class="form__input" 
                type="password" 
                v-model="registerForm.confirmPassword" 
                placeholder="确认密码"
                @input="validatePassword"
                required
              />
            </div>
            <p class="error-text" v-if="passwordError">{{ passwordError }}</p>
            <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
            <div class="form__button" @click="validateAndRegister">立即注册</div>
          </form>
        </div>
        <div :class="['container', 'container-login', { 'is-txl is-z200': isLogin }]">
          <form @submit.prevent="handleLogin">
            <h2 class="title">登录</h2>
            <span class="text"></span>
            <div class="input-group">
              <span class="input-icon">👤</span>
              <input 
                class="form__input" 
                type="email" 
                v-model="loginForm.username" 
                placeholder="邮箱"
                required
              />
            </div>
            <div class="input-group">
              <span class="input-icon">🔒</span>
              <input 
                class="form__input" 
                type="password" 
                v-model="loginForm.password" 
                placeholder="请输入密码"
                required
              />
            </div>
            <div class="form__button" @click="validateAndLogin">立即登录</div>
          </form>
        </div>
        <div :class="['switch', { 'login': isLogin }]">
          <div class="switch__circle"></div>
          <div class="switch__circle switch__circle_top"></div>
          <div class="switch__container">
            <h2>{{ isLogin ? '用户注册' : '欢迎回来 !' }}</h2>
            <p>
              {{
                isLogin
                    ? '如果您还没有账号，请点击下方立即注册按钮进行账号注册'
                    : '如果您已经注册过账号，请点击下方立即登录按钮进行登录'
              }}
            </p>
            <div class="form__button" @click="isLogin = !isLogin">
              {{ isLogin ? '立即注册' : '立即登录' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { emitter } from '../SideBar.vue'  // 导入事件总线

  export default {
    name: 'LoginPage',
    data() {
      return {
        isLogin: true,
        passwordError: '',
        loginForm: {
          username: '',  // 用作email
          password: '',
        },
        registerForm: {
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
        },
        errorMessage: ''  // 添加错误消息
      }
    },
    methods: {
      validatePassword() {
        if (this.registerForm.password !== this.registerForm.confirmPassword) {
          this.passwordError = '两次输入的密码不一致';
        } else {
          this.passwordError = '';
        }
      },
      validateAndLogin() {
        if (!this.loginForm.username || !this.loginForm.password) {
          alert('请填写所有登录信息！');
          return;
        }
        this.handleLogin();
      },
      validateAndRegister() {
        if (!this.registerForm.username || !this.registerForm.email || 
            !this.registerForm.password || !this.registerForm.confirmPassword) {
          alert('请填写所有注册信息！');
          return;
        }
        if (this.registerForm.password !== this.registerForm.confirmPassword) {
          alert('两次输入的密码不一致！');
          return;
        }
        this.handleRegister();
      },
      async handleLogin() {
        try {
          const response = await axios.post('/api/auth/login/', {
            username: this.loginForm.username,
            password: this.loginForm.password
          });
          
          if (response.data.status === 'success') {
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('username', response.data.username);
            // 触发登录成功事件
            emitter.emit('loginSuccess')
            const redirectPath = this.$route.query.redirect || '/progress'
            this.$router.replace(redirectPath)
          } else {
            alert(response.data.message || '登录失败！');
          }
        } catch (error) {
          console.error('登录错误:', error.response || error);
          alert(error.response?.data?.message || '登录失败，请稍后重试');
        }
      },
      async handleRegister() {
        try {
          const response = await axios.post('/api/auth/register/', {
              username: this.registerForm.username,
              email: this.registerForm.email,
              password: this.registerForm.password
          });
          
          console.log('注册响应:', response.data);
          
          if (response.data.status === 'success') {
            alert('注册成功！请登录');
            this.isLogin = true;
            this.loginForm.username = this.registerForm.email;
            this.loginForm.password = this.registerForm.password;
          } else {
            alert(response.data.message || '注册失败！');
          }
        } catch (error) {
          console.error('注册错误:', error.response || error);
          alert(error.response?.data?.message || '注册失败，请稍后重试');
        }
      }
    },
  }
  </script>
  
  <style lang="scss" scoped>
  .body {
    width: calc(100vw - 250px);  /* 保持宽度减去导航栏宽度 */
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: "Montserrat", sans-serif;
    font-size: 12px;
    background-color: #f8f9fa;
    background-size: cover;
    background-position: center;
    color: #a0a5a8;
    margin-left: 250px;  /* 修改这里：添加左边距，与导航栏宽度相同 */
    margin-top: -30px;
  }

  .main-box {
    position: relative;
    width: 1000px;  /* 固定宽度，不用百分比 */
    height: 600px;  /* 固定高度，不用视窗高度 */
    padding: 25px;
    background-color: #ecf0f3;
    box-shadow: 1px 1px 100px 10px #ecf0f3;
    border-radius: 12px;
    overflow: hidden;
  }
  
    .container {
      display: flex;
      justify-content: center;
      align-items: center;
      position: absolute;
      top: 0;
      width: 50%;        /* 调整为相对宽度 */
      height: 100%;
      padding: 25px;
      background-color: #ecf0f3;
      transition: all 1.25s;
  
      form {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        width: 100%;
        height: 100%;
        color: #a0a5a8;
  
        .form__icon {
          object-fit: contain;
          width: 30px;
          margin: 0 5px;
          opacity: .5;
          transition: .15s;
  
          &:hover {
            opacity: 1;
            transition: .15s;
            cursor: pointer;
  
          }
        }
  
        .title {
          font-size: 34px;
          font-weight: 700;
          line-height: 3;
          color: #181818;
        }
  
        .text {
          margin-top: 30px;
          margin-bottom: 12px;
        }
  
        .form__input {
          width: 100% !important;  /* 确保宽度填满父容器 */
          height: 50px !important;  /* 增加高度 */
          padding-left: 45px !important;  /* 为更大的图标留出空间 */
          font-size: 16px !important;  /* 增加字体大小 */
          letter-spacing: 0.15px;
          border: none;
          outline: none;
          background-color: #ecf0f3;
          transition: 0.25s ease;
          border-radius: 12px;  /* 稍微增加圆角 */
          box-shadow: inset 2px 2px 4px #d1d9e6, inset -2px -2px 4px #f9f9f9;
  
          &::placeholder {
            color: #a0a5a8;
            font-size: 16px;  /* 增加占位符字体大小 */
          }
        }
      }
    }
  
    .container-register {
      z-index: 100;
      left: calc(100% - 600px);
    }
  
    .container-login {
      left: calc(100% - 600px);
      z-index: 0;

    }
  
    .is-txl {
      left: 0;
      transition: 1.25s;
      transform-origin: right;
    }
  
    .is-z200 {
      z-index: 200;
      transition: 1.25s;
    }
  
    .switch {
      display: flex;
      justify-content: center;
      align-items: center;
      position: absolute;
      top: 0;
      left: 0;
      height: 100%;
      width: 40% !important;  /* 调整切换区域宽度 */
      padding: 50px;
      z-index: 200;
      transition: 1.25s;
      background-color: #ecf0f3;
      overflow: hidden;
      box-shadow: 4px 4px 10px #d1d9e6, -4px -4px 10px #f9f9f9;
      color: #a0a5a8;
  
      .switch__circle {
        position: absolute;
        width: 500px;
        height: 500px;
        border-radius: 50%;
        background-color: #ecf0f3;
        box-shadow: inset 8px 8px 12px #d1d9e6, inset -8px -8px 12px #f9f9f9;
        bottom: -60%;
        left: -60%;
        transition: 1.25s;
      }
  
      .switch__circle_top {
        top: -30%;
        left: 60%;
        width: 300px;
        height: 300px;
      }
  
      .switch__container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        position: absolute;
        width: 400px;
        padding: 50px 55px;
        transition: 1.25s;
  
        h2 {
          font-size: 34px;
          font-weight: 700;
          line-height: 3;
          color: #181818;
        }
  
        p {
          font-size: 14px;
          letter-spacing: 0.25px;
          text-align: center;
          line-height: 1.6;
        }
      }
    }
  
    .login {
      left: calc(100% - 400px);
  
      .switch__circle {
        left: 0;
      }
    }
  
    .form__button {
      width: 180px;
      height: 50px;
      border-radius: 25px;
      margin-top: 50px;
      text-align: center;
      line-height: 50px;
      font-size: 14px;
      letter-spacing: 2px;
      background-color: #4b70e2;
      color: #f9f9f9;
      cursor: pointer;
      box-shadow: 8px 8px 16px #d1d9e6, -8px -8px 16px #f9f9f9;
  
      &:hover {
        box-shadow: 2px 2px 3px 0 rgba(255, 255, 255, 50%),
        -2px -2px 3px 0 rgba(116, 125, 136, 50%),
        inset -2px -2px 3px 0 rgba(255, 255, 255, 20%),
        inset 2px 2px 3px 0 rgba(0, 0, 0, 30%);
    }
  }
  
  /* 调整响应式设计 */
  @media (max-width: 1400px) {
    .main-box {
      width: 900px;  /* 较小屏幕时稍微减小宽度 */
      height: 550px;
    }
  }

  @media (max-width: 1200px) {
    .main-box {
      width: 800px;
      height: 500px;
    }
  }
  
  .input-group {
    position: relative;
    width: 450px;  /* 增加宽度 */
    margin: 8px 0;  /* 增加垂直间距 */
  }
  
  .input-icon {
    position: absolute;
    left: 15px;  /* 稍微调整图标位置 */
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;  /* 增加图标大小 */
    color: #95a5a6;
    z-index: 1;
  }
  
  .form__input {
    padding-left: 45px !important;  /* 为更大的图标留出空间 */
  }
  
  .error-text {
    color: #e74c3c;
    font-size: 12px;
    margin-top: 5px;
  }
  
  /* 添加错误消息样式 */
  .error-message {
    color: #e74c3c;
    font-size: 14px;
    margin-top: 10px;
    text-align: center;
  }
  </style>
  
  