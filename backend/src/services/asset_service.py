from sqlalchemy.orm import Session, joinedload
from ..models.asset import Asset
from ..models.asset_category import AssetCategory


def get_assets_by_holder(user_id: int, db: Session) -> list[dict]:
    """Return all active assets assigned to the given user."""
    assets = (
        db.query(Asset)
        .options(joinedload(Asset.category))
        .filter(Asset.current_holder_id == user_id, Asset.status == "Active")
        .all()
    )
    return [
        {
            "asset_id": a.asset_id,
            "asset_code": a.asset_code,
            "asset_name": a.asset_name,
            "category": {
                "category_id": a.category.category_id,
                "category_name": a.category.category_name,
            } if a.category else None,
            "registered_address": a.registered_address,
            "status": a.status,
            "last_audit_date": a.last_audit_date.isoformat() if a.last_audit_date else None,
            "last_condition": a.last_condition,
        }
        for a in assets
    ]
