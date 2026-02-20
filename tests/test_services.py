"""Tests for service layer."""

import pytest
from fastapi import HTTPException

from app.services import DepartmentService, StaffService, OvertimeService
from app.models import Department, Staff, Sat, Sun


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

    def test_get_staffs_by_department_with_data(
        self, db_session, sample_department, sample_staff
    ):
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

    def _assert_status(self, service, staff_id, day, expected):
        try:
            status = service.get_staff_status(staff_id, day)
        except Exception as exc:
            pytest.fail(f"unexpected exception: {exc}")
        assert status == expected

    def test_get_staff_status_no_record(self, db_session, sample_staff):
        """Test getting staff status when no record exists."""
        service = OvertimeService(db_session)
        self._assert_status(service, sample_staff.id, "mon", "bg-1")

    def test_toggle_staff_status_to_internal(self, db_session, sample_staff):
        """Test setting staff status to internal overtime."""
        service = OvertimeService(db_session)
        success = service.toggle_staff_status(sample_staff.id, "bg-2", "mon")
        assert success is True

        # Check status was updated
        self._assert_status(service, sample_staff.id, "mon", "bg-2")

    def test_toggle_staff_status_to_business_trip(self, db_session, sample_staff):
        """Test setting staff status to business trip."""
        service = OvertimeService(db_session)
        success = service.toggle_staff_status(sample_staff.id, "bg-3", "mon")
        assert success is True

        # Check status was updated
        self._assert_status(service, sample_staff.id, "mon", "bg-3")

    def test_toggle_staff_status_to_none(self, db_session, sample_staff):
        """Test clearing staff status to no overtime."""
        service = OvertimeService(db_session)
        # First set to internal
        service.toggle_staff_status(sample_staff.id, "bg-2", "mon")

        # Then clear to none
        success = service.toggle_staff_status(sample_staff.id, "bg-1", "mon")
        assert success is True

        # Check status was updated
        self._assert_status(service, sample_staff.id, "mon", "bg-1")

    def test_apply_to_all_success(self, db_session, sample_department, sample_staff):
        """Test applying status to all staff in department."""
        service = OvertimeService(db_session)
        success = service.apply_to_all(sample_department.id, "bg-2", "tue")
        assert success is True

        # Check status was updated
        self._assert_status(service, sample_staff.id, "tue", "bg-2")

    def test_apply_to_all_empty_department(self, db_session, sample_department):
        """Test applying status to empty department."""
        service = OvertimeService(db_session)
        success = service.apply_to_all(sample_department.id, "bg-2", "tue")
        assert success is True

    def test_backfill_from_legacy_tables(self, db_session, sample_staff):
        """Test backfill creates unified records from legacy tables."""
        from app import models
        from app.services import overtime as overtime_module

        assert getattr(models, "OvertimeWeek", None) is not None
        assert hasattr(overtime_module, "backfill_overtime_weeks")

        sat_record = Sat(staff_id=sample_staff.id, is_evection=False)
        sun_record = Sun(staff_id=sample_staff.id, is_evection=True)
        db_session.add_all([sat_record, sun_record])
        db_session.commit()

        created = overtime_module.backfill_overtime_weeks(db_session)
        assert created == 1

        week = (
            db_session.query(models.OvertimeWeek)
            .filter(models.OvertimeWeek.staff_id == sample_staff.id)
            .first()
        )
        assert week is not None
        assert week.mon == "bg-1"
        assert week.sat == "bg-2"
        assert week.sun == "bg-3"
