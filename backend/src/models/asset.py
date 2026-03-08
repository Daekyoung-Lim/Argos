from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship
from ..database import Base


class Asset(Base):
    __tablename__ = "Assets"

    asset_id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(10), nullable=False, unique=True)
    asset_name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("AssetCategories.category_id"), nullable=True)
    status = Column(String(20), default="Active")
    current_holder_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    registered_address = Column(String(500), nullable=True)
    # geography type stored as raw WKT/binary — read via raw SQL for STDistance()
    from sqlalchemy.orm import deferred
    registered_location = deferred(Column(String, nullable=True))
    last_audit_date = Column(DateTime, nullable=True)
    last_condition = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.getdate())

    category = relationship("AssetCategory", back_populates="assets")
    current_holder = relationship("User", back_populates="assets", foreign_keys=[current_holder_id])
    audit_logs = relationship("AuditLog", back_populates="asset")
