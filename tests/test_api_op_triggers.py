import pytest
from datetime import date
from fastapi.testclient import TestClient
import os
import sys

# 确保后端路径在 sys.path 中
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
from app.models import Department, DepartmentOperation, Staff
from app.database import get_db

client = TestClient(app)

def test_api_triggers_op_record(db_session):
    """验证 Staff API 和 Overtime API 是否触发操作记录。"""
    # 覆盖数据库依赖以使用测试 session
    app.dependency_overrides[get_db] = lambda: db_session
    
    try:
        # 1. 设置测试部门
        dept = Department(id=1, name="制造部")
        db_session.add(dept)
        db_session.commit()
    
        # 2. 调用添加员工接口
        response = client.post(
            "/api/staffs/add",
            json={"name": "新员工", "sub_department_id": None},
            cookies={"department": "1"}
        )
        assert response.status_code == 200
    
        # 检查操作记录
        op = db_session.query(DepartmentOperation).filter_by(
            department_name="制造部",
            date=date.today()
        ).first()
        assert op is not None
        
        # 3. 调用切换状态接口
        staff = db_session.query(Staff).filter_by(name="新员工").first()
        assert staff is not None
        
        response = client.post(
            "/api/overtime/toggle",
            json={"staff_id": staff.id, "status": "bg-2", "day": "sat"}
        )
        assert response.status_code == 200
        
        # 确认操作记录依然存在（由于是在同一个日期，upsert 应该是更新）
        db_session.refresh(op)
        assert op.department_name == "制造部"
        
    finally:
        # 清理覆盖，避免影响其他测试
        app.dependency_overrides.clear()
