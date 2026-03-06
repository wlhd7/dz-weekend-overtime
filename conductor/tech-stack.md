# 技术栈 (Technology Stack)

## 1. 编程语言 (Programming Languages)
- **Python 3.11+：** 用于编写高性能、现代化的 FastAPI 后端。
- **TypeScript：** 确保前端代码的类型安全和长期维护的可靠性。

## 2. 后端开发 (Backend Frameworks)
- **FastAPI：** 用于构建高性能、异步的 RESTful API，并自动生成完善的交互式 API 文档。
- **SQLAlchemy (ORM)：** 负责与数据库的交互，提供灵活的对象关系映射功能。

## 3. 前端开发 (Frontend Frameworks)
- **Vue 3 (Composition API)：** 提供响应式、声明式的 UI 组件开发模式，具有极佳的性能和可扩展性。
- **Vite：** 现代化的构建工具，提供极速的开发服务器启动和热模块替换体验。
- **Pinia：** 用于前端的状态管理，保持数据的单向流动和一致性。
- **Vue-router：** 官方路由管理器，实现单页应用 (SPA) 的导航和页面管理。

## 4. 数据库与持久化 (Database)
- **SQLite：** 作为轻量级、零配置的关系型数据库，完美支持当前的项目规模。
- **WAL 模式：** 开启预写日志 (Write-Ahead Logging) 模式，以提高数据库的并发性能。

## 5. 基础设施与工具 (Infrastructure & Tools)
- **Docker Compose：** 通过容器化管理后端、前端及反向代理服务，实现一键式的本地开发和部署环境。
- **Nginx：** 用作反向代理，负责请求分发、静态资源处理及 SSL 管理。
