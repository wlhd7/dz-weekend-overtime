from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

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
