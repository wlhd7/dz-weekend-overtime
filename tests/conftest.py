"""Test configuration and fixtures."""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import Base

# Create temporary database for testing
@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.unlink(path)

@pytest.fixture(scope="function")
def db_session(temp_db):
    """Create a fresh database session for each test."""
    # Create test engine
    test_engine = create_engine(
        f"sqlite:///{temp_db}",
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session factory
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def sample_department(db_session):
    """Create a sample department for testing."""
    from app.models import Department
    
    dept = Department(name="测试部门")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept

@pytest.fixture
def sample_staff(db_session, sample_department):
    """Create a sample staff for testing."""
    from app.models import Staff
    
    staff = Staff(
        name="测试员工",
        department_id=sample_department.id
    )
    db_session.add(staff)
    db_session.commit()
    db_session.refresh(staff)
    return staff
