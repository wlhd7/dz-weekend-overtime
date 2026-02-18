# 周末加班管理系统 - 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品简介
周末加班管理系统是一个基于Web的企业级应用，用于统一管理企业各部门的周末加班人员安排和状态跟踪。系统支持多部门隔离管理，提供直观的界面进行加班人员状态设置、预设内容管理和实时数据查看。采用现代化的前后端分离架构，提供更好的用户体验和可维护性。

### 1.2 产品目标
- 提高加班管理效率，减少人工统计工作量
- 实现加班信息的标准化和规范化管理
- 提供实时的加班状态查看和统计功能
- 支持多部门独立管理，确保数据安全隔离
- 采用现代技术栈，确保系统可维护性和扩展性

### 1.3 目标用户
- **部门管理员**：负责管理本部门员工的加班安排
- **企业管理员**：查看全公司加班统计信息
- **员工**：查看个人加班安排（通过信息页面）

## 2. 用户角色与权限

### 2.1 部门管理员
- 选择并切换管理部门
- 添加/删除本部门员工
- 设置员工加班状态（正常加班/出差）
- 管理本部门的预设内容
- 查看本部门加班统计信息

### 2.2 系统访问者
- 查看全公司加班统计信息
- 按部门查看加班人员名单
- 区分正常加班和出差人员

## 3. 功能需求详述

### 3.1 部门管理模块

#### 3.1.1 部门选择
- **功能描述**：用户首次访问时需选择所属部门
- **业务规则**：
  - 部门信息存储在Cookie中，有效期1年
  - 支持部门间切换
  - 无效部门自动重定向到选择页面

#### 3.1.2 子部门支持
- **功能描述**：支持部门下的班组/子部门管理
- **业务规则**：
  - 员工可归属到具体子部门
  - 子部门信息在员工管理中显示

### 3.2 员工管理模块

#### 3.2.1 员工添加
- **功能描述**：向当前部门添加新员工
- **业务规则**：
  - 员工姓名在系统内唯一
  - 可选择归属子部门
  - 重复添加时自动更新部门归属

#### 3.2.2 员工删除
- **功能描述**：从当前部门移除员工
- **业务规则**：
  - 仅删除当前部门的员工记录
  - 清除相关的加班状态记录

### 3.3 加班状态管理模块

#### 3.3.1 状态类型
- **bg-1（默认）**：无加班
- **bg-2（正常加班）**：公司内加班
- **bg-3（出差）**：外出出差

#### 3.3.2 状态切换
- **功能描述**：通过API实时切换员工加班状态
- **业务规则**：
  - 支持批量操作（全部设为正常加班/出差）
  - 支持一键清空所有加班状态
  - 状态变更实时保存到数据库

#### 3.3.3 日期管理
- **功能描述**：分别管理周六和周日的加班安排
- **业务规则**：
  - 支持日期切换查看
  - 每个员工每天只能有一种状态

### 3.4 统计查看模块

#### 3.4.1 实时统计
- **功能描述**：按部门显示当前加班人员名单
- **业务规则**：
  - 区分周六和周日统计
  - 分别显示正常加班和出差人员
  - 按部门分组显示

#### 3.4.2 数据展示
- **功能描述**：以列表形式展示加班人员信息
- **业务规则**：
  - 支持多部门同时查看
  - 人员姓名按部门排序显示

## 4. 业务流程

### 4.1 部门管理员工作流程

```mermaid
graph TD
    A[访问系统] --> B{是否有部门Cookie}
    B -->|否| C[选择部门]
    B -->|是| D[进入管理界面]
    C --> D
    D --> E[管理员工名单]
    D --> F[设置加班状态]
    E --> H[添加/删除员工]
    F --> I[切换周六/周日]
    F --> J[设置员工状态]
    J --> K[API保存]
    K --> L[更新界面显示]
    L --> M[查看统计信息]
```

### 4.2 加班状态设置流程

```mermaid
graph TD
    A[选择日期] --> B[查看员工列表]
    B --> C{操作类型}
    C -->|单个设置| D[点击员工状态]
    C -->|批量操作| E[选择批量操作]
    D --> F[切换状态]
    E --> G[全部设为正常加班]
    E --> H[全部设为出差]
    E --> I[清空所有状态]
    F --> J[API保存]
    G --> J
    H --> J
    I --> J
    J --> K[更新界面显示]
```

## 5. 数据模型设计

### 5.1 核心实体关系

```mermaid
erDiagram
    departments ||--o{ staffs : contains
    departments ||--o{ sub_departments : contains
    sub_departments ||--o{ staffs : belongs_to
    staffs ||--o| sat : has
    staffs ||--o| sun : has

    departments {
        int id PK
        string name UK
    }
    
    sub_departments {
        int id PK
        int department_id FK
        string name
    }
    
    staffs {
        int id PK
        string name UK
        int department_id FK
        int sub_department_id FK
    }
    
    sat {
        int id PK
        int staff_id FK
        boolean is_evection
        string content
        string begin_time
        string end_time
        int updated_at
    }
    
    sun {
        int id PK
        int staff_id FK
        boolean is_evection
        string content
        string begin_time
        string end_time
        int updated_at
    }
```

### 5.2 状态说明
- **is_evection = 0**：正常加班（公司内）
- **is_evection = 1**：出差加班
- **无记录**：无加班

