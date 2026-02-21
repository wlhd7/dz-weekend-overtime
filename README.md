# 周末加班管理系统 (Weekend Overtime)

基于 FastAPI + Vue 3 的周末加班人员管理与统计系统：按部门隔离管理员工名单，分别管理周六/周日加班状态，并提供跨部门统计页。

## 功能概览

- 部门选择与隔离：部门信息写入 Cookie（`department`），有效期 1 年
- 员工管理：添加/移除员工；可选子部门/班组
- 加班状态：`bg-1` 无加班、`bg-2` 正常加班、`bg-3` 出差
- 统计页：按部门汇总周六/周日（正常/出差）名单

## 本地开发

### 依赖

- Python 3.8+（建议 3.11，Docker 使用 `python:3.11-slim`）
- Node.js 18+

### 一键启动（推荐）

```bash
./start-dev.sh
```

- 后端：`http://localhost:8000`
- 前端：`http://localhost:5173`
- Swagger：`http://localhost:8000/docs`

### 手动启动

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# frontend（新终端）
cd frontend
npm install
npm run dev
```

前端开发服务器已配置代理：`/api` -> `http://localhost:8000`（见 `frontend/vite.config.js`）。

## 测试与检查

```bash
# backend tests
cd backend && pytest

# backend lint/type
black backend/
flake8 backend/
mypy backend/

# frontend typecheck
npm --prefix frontend run typecheck
```

## 生产部署（Docker）

```bash
docker compose up -d --build
```

- 访问：`http://localhost:8080/`
- API：`http://localhost:8080/api/*`

说明：`frontend/nginx.conf` 会将 `/api/` 反代到后端容器。

### Troubleshooting

如果后端容器启动报错 `sqlite3.OperationalError: unable to open database file`：

- 现状：`backend/app/database.py` 使用固定的 SQLite 路径（未读取 `SQLITE_DATABASE_URL` 环境变量）
- 解决：将后端数据库路径改为容器内可写位置（例如 `/app/database/weekend-overtime.sqlite`），并与 `docker-compose.yml` 的 volume 对齐

## 数据与约定

- SQLite 数据库文件：`database/weekend-overtime.sqlite`（WAL 模式会生成 `*.sqlite-wal`/`*.sqlite-shm`）
- 周六/周日数据表：`sat` / `sun`（按 `staff_id` 唯一）
- 状态 token（前端样式类名）会被持久化：`bg-1` / `bg-2` / `bg-3`

## 项目结构

```text
backend/            FastAPI（routers/services/models/database）
frontend/           Vue 3 + Vite（views/components/stores/utils）
database/           SQLite 数据库文件
docker-compose.yml  Docker 编排（backend + frontend/nginx）
start-dev.sh        本地开发一键启动脚本
PRD.md              产品需求文档
```

### Docker Compose 命令

本项目使用 Docker Compose V2 语法：
- 启动：`docker compose up -d --build`
- 停止：`docker compose down`
- 查看状态：`docker compose ps`

## 相关文档

- `PRD.md`
- `AGENTS.md`（常用命令、风格约定）
