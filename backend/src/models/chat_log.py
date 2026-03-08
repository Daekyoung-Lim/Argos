from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class ChatLog(Base):
    __tablename__ = "ChatLogs"

    log_id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    user_query = Column(String, nullable=False)
    generated_sql = Column(String, nullable=True)
    result_summary = Column(String, nullable=True)
    export_file_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.getdate())

    admin_user = relationship("User", back_populates="chat_logs")
