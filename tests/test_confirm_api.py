import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.models import Department, DepartmentOperation
from app.database import get_db

client = TestClient(app)

def test_confirm_endpoint(db_session):
    """验证部门确认接口。"""
    # 覆盖数据库依赖
    app.dependency_overrides[get_db] = lambda: db_session
    
    try:
        # 1. 准备测试数据
        dept = Department(id=1, name="制造部")
        db_session.add(dept)
        db_session.commit()
        
        # 2. 调用确认接口 (POST /api/departments/confirm)
        # 模拟 Cookie
        response = client.post(
            "/api/departments/confirm",
            cookies={"department": "1"}
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # 3. 验证数据库中是否生成了操作记录
        op = db_session.query(DepartmentOperation).filter_by(
            department_name="制造部",
            date=date.today()
        ).first()
        assert op is not None
        
        # 4. 调用查询确认状态接口 (GET /api/departments/confirm-status)
        response = client.get(
            "/api/departments/confirm-status",
            cookies={"department": "1"}
        )
        assert response.status_code == 200
        assert response.json()["is_confirmed"] == True
        
    finally:
        app.dependency_overrides.clear()

def test_confirm_status_without_op(db_session):
    """验证未确认时的状态。"""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        dept = Department(id=1, name="制造部")
        db_session.add(dept)
        db_session.commit()
        
        # 在没有任何操作的情况下查询状态
        response = client.get(
            "/api/departments/confirm-status",
            cookies={"department": "1"}
        )
        assert response.status_code == 200
        assert response.json()["is_confirmed"] == False
        
    finally:
        app.dependency_overrides.clear()

def test_confirm_error_cases(db_session):
    """验证确认接口的错误处理。"""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        # 1. 缺失 Cookie
        response = client.post("/api/departments/confirm")
        assert response.status_code == 400
        assert "cookie not found" in response.json()["detail"].lower()
        
        response = client.get("/api/departments/confirm-status")
        assert response.status_code == 200
        assert response.json()["is_confirmed"] == False
        
        # 2. 部门不存在
        response = client.post("/api/departments/confirm", cookies={"department": "999"})
        assert response.status_code == 404
        
        response = client.get("/api/departments/confirm-status", cookies={"department": "999"})
        assert response.status_code == 200
        assert response.json()["is_confirmed"] == False
        
        # 3. 无效的 Cookie (非整数)
        response = client.get("/api/departments/confirm-status", cookies={"department": "abc"})
        assert response.status_code == 200
        assert response.json()["is_confirmed"] == False
        
    finally:
        app.dependency_overrides.clear()
