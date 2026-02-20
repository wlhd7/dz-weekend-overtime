"""Overtime service for business logic."""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
import logging

from .base import BaseService
from ..models import Staff, Sat, Sun, OvertimeWeek
from .department import DepartmentService

logger = logging.getLogger(__name__)

DAY_TOKENS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def _legacy_status(record: Optional[Sat]) -> str:
    if not record:
        return "bg-1"
    return "bg-3" if record.is_evection is True else "bg-2"


def backfill_overtime_weeks(db: Session) -> int:
    """Backfill unified overtime records from legacy sat/sun tables."""
    created = 0
    try:
        staff_ids = [row.id for row in db.query(Staff.id).all()]
        if not staff_ids:
            return 0

        existing_ids = {
            row.staff_id
            for row in db.query(OvertimeWeek.staff_id)
            .filter(OvertimeWeek.staff_id.in_(staff_ids))
            .all()
        }

        sat_records = {
            record.staff_id: record
            for record in db.query(Sat).filter(Sat.staff_id.in_(staff_ids)).all()
        }
        sun_records = {
            record.staff_id: record
            for record in db.query(Sun).filter(Sun.staff_id.in_(staff_ids)).all()
        }

        for staff_id in staff_ids:
            if staff_id in existing_ids:
                continue

            week = OvertimeWeek(
                staff_id=staff_id,
                sat=_legacy_status(sat_records.get(staff_id)),
                sun=_legacy_status(sun_records.get(staff_id)),
            )
            db.add(week)
            created += 1

        if created:
            db.commit()
        return created
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to backfill overtime weeks")
        raise


