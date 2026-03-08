from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, func
from sqlalchemy.orm import relationship
from ..database import Base


class AuditLog(Base):
    __tablename__ = "AuditLogs"

    audit_id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("Assets.asset_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    photo_url = Column(String, nullable=False)
    ocr_asset_code = Column(String(20), nullable=True)
    detected_address = Column(String(500), nullable=True)
    # geography stored as String — raw SQL for STDistance()
    detected_location = Column(String, nullable=True)
    distance_meters = Column(Float, nullable=True)
    photo_taken_at = Column(DateTime, nullable=True)
    asset_condition = Column(String(50), nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_msg = Column(String, nullable=True)
    device_info = Column(String(255), nullable=True)
    is_manual_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.getdate())

    asset = relationship("Asset", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
