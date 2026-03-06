import pytest
from datetime import date, datetime
import os
import sys

# 确保后端路径在 sys.path 中
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models import Department, Staff, DepartmentOperation, OvertimeWeek
from app.services.department import upsert_department_operation
from app.services.exports import OvertimeTableExportService, TEMPLATE_ROWS

def test_full_flow_op_records(db_session):
    """验证从操作触发到报表过滤的完整流程。"""
    # 1. 寻找 TEMPLATE_ROWS 中前两个有 department_id 的项
    target_rows = [r for r in TEMPLATE_ROWS if r.department_id is not None][:2]
    if len(target_rows) < 2:
        pytest.skip("Not enough template rows with department_id")
        
    id1 = target_rows[0].department_id
    name1 = target_rows[0].template_name
    id2 = target_rows[1].department_id
    name2 = target_rows[1].template_name
    
    # 2. 创建对应的部门和员工
    dept1 = Department(id=id1, name=name1)
    dept2 = Department(id=id2, name=name2)
    db_session.add_all([dept1, dept2])
    db_session.commit()
    
    staff1 = Staff(name="员工1", department_id=id1)
    staff2 = Staff(name="员工2", department_id=id2)
    db_session.add_all([staff1, staff2])
    db_session.commit()
    
    # 初始化加班记录 (测试周六)
    test_date = date(2026, 3, 7) # 周六
    
    db_session.add(OvertimeWeek(staff_id=staff1.id, sat="bg-2"))
    db_session.add(OvertimeWeek(staff_id=staff2.id, sat="bg-2"))
    db_session.commit()
    
    # 3. 模拟只有部门 1 有操作
    upsert_department_operation(db_session, name1, test_date)
    
    # 4. 验证报表生成
    export_service = OvertimeTableExportService(db_session)
    rows = export_service.build_department_rows(test_date)
    
    row1 = next(r for r in rows if r.department_id == id1)
    row2 = next(r for r in rows if r.department_id == id2)
    
    # 预期：部门 1 有名字，部门 2 没名字（被过滤）
    assert len(row1.name_runs) > 0
    assert row1.name_runs[0].text == "员工1"
    assert len(row2.name_runs) == 0
    assert row2.remark_count == 0
