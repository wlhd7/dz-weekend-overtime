import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import os
import sys

# 确保后端路径在 sys.path 中
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import Base
# 显式导入模型以注册到 Base.metadata
from app.models.department_operation import DepartmentOperation

def test_create_department_operation(db_session):
    """测试创建 DepartmentOperation 记录。"""
    today = date.today()
    op = DepartmentOperation(
        department_name="测试部门",
        date=today,
        last_updated=datetime.now()
    )
    db_session.add(op)
    db_session.commit()
    db_session.refresh(op)

    assert op.id is not None
    assert op.department_name == "测试部门"
    assert op.date == today
    assert isinstance(op.last_updated, datetime)
