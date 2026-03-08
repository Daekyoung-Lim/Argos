from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import require_employee
from ..models.user import User
from ..services.asset_service import get_assets_by_holder

router = APIRouter()


@router.get("/my")
def get_my_assets(
    current_user: User = Depends(require_employee),
    db: Session = Depends(get_db),
):
    assets = get_assets_by_holder(current_user.user_id, db)
    return {"assets": assets, "total": len(assets)}
