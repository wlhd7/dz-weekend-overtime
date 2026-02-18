# 周末加班管理系统

一个基于Vue.js + FastAPI的现代化周末加班管理系统，支持多部门隔离管理和实时状态跟踪。

## 1. 🚀 技术栈

### 1.1 后端
- **FastAPI 0.104.1** - 现代Python Web框架
- **SQLAlchemy 2.0+** - Python ORM
- **Pydantic** - 数据验证和序列化
- **Uvicorn** - ASGI服务器
- **SQLite** - 轻量级数据库

### 1.2 前端
- **Vue 3.3.8** - 渐进式JavaScript框架
- **Vite 5.0.0** - 现代前端构建工具
- **Element Plus 2.4.4** - Vue 3 UI组件库
- **Pinia 2.1.7** - Vue状态管理
- **Vue Router 4.2.5** - 客户端路由
- **Axios 1.6.2** - HTTP客户端

### 1.3 部署
- **Docker** - 容器化部署
- **Docker Compose** - 多容器编排

## 2. 📋 功能特性

- ✅ **多部门管理** - 支持部门隔离和子部门管理
- ✅ **员工管理** - 添加/删除员工，支持子部门归属
- ✅ **加班状态管理** - 三种状态：无加班、正常加班、出差
- ✅ **实时统计** - 按部门查看加班人员统计
- ✅ **现代化UI** - 响应式设计，移动端友好
- ✅ **RESTful API** - 标准化API接口设计
- ✅ **容器化部署** - Docker一键部署

## 3. 🛠️ 快速开始

### 3.1 环境要求
- Python 3.8+
- Node.js 18+（Vite 5 要求）
- Docker & Docker Compose (生产环境)

### 3.2 开发环境

#### 3.2.1 克隆项目
```bash
git clone <repository-url>
cd dz-weekend-overtime
```

#### 3.2.2 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3.2.3 一键启动全栈（推荐）
```bash
./start-dev.sh
```

#### 3.2.4 开发环境设置（可选）
```bash
# 安装pre-commit钩子
pip install pre-commit
pre-commit install

# 使用开发工具（按需安装）
pip install black flake8 mypy pytest

black backend/              # 代码格式化
flake8 backend/             # 代码检查
mypy backend/               # 类型检查
cd backend && pytest        # 运行测试
pre-commit run --all-files  # 运行所有pre-commit检查
```

#### 3.2.5 启动前端
```bash
cd frontend
npm install
npm run dev
```

#### 3.2.6 访问应用
- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 3.3 生产环境 (Docker)

#### 3.3.1 一键部署
```bash
docker-compose up -d --build
```

#### 3.3.2 访问应用
- 前端：http://localhost:80
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

#### 3.3.3 查看日志
```bash
docker-compose logs -f
```

## 4. 📁 项目结构

```
dz-weekend-overtime/
├── .git/                   # Git版本控制
├── .github/                # GitHub Actions配置
├── .gitignore              # Git忽略文件
├── .python-version         # Python版本指定
├── .vscode/                # VS Code配置
├── .windsurf/              # Windsurf配置
├── backend/                # FastAPI后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── database.py     # 数据库配置
│   │   ├── models/         # SQLAlchemy模型
│   │   │   ├── department.py      # 部门模型
│   │   │   ├── overtime.py        # 加班状态模型
│   │   │   ├── staff.py           # 员工模型
│   │   │   └── sub_department.py  # 子部门模型
│   │   ├── routers/        # API路由
│   │   │   ├── departments.py     # 部门管理路由
│   │   │   ├── info.py           # 统计信息路由
│   │   │   ├── overtime.py       # 加班管理路由
│   │   │   └── staffs.py         # 员工管理路由
│   │   ├── utils/          # 工具模块
│   │   │   └── logging.py        # 日志工具
│   │   └── middleware/     # 中间件
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile          # 后端Docker配置
├── frontend/               # Vue.js前端
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   │   ├── BatchOperations.vue
│   │   │   ├── StaffForm.vue
│   │   │   └── StaffList.vue
│   │   ├── router/         # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/         # Pinia状态管理
│   │   │   ├── department.ts      # 部门状态管理
│   │   │   └── staff.ts           # 员工状态管理
│   │   ├── utils/          # 工具函数
│   │   │   └── api.ts             # API请求工具
│   │   ├── views/          # 页面组件
│   │   │   ├── DepartmentSelect.vue  # 部门选择页面
│   │   │   ├── Home.vue            # 主页面
│   │   │   └── Info.vue            # 统计信息页面
│   │   ├── App.vue         # 根组件
│   │   ├── main.ts         # 前端入口
│   │   └── shims-vue.d.ts  # TS声明
│   ├── index.html          # HTML入口文件
│   ├── nginx.conf          # Nginx配置（生产环境）
│   ├── package.json        # Node.js依赖
│   ├── package-lock.json   # 依赖锁定文件
│   ├── vite.config.js      # Vite构建配置
│   └── Dockerfile          # 前端Docker配置
├── weekendOvertime/        # 旧版Flask应用（遗留）
├── instance/               # 旧版Flask实例目录（遗留）
├── database/               # SQLite数据库文件
├── CHANGELOG.md            # 变更日志
├── MIGRATION-REPORT.md     # 迁移报告
├── README-MIGRATION.md     # 迁移说明
├── flask-to-fastapi-vue-migration-e10bc4.md  # 迁移文档
├── pyproject.toml          # Python项目配置（包含开发依赖）
├── start-dev.sh            # 开发启动脚本
├── test-backend.py         # 后端测试脚本
├── docker-compose.yml      # Docker编排配置
├── PRD.md                  # 产品需求文档
├── AGENTS.md               # 开发指南
└── README.md               # 项目说明
```

