## [1.1.1] - 2026-02-28

### Fixed
- 修复后端数据库环境变量名不匹配的问题 (@fix)
- 修正 SQLite 数据库在 Docker 容器内的默认相对路径 (@fix)

### Changed
- 将 Nginx 宿主机端口映射由 8001 调整为 8080 (@chore)
- 统一 Docker 部署中的数据库文件名为 weekend-overtime.sqlite (@chore)
- 开启 Vite 容器网络监听 (0.0.0.0) 以支持反向代理访问 (@chore)

# CHANGELOG

## [1.1.0] - 2026-02-28

### Added
- 实现首次登录强制跳转至部门选择页 (@feat)
- 前端 Pinia 商店集成 checkCurrentDepartment 缓存 (@perf)

### Changed
- 使用 Nginx 反向代理配置服务 (@chore)
- 移除后端直接端口访问限制 (@security)

## v0.0.1 - 2026-02-07

### Features

_No feature commits found since initial tag._

### Fixes
- Fix: index sub-department rendering; minor UI tweaks

### Breaking Changes

_No breaking changes found._

### Other changes
- update: multiple files
- chore: split runtime and dev requirements; add linters/types for dev
- opencode github install
- preset 4
- preset 3
- preset 2
- preset-basic
- 25.12.5
- chore(ui): remove no-overtime cookie UI and related handlers; add bulk-action helpers
- UI: mobile styles, clear button behavior; fix index template; toggle dedupe; add info page and migration script
- ?
- s
- Merge branch 'main' of github.com:wlhd7/dz-weekend-overtime
- Initial commit  On branch master
- Delete .gitignore
