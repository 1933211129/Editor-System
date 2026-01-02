# 期刊管理系统

一个基于 Django + Vue 3 的期刊文章管理与办公自动化系统，用于管理期刊文章的编辑流程、邮件发送、发票管理、联系人管理等业务。

## 📋 项目简介

本系统是一个面向期刊编辑部的综合管理平台，提供了从文章进度跟踪、邮件批量发送、发票管理到联系人维护等全方位的功能支持。系统采用前后端分离架构，后端使用 Django REST Framework 提供 API 服务，前端使用 Vue 3 + Vite 构建现代化的用户界面。

## 🏗️ 项目结构

```
BJ/
├── qk/                    # Django 后端项目
│   ├── qk/               # Django 项目配置
│   │   ├── settings.py   # 项目设置
│   │   ├── urls.py       # 主路由配置
│   │   └── ...
│   ├── qikan/            # 主应用模块
│   │   ├── models.py     # 数据模型
│   │   ├── views.py      # 视图函数
│   │   ├── urls.py       # 应用路由
│   │   ├── serializers.py # 序列化器
│   │   ├── templates/    # Word 模板文件
│   │   └── ...
│   ├── manage.py         # Django 管理脚本
│   └── db.sqlite3        # SQLite 数据库（开发环境）
│
└── qk-vue/               # Vue 3 前端项目
    ├── src/
    │   ├── components/   # Vue 组件
    │   │   ├── journal/  # 期刊相关组件
    │   │   ├── email/    # 邮件相关组件
    │   │   ├── invoice/  # 发票相关组件
    │   │   ├── contacts/ # 联系人相关组件
    │   │   └── ...
    │   ├── router/       # 路由配置
    │   ├── App.vue       # 根组件
    │   └── main.js       # 入口文件
    ├── package.json      # 前端依赖配置
    └── vite.config.js    # Vite 构建配置
```

## ✨ 核心功能

### 1. 期刊文章进度管理
- **多期数管理**：支持管理 5 个期数的文章进度，可灵活映射到 1-12 期的显示期数
- **进度跟踪**：记录文章的责编、校对编辑、校对时间、版面费等信息
- **版次管理**：支持批量更新文章版次信息
- **历史记录**：自动归档清空前的进度数据，支持查看历史记录

### 2. 文章预排期管理
- 文章排期计划管理
- 排期确认状态跟踪
- 支持 Excel 导入/导出

### 3. 发票管理
- 发票信息录入与编辑
- 发票类型、标签分类管理
- 支付方式、支付日期记录
- 支持批量导入/导出 Excel 数据

### 4. 邮件批量发送
- **批量发送**：支持向多个收件人批量发送邮件
- **模板管理**：创建、编辑、删除邮件模板（HTML 格式）
- **数据驱动模板**：支持邮件合并功能，使用模板变量动态生成个性化邮件
- **收件人管理**：联系人分组管理，支持多分组关联
- **历史记录**：查看邮件发送历史

### 5. 联系人管理
- **作者通讯录**：管理作者的联系信息（姓名、邮箱、地址、邮编等）
- **联系人分组**：支持创建分组，联系人可属于多个分组
- **批量操作**：支持批量导入、批量删除、批量更新分组

### 6. 责编管理
- 责编信息管理（姓名、工作单位、身份证号、银行卡信息等）
- 按年份和期次组织责编数据
- 稿费计算（应发、税金、实发）

### 7. 待办事项管理
- 任务创建、编辑、删除
- 优先级设置（低、中、高）
- 状态跟踪（进行中、已完成）
- 截止日期管理
- 按添加人分类

### 8. 通知文件生成
- 基于 Word 模板生成通知文件
- 支持录用通知、收费通知等模板
- 批量生成 PDF 文件

### 9. 参考文献纠错
- 参考文献格式检查与纠错功能

### 10. 公众号文章生成
- 生成微信公众号文章内容

## 🛠️ 技术栈

### 后端技术
- **框架**：Django 4.2.13
- **API**：Django REST Framework
- **数据库**：MySQL（生产环境）/ SQLite（开发环境）
- **其他**：
  - `python-docx`：Word 文档处理
  - `docxtpl`：Word 模板渲染
  - `django-cors-headers`：跨域支持
  - `python-dotenv`：环境变量管理