## 5. 🔧 开发工具集成

### 5.1 CI/CD 自动化
项目集成了 GitHub Actions 自动化流水线：
- **类型检查**：mypy 静态类型分析
- **代码检查**：flake8 代码风格检查  
- **格式检查**：black 代码格式验证
- **测试执行**：pytest 单元测试
- **前端构建**：Vue.js 应用构建和测试

### 5.2 Pre-commit 钩子
本地开发时自动执行代码质量检查：
```bash
# 安装钩子（一次性）
pre-commit install

# 手动运行所有检查
pre-commit run --all-files
```

每次提交代码时，pre-commit 会自动运行：
- 移除行尾空格
- 修复 YAML 语法
- black 代码格式化
- flake8 代码检查
- mypy 类型检查
- ESLint 前端代码检查

## 6. 🔧 API接口

### 6.1 部门管理
- `GET /api/departments` - 获取所有部门
- `GET /api/departments/current` - 获取当前部门
- `POST /api/departments/select` - 设置部门Cookie

### 6.2 员工管理
- `GET /api/staffs` - 获取当前部门员工（依赖 `department` Cookie）
- `GET /api/staffs/sub-departments` - 获取当前部门子部门（依赖 `department` Cookie）
- `POST /api/staffs/add` - 添加员工
- `POST /api/staffs/remove` - 删除员工

### 6.3 加班管理
- `POST /api/overtime/toggle` - 切换加班状态
- `POST /api/overtime/update` - 批量更新状态
- `GET /api/overtime/status` - 获取加班状态

### 6.4 统计信息
- `GET /api/info/statistics` - 获取跨部门统计

## 7. 🎨 状态标识

| 状态 | 标识 | 颜色 | 说明 |
|------|------|------|------|
| 无加班 | `bg-1` | 白色 | 默认状态 |
| 正常加班 | `bg-2` | 黄色 | 公司内加班 |
| 出差 | `bg-3` | 蓝色 | 外出出差 |

## 8. 🧪 测试

### 8.1 后端测试
```bash
cd backend && pytest
```

### 8.2 前端测试
```bash
cd frontend
npm run typecheck
npm run build
```

### 8.3 手动测试
访问 http://localhost:8000/docs 进行API测试

## 9. 📊 数据库

- **数据库文件**：`database/weekend-overtime.sqlite`
- **ORM**：SQLAlchemy 2.0+
- **自动建表**：应用启动时自动创建数据表

## 10. 🔒 安全特性

- **输入验证**：Pydantic模型验证
- **SQL注入防护**：SQLAlchemy参数化查询
- **CORS配置**：跨域资源共享控制
- **部门隔离**：数据访问权限控制

## 11. 📈 性能优化

- **数据库连接池**：SQLAlchemy连接管理
- **前端热重载**：Vite开发服务器
- **API缓存**：适当的响应缓存策略
- **容器化**：Docker多层缓存构建

## 12. 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 13. 📝 开发规范

- **代码风格**：遵循PEP 8 (Python) 和 Vue 3最佳实践
- **提交规范**：使用语义化提交信息
- **API设计**：遵循RESTful设计原则
- **文档更新**：及时更新相关文档

详细开发指南请参考 [AGENTS.md](./AGENTS.md)

## 14. 📄 许可证

本仓库当前未提供 LICENSE 文件。

## 15. 📞 支持

如有问题或建议，请：
1. 查看 [PRD.md](./PRD.md) 了解产品需求
2. 查看 [AGENTS.md](./AGENTS.md) 了解开发规范
3. 提交 Issue 或联系开发团队

---

**版本**：v2.0  
**最后更新**：2026年2月17日  
**架构**：Vue 3 + FastAPI 前后端分离
