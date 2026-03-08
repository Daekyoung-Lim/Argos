import base64
import logging
from fastapi import UploadFile
from ..tools.blob_storage_tool import upload_bytes_to_blob
from ..tools.exif_parser_tool import extract_exif_metadata
from ..crews.asset_audit.crew import run_asset_diligence_crew

logger = logging.getLogger(__name__)


async def process_audit_submission(
    image: UploadFile,
    asset_code: str,
    asset_condition: str,
    user_id: int,
) -> dict:
    """
    Orchestrate the full asset self-survey pipeline:
    1. Read uploaded image bytes
    2. Upload to Azure Blob Storage
    3. Run Asset Diligence Crew (OCR + EXIF + DB validation)
    4. Return structured result
    """
    # 1. Read image bytes
    image_bytes = await image.read()
    print(f"[DEBUG] Image size: {len(image_bytes)} bytes")

    # 2. Upload to Blob Storage
    blob_path = f"audit-photos/{user_id}/temp_{asset_code}.jpg"
    photo_url = upload_bytes_to_blob(image_bytes, blob_path)

    # Extract EXIF metadata before running the AI agent
    exif_data = extract_exif_metadata(image_bytes)
    print(f"[DEBUG] EXIF extraction result: {exif_data}")

    # 3. Run CrewAI pipeline
    result = run_asset_diligence_crew(
        image_url=photo_url,
        exif_data=exif_data,
        asset_code=asset_code,
        user_id=user_id,
        asset_condition=asset_condition,
    )
    print(f"[DEBUG] CrewAI result: {result}")

    # 4. Rename blob to use actual audit_id if available
    audit_id = result.get("audit_id", -1)
    if audit_id is not None and isinstance(audit_id, int) and audit_id > 0:
        final_path = f"audit-photos/{user_id}/{audit_id}.jpg"
        upload_bytes_to_blob(image_bytes, final_path)
        result["photo_url"] = f"https://argosstphotos.blob.core.windows.net/asset-photos/{final_path}"

    result["photo_url"] = result.get("photo_url", photo_url)
    return result
