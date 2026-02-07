from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class Staff(Base):
    __tablename__ = "staffs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    sub_department_id = Column(Integer, ForeignKey("sub_departments.id"))
    
    # Relationships
    department = relationship("Department", back_populates="staffs")
    sub_department = relationship("SubDepartment", back_populates="staffs")
    sat_records = relationship("Sat", back_populates="staff")
    sun_records = relationship("Sun", back_populates="staff")
    
    def __repr__(self):
        return f"<Staff(id={self.id}, name='{self.name}', dept_id={self.department_id})>"
