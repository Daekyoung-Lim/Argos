from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException

from ..auth.dependencies import require_employee
from ..models.user import User
from ..services.audit_service import process_audit_submission

router = APIRouter()


@router.post("/submit")
async def submit_audit(
    image: UploadFile = File(..., description="Asset sticker photo (JPEG/PNG)"),
    asset_code: str = Form(..., description="10-digit asset code"),
    asset_condition: str = Form(..., description="Asset condition: 양호/불량/수리필요"),
    current_user: User = Depends(require_employee),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")

    result = await process_audit_submission(
        image=image,
        asset_code=asset_code,
        asset_condition=asset_condition,
        user_id=current_user.user_id,
    )

    return {
        "is_verified": result.get("is_verified", False),
        "audit_id": result.get("audit_id", -1),
        "asset_code": asset_code,
        "photo_url": result.get("photo_url"),
        "details": {
            "ocr_asset_code": result.get("ocr_asset_code"),
            "code_match": result.get("code_match", False),
            "detected_address": result.get("detected_address"),
            "distance_meters": result.get("distance_meters"),
            "location_match": result.get("location_match", False),
            "photo_taken_at": result.get("photo_taken_at"),
            "time_match": result.get("time_match", False),
        },
        "verification_msg": result.get("verification_msg", ""),
    }
