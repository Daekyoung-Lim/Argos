from datetime import datetime
from typing import Optional
from io import BytesIO

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _convert_gps_coordinate(value) -> float:
    """Convert GPS rational numbers (degrees, minutes, seconds) to decimal degrees."""
    d, m, s = value
    return float(d) + float(m) / 60 + float(s) / 3600


def extract_exif_metadata(image_bytes: bytes) -> dict:
    """
    Extract GPS coordinates and capture time from image EXIF data.
    Returns {
        "latitude": float | None,
        "longitude": float | None,
        "photo_taken_at": str | None,  # ISO format
        "error": str | None
    }
    """
    result = {"latitude": None, "longitude": None, "photo_taken_at": None, "error": None}
    try:
        img = Image.open(BytesIO(image_bytes))
        exif_data = img._getexif()
        if not exif_data:
            result["error"] = "No EXIF data found"
            return result

        tagged = {TAGS.get(k, k): v for k, v in exif_data.items()}

        # Extract timestamp
        dt_str = tagged.get("DateTimeOriginal") or tagged.get("DateTime")
        if dt_str:
            try:
                dt = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                result["photo_taken_at"] = dt.isoformat()
            except ValueError:
                pass

        # Extract GPS
        gps_info_raw = tagged.get("GPSInfo")
        if gps_info_raw:
            gps_data = {GPSTAGS.get(k, k): v for k, v in gps_info_raw.items()}
            lat_raw = gps_data.get("GPSLatitude")
            lat_ref = gps_data.get("GPSLatitudeRef", "N")
            lon_raw = gps_data.get("GPSLongitude")
            lon_ref = gps_data.get("GPSLongitudeRef", "E")

            if lat_raw and lon_raw:
                lat = _convert_gps_coordinate(lat_raw)
                lon = _convert_gps_coordinate(lon_raw)
                if lat_ref == "S":
                    lat = -lat
                if lon_ref == "W":
                    lon = -lon
                result["latitude"] = round(lat, 7)
                result["longitude"] = round(lon, 7)
            else:
                result["error"] = "GPS coordinates not found in EXIF"
        else:
            result["error"] = "No GPS information in EXIF"

    except Exception as e:
        result["error"] = str(e)

    return result
