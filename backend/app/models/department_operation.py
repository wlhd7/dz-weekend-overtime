from sqlalchemy import Column, Integer, String, Date, DateTime
from ..database import Base
from datetime import datetime

class DepartmentOperation(Base):
    __tablename__ = "department_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<DepartmentOperation(id={self.id}, department_name='{self.department_name}', date='{self.date}')>"
