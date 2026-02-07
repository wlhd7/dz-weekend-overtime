from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class SubDepartment(Base):
    __tablename__ = "sub_departments"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name = Column(String, nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="sub_departments")
    staffs = relationship("Staff", back_populates="sub_department")
    
    def __repr__(self):
        return f"<SubDepartment(id={self.id}, name='{self.name}', dept_id={self.department_id})>"