## 6. 非功能性需求

### 6.1 性能要求
- 页面响应时间 < 2秒
- 支持50+并发用户访问
- 数据库查询优化，避免N+1问题
- 前端资源按需加载（懒加载路由组件）

### 6.2 安全要求
- 部门数据隔离，防止跨部门访问
- 输入数据验证（Pydantic模型）
- API参数校验，防止SQL注入
- 会话管理，Cookie安全设置
- CORS跨域配置

### 6.3 可用性要求
- 直观的用户界面，操作简单
- 支持主流浏览器访问
- 移动端友好响应式设计
- Element Plus组件库提供一致的用户体验

### 6.4 可靠性要求
- 数据库事务保证数据一致性
- 异常处理和错误日志记录
- 自动数据库连接管理
- 类型检查确保代码质量

## 7. 技术架构

### 7.1 技术栈

#### 后端 (FastAPI)
- **框架**：FastAPI 0.104.1
- **ORM**：SQLAlchemy 2.0+
- **数据验证**：Pydantic 2.10+
- **ASGI服务器**：Uvicorn 0.24.0
- **认证**：python-jose, passlib
- **数据库**：SQLite（支持WAL模式）

#### 前端 (Vue 3)
- **框架**：Vue 3.3.8
- **路由**：Vue Router 4.2.5
- **状态管理**：Pinia 2.1.7
- **HTTP客户端**：Axios 1.6.2
- **UI组件库**：Element Plus 2.4.4
- **构建工具**：Vite 5.0.0
- **语言**：TypeScript 5.5.4

### 7.2 架构特点
- **前后端分离**：独立的开发和部署流程
- **RESTful API**：标准化的接口设计
- **类型安全**：前后端均使用类型系统
- **模块化设计**：路由、服务、模型分层清晰
- **数据库优化**：WAL模式提升并发性能

### 7.3 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI应用入口
│   │   ├── database.py      # 数据库配置
│   │   ├── routers/         # API路由
│   │   │   ├── departments.py
│   │   │   ├── staffs.py
│   │   │   ├── overtime.py
│   │   │   └── info.py
│   │   ├── services/        # 业务逻辑层
│   │   ├── models/          # 数据模型
│   │   ├── middleware/      # 中间件
│   │   └── utils/           # 工具函数
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.ts          # Vue应用入口
│   │   ├── App.vue
│   │   ├── router/          # 路由配置
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── stores/          # Pinia状态管理
│   │   └── utils/           # 工具函数
│   └── package.json
└── docker-compose.yml       # Docker部署配置
```

### 7.4 关键技术实现
- **依赖注入**：FastAPI的Depends系统管理数据库会话
- **数据验证**：Pydantic模型自动验证和序列化
- **状态管理**：Pinia管理前端应用状态
- **响应式设计**：Vue 3 Composition API
- **API交互**：Axios封装统一的HTTP请求处理

## 8. API接口设计

### 8.1 部门管理
- `GET /api/departments` - 获取所有部门列表
- `POST /api/departments/select` - 选择部门

### 8.2 员工管理
- `GET /api/staffs` - 获取当前部门员工列表
- `GET /api/staffs/sub-departments` - 获取子部门列表
- `POST /api/staffs/add` - 添加员工
- `POST /api/staffs/remove` - 移除员工

### 8.3 加班管理
- `POST /api/overtime/toggle` - 切换员工加班状态
- `GET /api/overtime/status` - 获取部门加班状态

### 8.4 信息查看
- `GET /api/info` - 获取统计信息

## 9. 部署与运维

### 9.1 开发环境
```bash
# 后端
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend && npm install
npm run dev

# 或使用启动脚本
./start-dev.sh
```

### 9.2 生产环境
```bash
# 前端构建
npm --prefix frontend run build

# Docker部署
docker-compose up -d --build
```

### 9.3 环境要求
- Python 3.8+
- Node.js 18+
- SQLite 3.x
- 现代Web浏览器

### 9.4 数据备份
- 定期备份SQLite数据库文件
- 支持数据库导出和恢复
- 操作日志记录便于审计

## 10. 质量保证

### 10.1 代码质量
- **后端**：black（格式化）、flake8（检查）、mypy（类型检查）
- **前端**：vue-tsc（TypeScript检查）、ESLint
- **测试**：pytest单元测试

### 10.2 测试命令
```bash
# 后端测试
cd backend && pytest

# 前端类型检查
npm --prefix frontend run typecheck

# 代码格式化
black backend/
flake8 backend/
```

## 11. 版本规划

### 11.1 当前版本 (v2.0)
- ✅ 基础加班管理功能
- ✅ 多部门支持
- ✅ 实时统计查看
- ✅ 前后端分离架构（FastAPI + Vue 3）
- ✅ TypeScript类型安全
- ✅ Element Plus UI组件库
- ✅ Docker部署支持
- ✅ 安全性增强（Pydantic验证、API参数校验）

### 11.2 未来规划
- 📋 用户权限管理系统
- 📋 加班时长统计
- 📋 报表导出功能
- 📋 移动端APP
- 📋 邮件通知功能
- 📋 数据导入导出
- 📋 历史记录查询

---

**文档版本**：v2.0  
**创建日期**：2026年2月7日  
**最后更新**：2026年2月18日
