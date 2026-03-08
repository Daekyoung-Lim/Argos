from crewai import Crew, Task, Process
from .agents import make_vision_agent, make_metadata_agent, make_db_reference_agent, make_verifier_agent


def run_asset_diligence_crew(
    image_url: str,
    exif_data: dict,
    asset_code: str,
    user_id: int,
    asset_condition: str,
) -> dict:
    """
    Run the Asset Diligence Crew sequentially.
    Input:
        image_url: Blob URL of uploaded photo
        exif_data: Pre-extracted EXIF metadata containing GPS and timestamp
        asset_code: Asset code claimed by the employee
        user_id: User performing the audit
        asset_condition: Condition reported (양호/불량/수리필요)
    Returns:
        {
          "is_verified": bool,
          "audit_id": int,
          "ocr_asset_code": str | None,
          "distance_meters": float | None,
          "photo_taken_at": str | None,
          "code_match": bool,
          "location_match": bool,
          "time_match": bool,
          "verification_msg": str
        }
    """
    vision_agent = make_vision_agent()
    metadata_agent = make_metadata_agent()
    db_agent = make_db_reference_agent()
    verifier_agent = make_verifier_agent()

    t_vision = Task(
        description=(
            f"Extract the asset code from this image URL: {image_url}. "
            "Note that the asset code could be in formats like 'KT-AS-1016' or a 9-digit sequence like '251015774'. "
            "Return a JSON with 'raw_text' and 'asset_code' (null if not found)."
        ),
        expected_output="JSON with raw_text and asset_code",
        agent=vision_agent,
    )

    t_metadata = Task(
        description=(
            f"Here is the pre-extracted EXIF metadata: {exif_data}. "
            "Format this into a JSON with 'latitude', 'longitude', 'photo_taken_at', and 'error'."
        ),
        expected_output="JSON with latitude, longitude, photo_taken_at, and error",
        agent=metadata_agent,
    )

    t_db = Task(
        description=(
            f"Look up asset info for '{asset_code}'. "
            "CRITICAL: You MUST use the `azure_sql_distance_tool`. Provide a single JSON string as input "
            "with exactly these keys: 'asset_code' (string), 'detected_lat' (float), and 'detected_lon' (float). "
            "Get the lat/lon from the metadata step. "
            "Return JSON with asset_id, distance_meters, registered_address, current_holder_id."
        ),
        expected_output="JSON with asset_id, distance_meters, registered_address, current_holder_id",
        agent=db_agent,
        context=[t_metadata],
    )

    import datetime
    current_time_str = datetime.datetime.now().isoformat()

    t_verify = Task(
        description=(
            f"Verify the asset survey submission for user_id={user_id}, asset_code={asset_code}. "
            f"The current system time is {current_time_str}. "
            "Rules: (1) OCR code == asset_code, (2) distance_meters <= 3000, (3) photo age <= 48h from current system time. "
            f"Asset condition: {asset_condition}. Image URL: {image_url}. "
            "Return JSON: is_verified, ocr_asset_code, distance_meters, "
            "photo_taken_at, code_match, location_match, time_match, verification_msg."
        ),
        expected_output=(
            "JSON with is_verified (bool), ocr_asset_code, distance_meters, "
            "photo_taken_at, code_match, location_match, time_match, verification_msg"
        ),
        agent=verifier_agent,
        context=[t_vision, t_metadata, t_db],
    )

    crew = Crew(
        agents=[vision_agent, metadata_agent, db_agent, verifier_agent],
        tasks=[t_vision, t_metadata, t_db, t_verify],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff(inputs={
        "image_url": image_url,
        "exif_data": exif_data,
        "asset_code": asset_code,
        "user_id": user_id,
        "asset_condition": asset_condition,
    })

    # Parse final task output
    import json
    import re
    try:
        raw_output = result.raw
        # Clean up markdown code block wrapping if present
        if "```" in raw_output:
            json_match = re.search(r'```(?:json)?\n?(.*?)\n?```', raw_output, re.DOTALL)
            if json_match:
                raw_output = json_match.group(1).strip()
            
        final_dict = json.loads(raw_output)
        
        # 1. Provide a more detailed diagnostic message if there's a problem
        verification_msg = final_dict.get("verification_msg", "")
        if not final_dict.get("code_match"):
             verification_msg += f" [자산 번호 불일치: {final_dict.get('ocr_asset_code')} != {asset_code}]"
        
        distance = final_dict.get("distance_meters")
        if distance is not None and distance > 3000 and not final_dict.get("location_match"):
             verification_msg += f" [위치 불일치: 지정 위치로부터 {distance:.1f}m 거리]"

        final_dict["verification_msg"] = verification_msg.strip()
        
        # 2. Insert into database using standard Python to guarantee it saves
        from ...tools.azure_sql_tool import insert_audit_log, get_asset_with_distance
        lat = exif_data.get('latitude', 0.0)
        lon = exif_data.get('longitude', 0.0)
        db_info = get_asset_with_distance(asset_code, lat, lon)
        
        audit_data = {
            "asset_id": db_info["asset_id"] if db_info else 0,
            "user_id": user_id,
            "photo_url": image_url,
            "ocr_asset_code": final_dict.get("ocr_asset_code", ""),
            "detected_address": db_info["registered_address"] if db_info else "",
            "lat": lat,
            "lon": lon,
            "distance_meters": distance,
            "photo_taken_at": final_dict.get("photo_taken_at", "2000-01-01T00:00:00"),
            "asset_condition": asset_condition,
            "is_verified": final_dict.get("is_verified", False),
            "verification_msg": final_dict["verification_msg"]
        }
        
        audit_id = insert_audit_log(audit_data)
        final_dict["audit_id"] = audit_id
        
        return final_dict
        
    except (json.JSONDecodeError, AttributeError) as e:
        return {
            "is_verified": False,
            "audit_id": -1,
            "verification_msg": "분석 결과를 파싱할 수 없습니다.",
            "ocr_asset_code": None,
            "distance_meters": None,
            "photo_taken_at": None,
            "code_match": False,
            "location_match": False,
            "time_match": False,
        }
