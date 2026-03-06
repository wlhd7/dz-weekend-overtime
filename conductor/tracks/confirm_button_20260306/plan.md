# 实施计划 (Implementation Plan): 首页确认按钮 - 部门加班名单状态确认

本计划旨在实现首页新增“确认”按钮功能，通过点击按钮或进行修改操作，标记该部门在当日为“已确认”状态，并以此确保该部门显示在当日的加班统计报表中。

## Phase 1: 后端接口开发 (Backend API Development)
*本阶段侧重于新增后端确认接口，并确保该接口能正确操作 `department_operations` 表。*

- [ ] **Task: 新增确认操作 API 接口**
    - [ ] 在 `backend/app/routers/` 中新增接口，用于接收并记录部门确认操作。
    - [ ] 确保接口逻辑能正确在 `department_operations` 表中创建或更新记录。
- [ ] **Task: 扩展操作记录查询逻辑**
    - [ ] 确保前端在页面加载时，能查询到该部门在当日是否已存在操作记录，以决定按钮的初始状态。
- [ ] **Task: 编写后端单元测试 (TDD)**
    - [ ] 验证确认接口的幂等性和数据库记录的准确性。
- [ ] **Task: Conductor - User Manual Verification '后端接口开发' (Protocol in workflow.md)**

## Phase 2: 前端 UI 实现与集成 (Frontend UI & Integration)
*本阶段侧重于首页 UI 变更、按钮逻辑控制及与后端的集成。*

- [ ] **Task: 首页新增确认按钮 UI**
    - [ ] 在首页相关组件中新增“确认”按钮，位置在“全部出差”右侧。
    - [ ] 样式符合要求：蓝色加粗边框，白色背景。
- [ ] **Task: 按钮状态逻辑控制**
    - [ ] 页面加载时根据后端数据初始化按钮状态。
    - [ ] 点击确认或发生任何名单修改时，按钮应变为“已禁用”并显示“已确认”。
- [ ] **Task: 前端组件测试**
    - [ ] 验证按钮在不同状态下的显示和交互逻辑。
- [ ] **Task: Conductor - User Manual Verification '前端 UI 实现与集成' (Protocol in workflow.md)**

## Phase 3: 系统联调与验收 (System Integration & Verification)
*本阶段确保前后端协同工作，并在报表中正确反映确认状态。*

- [ ] **Task: 跨操作联动验证**
    - [ ] 验证手动确认和自动确认（由修改触发）的一致性。
- [ ] **Task: 统计报表集成验证**
    - [ ] 验证仅通过点击确认按钮（无修改），该部门是否能出现在统计汇总报表中。
- [ ] **Task: Conductor - User Manual Verification '系统联调与验收' (Protocol in workflow.md)**
