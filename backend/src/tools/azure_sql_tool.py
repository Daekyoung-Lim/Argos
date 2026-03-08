from sqlalchemy import text
from typing import Any, Optional
from ..database import get_db_context


def execute_read_query(sql: str, params: Optional[dict] = None) -> list[dict]:
    """Execute a SELECT query and return list of row dicts."""
    with get_db_context() as db:
        result = db.execute(text(sql), params or {})
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]


def execute_write(sql: str, params: Optional[dict] = None) -> int:
    """Execute an INSERT/UPDATE query and return rowcount."""
    with get_db_context() as db:
        result = db.execute(text(sql), params or {})
        return result.rowcount

def get_asset_with_distance(asset_code: str, detected_lat: float, detected_lon: float) -> Optional[dict]:
    """
    Fetch asset info and calculate distance to detected location using SQL Server STDistance().
    Returns dict with asset info + distance_meters, or None if not found.
    """
    sql = """
        SELECT
            a.asset_id,
            a.asset_code,
            a.asset_name,
            a.current_holder_id,
            a.registered_address,
            a.registered_location.STDistance(
                geography::Point(:lat, :lon, 4326)
            ) AS distance_meters
        FROM Assets a
        WHERE a.asset_code = :asset_code
    """
    rows = execute_read_query(sql, {"asset_code": asset_code, "lat": detected_lat, "lon": detected_lon})
    return rows[0] if rows else None


def insert_audit_log(data: dict) -> int:
    """Insert a new AuditLog record and return the new audit_id."""
    sql = """
        INSERT INTO AuditLogs (
            asset_id, user_id, photo_url, ocr_asset_code, detected_address,
            detected_location, distance_meters, photo_taken_at, asset_condition,
            is_verified, verification_msg, device_info
        )
        OUTPUT INSERTED.audit_id
        VALUES (
            :asset_id, :user_id, :photo_url, :ocr_asset_code, :detected_address,
            geography::Point(:lat, :lon, 4326), :distance_meters, :photo_taken_at,
            :asset_condition, :is_verified, :verification_msg, :device_info
        )
    """
    
    # Provide safe defaults if AI agent omits any keys
    safe_data = {
        "asset_id": data.get("asset_id", 0),
        "user_id": data.get("user_id", 0),
        "photo_url": data.get("photo_url", "https://argosstphotos.blob.core.windows.net/asset-photos/placeholder.jpg"),
        "ocr_asset_code": data.get("ocr_asset_code", ""),
        "detected_address": data.get("detected_address", ""),
        "lat": data.get("lat", 0.0),
        "lon": data.get("lon", 0.0),
        "distance_meters": data.get("distance_meters", 0.0),
        "photo_taken_at": data.get("photo_taken_at", "2000-01-01T00:00:00"),
        "asset_condition": data.get("asset_condition", "Unknown"),
        "is_verified": 1 if data.get("is_verified", False) else 0,
        "verification_msg": data.get("verification_msg", ""),
        "device_info": data.get("device_info", "CrewAI Verification Agent")
    }

    with get_db_context() as db:
        result = db.execute(text(sql), safe_data)
        row = result.fetchone()
        db.commit() # Important to commit insert!
        return row[0] if row else -1


def update_asset_audit_date(asset_id: int) -> None:
    """Update Assets.last_audit_date to now after successful verification."""
    sql = "UPDATE Assets SET last_audit_date = GETDATE() WHERE asset_id = :asset_id"
    execute_write(sql, {"asset_id": asset_id})