### 前端技术
- **框架**：Vue 3.2.13
- **构建工具**：Vite 5.0
- **路由**：Vue Router 4.5
- **UI 框架**：Bootstrap 5.3.3
- **图标**：Bootstrap Icons
- **HTTP 客户端**：Axios 1.8.4
- **富文本编辑器**：TinyMCE
- **其他**：
  - `docx`：Word 文档处理
  - `mammoth`：Word 转 HTML
  - `xlsx`：Excel 文件处理
  - `vuedraggable`：拖拽排序

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+（生产环境）

### 后端部署

1. **进入后端目录**
```bash
cd qk
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install django==4.2.13
pip install djangorestframework
pip install django-cors-headers
pip install python-dotenv
pip install mysql-connector-python
pip install python-docx
pip install docxtpl
```

4. **配置环境变量**
在 `qk/` 目录下创建 `.env` 文件：
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=mysql.connector.django
DB_NAME=db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

5. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **创建超级用户（可选）**
```bash
python manage.py createsuperuser
```

7. **启动开发服务器**
```bash
python manage.py runserver
```
后端服务将在 `http://localhost:8000` 启动

### 前端部署

1. **进入前端目录**
```bash
cd qk-vue
```

2. **安装依赖**
```bash
npm install
```

3. **启动开发服务器**
```bash
npm run dev
```
前端服务将在 `http://localhost:8080` 启动

4. **构建生产版本**
```bash
npm run build
```
构建产物将输出到 `dist/` 目录

## 📡 API 接口说明

系统提供 RESTful API 接口，主要接口包括：

### 认证相关
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/register/` - 用户注册

### 期刊管理
- `GET /api/journal/<period>/data/` - 获取指定期数数据
- `POST /api/journal/<period>/create/` - 创建期刊记录
- `PUT /api/journal/<period>/update/` - 更新期刊字段
- `DELETE /api/journal/<period>/delete/` - 删除期刊记录
- `POST /api/journal/<period>/clear/` - 清空期刊数据
- `GET /api/journal/period-mapping/` - 获取期数映射

### 发票管理
- `GET /api/invoice/data/` - 获取发票数据
- `POST /api/invoice/create/` - 创建发票
- `PUT /api/invoice/update/` - 更新发票
- `DELETE /api/invoice/delete/` - 删除发票
- `POST /api/invoice/import/` - 导入发票数据

### 邮件管理
- `POST /api/email/send-bulk/` - 批量发送邮件
- `GET /api/email/history/` - 获取邮件历史
- `GET /api/email-templates/` - 获取邮件模板列表
- `POST /api/email-templates/create/` - 创建邮件模板
- `PUT /api/email-templates/<id>/update/` - 更新邮件模板

### 联系人管理
- `GET /api/recipients/` - 获取联系人列表
- `POST /api/recipients/create/` - 创建联系人
- `PUT /api/recipients/<id>/update/` - 更新联系人
- `DELETE /api/recipients/<id>/delete/` - 删除联系人
- `POST /api/recipients/import/` - 导入联系人

更多接口详情请参考 `qk/qikan/urls.py` 文件。

## 📁 数据模型

主要数据模型包括：

- **JournalPeriodBase**：期刊文章进度基类（抽象模型）
  - `JournalPeriodOne` ~ `JournalPeriodFive`：5 个期数的具体模型
- **Invoice**：发票信息
- **ArticleSchedule**：文章排期
- **Contact**：作者通讯录
- **Reviewer**：责编信息
- **Todo**：待办事项
- **EmailTemplate**：邮件模板
- **Recipient**：收件人
- **RecipientGroup**：收件人分组
- **JournalProgressSummary**：期刊进度汇总（历史记录）

详细模型定义请参考 `qk/qikan/models.py` 文件。

## 🔒 安全配置

### 生产环境注意事项

1. **修改 SECRET_KEY**：在 `.env` 文件中设置强密码
2. **关闭 DEBUG**：设置 `DEBUG=False`
3. **配置 ALLOWED_HOSTS**：在 `settings.py` 中设置允许的主机
4. **数据库安全**：使用强密码，限制数据库访问权限
5. **HTTPS**：生产环境建议使用 HTTPS
6. **CORS 配置**：限制允许的跨域来源

## 📝 开发说明

### 代码规范
- 后端遵循 PEP 8 Python 代码规范
- 前端使用 ESLint 进行代码检查
- 使用中文注释和文档字符串

### 数据库迁移
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate
```

### 静态文件
前端构建后，将 `dist/` 目录内容部署到 Web 服务器，或配置 Django 静态文件服务。

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目为内部使用项目，版权归项目所有者所有。

## 👥 维护者

项目维护团队

## 📞 联系方式

如有问题或建议，请联系项目维护团队。

---

**最后更新**：2026年1月2日

