from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class OvertimeWeek(Base):
    __tablename__ = "overtime_weeks"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staffs.id"), nullable=False, unique=True)
    mon = Column(String, default="bg-1", nullable=False)
    tue = Column(String, default="bg-1", nullable=False)
    wed = Column(String, default="bg-1", nullable=False)
    thu = Column(String, default="bg-1", nullable=False)
    fri = Column(String, default="bg-1", nullable=False)
    sat = Column(String, default="bg-1", nullable=False)
    sun = Column(String, default="bg-1", nullable=False)

    staff = relationship("Staff", back_populates="overtime_week")

    def __repr__(self):
        return (
            "<OvertimeWeek(staff_id=%s, mon=%s, tue=%s, wed=%s, thu=%s, fri=%s, sat=%s, sun=%s)>"
            % (
                self.staff_id,
                self.mon,
                self.tue,
                self.wed,
                self.thu,
                self.fri,
                self.sat,
                self.sun,
            )
        )


class Sat(Base):
    __tablename__ = "sat"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staffs.id"), nullable=False, unique=True)
    is_evection = Column(Boolean, default=False)
    content = Column(String, default="")
    begin_time = Column(String, default="")
    end_time = Column(String, default="")
    updated_at = Column(Integer, default=0)

    # Relationship
    staff = relationship("Staff", back_populates="sat_records")

    def __repr__(self):
        return f"<Sat(staff_id={self.staff_id}, is_evection={self.is_evection})>"


class Sun(Base):
    __tablename__ = "sun"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staffs.id"), nullable=False, unique=True)
    is_evection = Column(Boolean, default=False)
    content = Column(String, default="")
    begin_time = Column(String, default="")
    end_time = Column(String, default="")
    updated_at = Column(Integer, default=0)

    # Relationship
    staff = relationship("Staff", back_populates="sun_records")

    def __repr__(self):
        return f"<Sun(staff_id={self.staff_id}, is_evection={self.is_evection})>"
