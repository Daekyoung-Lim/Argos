from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import require_admin
from ..models.user import User
from ..services.admin_service import process_chat_query, export_chat_log

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
def admin_chat(
    request: ChatRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    result = process_chat_query(
        query=request.query,
        admin_user_id=current_user.user_id,
        db=db,
    )
    return result


@router.get("/chat/export/{log_id}")
def export_admin_chat(
    log_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = export_chat_log(log_id=log_id, admin_user_id=current_user.user_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Chat log not found")
    return result
