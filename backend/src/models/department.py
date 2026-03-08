from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class Department(Base):
    __tablename__ = "Departments"

    dept_id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String(100), nullable=False)
    manager_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)

    users = relationship("User", back_populates="department", foreign_keys="User.dept_id")
