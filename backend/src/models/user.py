from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    dept_id = Column(Integer, ForeignKey("Departments.dept_id"), nullable=True)
    role = Column(String(20), nullable=False, default="Employee")
    push_token = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.getdate())

    department = relationship("Department", back_populates="users", foreign_keys=[dept_id])
    assets = relationship("Asset", back_populates="current_holder", foreign_keys="Asset.current_holder_id")
    audit_logs = relationship("AuditLog", back_populates="user")
    chat_logs = relationship("ChatLog", back_populates="admin_user")