class OvertimeService(BaseService):
    """Service for overtime-related business logic."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.department_service = DepartmentService(db)

    def get_staff_status(self, staff_id: int, day: str) -> Optional[str]:
        """Get staff overtime status for specific day."""
        try:
            self._validate_id(staff_id, "Staff ID")
            self._validate_day(day)

            # Validate staff exists
            staff = self._get_by_id(Staff, staff_id, "Staff")

            record = (
                self.db.query(OvertimeWeek)
                .filter(OvertimeWeek.staff_id == staff_id)
                .first()
            )

            if not record:
                return "bg-1"

            return getattr(record, day, "bg-1")

        except (ValueError, HTTPException):
            raise
        except Exception as e:
            self._log_error("get_staff_status", e, {"staff_id": staff_id, "day": day})
            raise HTTPException(status_code=500, detail="Failed to get staff status")

    def toggle_staff_status(self, staff_id: int, target_status: str, day: str) -> bool:
        """Set staff overtime status to target value."""
        try:
            self._validate_id(staff_id, "Staff ID")
            self._validate_day(day)
            self._validate_status(target_status)

            logger.info(
                "Starting status update for staff %s, target status: %s, day: %s",
                staff_id,
                target_status,
                day,
            )

            # Validate staff exists
            staff = self._get_by_id(Staff, staff_id, "Staff")

            # Find existing record
            record = (
                self.db.query(OvertimeWeek)
                .filter(OvertimeWeek.staff_id == staff_id)
                .first()
            )
            logger.debug(
                "Existing overtime week for staff %s: %s", staff_id, record is not None
            )

            if not record:
                record = OvertimeWeek(staff_id=staff_id)
                self.db.add(record)
                logger.debug("Created overtime week for staff %s", staff_id)

            setattr(record, day, target_status)

            success = self._commit_or_rollback(
                "toggle_staff_status",
                {"staff_id": staff_id, "day": day, "new_status": target_status},
            )

            if not success:
                raise HTTPException(
                    status_code=500, detail="Failed to update staff status"
                )

            logger.info(
                "Successfully updated staff %s status to %s for %s",
                staff_id,
                target_status,
                day,
            )
            return True

        except (ValueError, HTTPException):
            raise
        except Exception as e:
            self._log_error(
                "toggle_staff_status",
                e,
                {"staff_id": staff_id, "target_status": target_status, "day": day},
            )
            raise HTTPException(status_code=500, detail="Failed to toggle staff status")

    def apply_to_all(self, department_id: int, status: str, day: str) -> bool:
        """Apply status to all staff in department."""
        try:
            self._validate_id(department_id, "Department ID")
            self._validate_day(day)
            self._validate_status(status)

            # Validate department exists
            self.department_service.validate_department_exists(department_id)

            # Get all staff in department
            staffs = (
                self.db.query(Staff).filter(Staff.department_id == department_id).all()
            )

            if not staffs:
                logger.info(f"No staff found in department {department_id}")
                return True

            staff_ids = [staff.id for staff in staffs]
            existing_records = {
                record.staff_id: record
                for record in self.db.query(OvertimeWeek)
                .filter(OvertimeWeek.staff_id.in_(staff_ids))
                .all()
            }

            updated_count = 0
            for staff in staffs:
                record = existing_records.get(staff.id)
                if not record:
                    record = OvertimeWeek(staff_id=staff.id)
                    self.db.add(record)
                setattr(record, day, status)
                updated_count += 1

            success = self._commit_or_rollback(
                "apply_to_all",
                {
                    "department_id": department_id,
                    "day": day,
                    "status": status,
                    "updated_count": updated_count,
                },
            )

            if not success:
                raise HTTPException(
                    status_code=500, detail="Failed to apply status to all staff"
                )

            logger.info(
                f"Applied status {status} to {updated_count} staff in department {department_id} for {day}"
            )
            return True

        except (ValueError, HTTPException):
            raise
        except Exception as e:
            self._log_error(
                "apply_to_all",
                e,
                {"department_id": department_id, "status": status, "day": day},
            )
            raise HTTPException(
                status_code=500, detail="Failed to apply status to all staff"
            )

    def get_department_statistics(self, department_id: int, day: str) -> Dict[str, Any]:
        """Get department overtime statistics."""
        try:
            self._validate_id(department_id, "Department ID")
            self._validate_day(day)

            # Validate department exists
            self.department_service.validate_department_exists(department_id)

            stats = self.db.execute(
                text(f"""
                SELECT
                    d.name as department_name,
                    COUNT(s.id) as total_staff,
                    COUNT(CASE WHEN ow.{day} = 'bg-2' THEN 1 END) as internal_overtime,
                    COUNT(CASE WHEN ow.{day} = 'bg-3' THEN 1 END) as business_trip,
                    COUNT(CASE WHEN ow.{day} IS NULL OR ow.{day} = 'bg-1' THEN 1 END) as no_overtime
                FROM departments d
                LEFT JOIN staffs s ON d.id = s.department_id
                LEFT JOIN overtime_weeks ow ON s.id = ow.staff_id
                WHERE d.id = :dept_id
                GROUP BY d.id, d.name
                """),
                {"dept_id": department_id},
            ).fetchone()

            if not stats:
                return {
                    "department_name": "",
                    "total_staff": 0,
                    "internal_overtime": 0,
                    "business_trip": 0,
                    "no_overtime": 0,
                }

            result = {
                "department_name": stats.department_name,
                "total_staff": stats.total_staff or 0,
                "internal_overtime": stats.internal_overtime or 0,
                "business_trip": stats.business_trip or 0,
                "no_overtime": stats.no_overtime or 0,
            }

            logger.info(f"Retrieved statistics for department {department_id} on {day}")
            return result

        except (ValueError, HTTPException):
            raise
        except Exception as e:
            self._log_error(
                "get_department_statistics",
                e,
                {"department_id": department_id, "day": day},
            )
            raise HTTPException(
                status_code=500, detail="Failed to get department statistics"
            )

    def _validate_day(self, day: str) -> None:
        """Validate day parameter."""
        if day not in DAY_TOKENS:
            raise ValueError("Day must be one of mon-sun")

    def _validate_status(self, status: str) -> None:
        """Validate status parameter."""
        if status not in ["bg-1", "bg-2", "bg-3"]:
            raise ValueError("Status must be 'bg-1', 'bg-2', or 'bg-3'")

    def _get_next_status(self, current_status: str) -> str:
        """Get next status in the cycle."""
        status_cycle = {"bg-1": "bg-2", "bg-2": "bg-3", "bg-3": "bg-1"}
        return status_cycle.get(current_status, "bg-1")
