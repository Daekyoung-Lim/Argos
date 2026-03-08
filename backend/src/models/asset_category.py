from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class AssetCategory(Base):
    __tablename__ = "AssetCategories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), nullable=False)
    audit_cycle_months = Column(Integer, default=12)

    assets = relationship("Asset", back_populates="category")
