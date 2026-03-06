# 实施计划 (Implementation Plan): 部门每日操作记录与报表过滤

本计划旨在实现部门每日操作记录功能，并基于该记录对加班统计报表进行过滤，确保只有当天“活跃”的部门才会显示。

## Phase 1: 基础架构与后端实现 (Foundation & Backend)
*本阶段侧重于数据库变更和核心逻辑实现。*

- [ ] **Task: 创建 DepartmentOperation 数据库模型**
    - [ ] 在 `backend/app/models/` 中新增模型。
    - [ ] 字段：`id`, `department_name`, `date`, `last_updated`。
    - [ ] 运行数据库迁移或自动创建表。
- [ ] **Task: 实现操作记录更新 Service**
    - [ ] 编写 `upsert_department_operation(db, dept_name, date)` 函数。
    - [ ] 确保该函数是幂等的且支持并发更新（WAL 模式）。
- [ ] **Task: 集成操作记录钩子 (API Hooks)**
    - [ ] 在 `Staff` 增删改 API 中调用更新函数。
    - [ ] 在 `Overtime` 状态切换 API 中调用更新函数。
- [ ] **Task: 修改统计报表 API 过滤逻辑**
    - [ ] 在获取所有部门加班统计的接口中，加入对 `DepartmentOperation` 的连接或过滤。
    - [ ] 仅返回在请求日期有操作记录的部门数据。
- [ ] **Task: Conductor - User Manual Verification '基础架构与后端实现' (Protocol in workflow.md)**

## Phase 2: 前端集成与 UI 适配 (Frontend Integration)
*本阶段确保前端交互能触发后端记录，并正确展示过滤后的报表。*

- [ ] **Task: 验证前端触发逻辑**
    - [ ] 检查部门切换、员工添加、状态修改是否能成功触发后端操作记录更新。
    - [ ] 使用浏览器的 Network 面板确认请求流。
- [ ] **Task: 适配统计页展示**
    - [ ] 确保统计页在调用 API 后，能正确处理可能减少的部门列表（即隐藏未操作部门）。
    - [ ] 保持 UI 响应式和加载状态的一致性。
- [ ] **Task: Conductor - User Manual Verification '前端集成与 UI 适配' (Protocol in workflow.md)**

## Phase 3: 测试与优化 (Testing & Polish)
*本阶段侧重于系统稳定性、边界情况测试和 UI 优化。*

- [ ] **Task: 编写多场景集成测试**
    - [ ] 测试场景：A 部门有操作记录，B 部门有历史数据但今日未操作。结果：报表仅显示 A。
    - [ ] 测试场景：跨天操作。结果：昨天的记录不影响今天的报表显示。
- [ ] **Task: UI 细节优化**
    - [ ] 在管理页增加简单的视觉提示（如“今日已确认”状态）。
    - [ ] 确保在没有任何部门操作时，统计页有友好的空状态提示。
- [ ] **Task: Conductor - User Manual Verification '测试与优化' (Protocol in workflow.md)**
