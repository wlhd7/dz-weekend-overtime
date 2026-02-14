"""Tests for service layer."""

import pytest
from fastapi import HTTPException

from app.services import DepartmentService, StaffService, OvertimeService
from app.models import Department, Staff

class TestDepartmentService:
    """Test DepartmentService functionality."""
    
    def test_get_all_departments_empty(self, db_session):
        """Test getting all departments when empty."""
        service = DepartmentService(db_session)
        departments = service.get_all_departments()
        assert departments == []
    
    def test_get_all_departments_with_data(self, db_session, sample_department):
        """Test getting all departments with data."""
        service = DepartmentService(db_session)
        departments = service.get_all_departments()
        assert len(departments) == 1
        assert departments[0].name == "测试部门"
    
    def test_get_department_by_id_success(self, db_session, sample_department):
        """Test getting department by valid ID."""
        service = DepartmentService(db_session)
        department = service.get_department_by_id(sample_department.id)
        assert department.name == "测试部门"
    
    def test_get_department_by_id_not_found(self, db_session):
        """Test getting department by invalid ID."""
        service = DepartmentService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.get_department_by_id(999)
        assert exc_info.value.status_code == 404
    
    def test_get_department_by_id_invalid_id(self, db_session):
        """Test getting department with invalid ID."""
        service = DepartmentService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.get_department_by_id(-1)
        assert exc_info.value.status_code == 400
    
    def test_validate_department_exists_success(self, db_session, sample_department):
        """Test validating existing department."""
        service = DepartmentService(db_session)
        department = service.validate_department_exists(sample_department.id)
        assert department.name == "测试部门"
    
    def test_validate_department_exists_not_found(self, db_session):
        """Test validating non-existing department."""
        service = DepartmentService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.validate_department_exists(999)
        assert exc_info.value.status_code == 404

class TestStaffService:
    """Test StaffService functionality."""
    
    def test_get_staffs_by_department_empty(self, db_session, sample_department):
        """Test getting staff when department has no staff."""
        service = StaffService(db_session)
        staffs = service.get_staffs_by_department(sample_department.id)
        assert staffs == []
    
    def test_get_staffs_by_department_with_data(self, db_session, sample_department, sample_staff):
        """Test getting staff with data."""
        service = StaffService(db_session)
        staffs = service.get_staffs_by_department(sample_department.id)
        assert len(staffs) == 1
        assert staffs[0]["name"] == "测试员工"
    
    def test_add_staff_success(self, db_session, sample_department):
        """Test adding staff successfully."""
        service = StaffService(db_session)
        success = service.add_staff("新员工", sample_department.id)
        assert success is True
        
        # Verify staff was added
        staffs = service.get_staffs_by_department(sample_department.id)
        assert len(staffs) == 1
        assert staffs[0]["name"] == "新员工"
    
    def test_add_staff_duplicate(self, db_session, sample_department, sample_staff):
        """Test adding duplicate staff."""
        service = StaffService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.add_staff("测试员工", sample_department.id)
        assert exc_info.value.status_code == 409
    
    def test_remove_staff_success(self, db_session, sample_department, sample_staff):
        """Test removing staff successfully."""
        service = StaffService(db_session)
        success = service.remove_staff("测试员工", sample_department.id)
        assert success is True
        
        # Verify staff was removed
        staffs = service.get_staffs_by_department(sample_department.id)
        assert len(staffs) == 0
    
    def test_remove_staff_not_found(self, db_session, sample_department):
        """Test removing non-existing staff."""
        service = StaffService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.remove_staff("不存在的员工", sample_department.id)
        assert exc_info.value.status_code == 404

class TestOvertimeService:
    """Test OvertimeService functionality."""
    
    def test_get_staff_status_no_record(self, db_session, sample_staff):
        """Test getting staff status when no record exists."""
        service = OvertimeService(db_session)
        status = service.get_staff_status(sample_staff.id, "sat")
        assert status == "bg-1"
    
    def test_toggle_staff_status_to_internal(self, db_session, sample_staff):
        """Test toggling staff status to internal overtime."""
        service = OvertimeService(db_session)
        success = service.toggle_staff_status(sample_staff.id, "bg-1", "sat")
        assert success is True
        
        # Check status was updated
        status = service.get_staff_status(sample_staff.id, "sat")
        assert status == "bg-2"
    
    def test_toggle_staff_status_to_business_trip(self, db_session, sample_staff):
        """Test toggling staff status to business trip."""
        service = OvertimeService(db_session)
        success = service.toggle_staff_status(sample_staff.id, "bg-2", "sat")
        assert success is True
        
        # Check status was updated
        status = service.get_staff_status(sample_staff.id, "sat")
        assert status == "bg-3"
    
    def test_toggle_staff_status_to_none(self, db_session, sample_staff):
        """Test toggling staff status to no overtime."""
        service = OvertimeService(db_session)
        # First set to internal
        service.toggle_staff_status(sample_staff.id, "bg-1", "sat")
        
        # Then toggle to none
        success = service.toggle_staff_status(sample_staff.id, "bg-3", "sat")
        assert success is True
        
        # Check status was updated
        status = service.get_staff_status(sample_staff.id, "sat")
        assert status == "bg-1"
    
    def test_apply_to_all_success(self, db_session, sample_department, sample_staff):
        """Test applying status to all staff in department."""
        service = OvertimeService(db_session)
        success = service.apply_to_all(sample_department.id, "bg-2", "sat")
        assert success is True
        
        # Check status was updated
        status = service.get_staff_status(sample_staff.id, "sat")
        assert status == "bg-2"
    
    def test_apply_to_all_empty_department(self, db_session, sample_department):
        """Test applying status to empty department."""
        service = OvertimeService(db_session)
        success = service.apply_to_all(sample_department.id, "bg-2", "sat")
        assert success is True
