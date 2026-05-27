from typing import Any, Dict, Optional, Tuple, Union

from PIL import ExifTags, Image


def _convert_to_degrees(value: Any) -> Optional[float]:
    """Convert GPS coordinate from EXIF format to decimal degrees.

    Handles both legacy tuple-of-rationals format ``((n,d), (n,d), (n,d))``
    and modern Pillow IFDRational objects that are directly float-castable.
    """
    if value is None:
        return None
    try:
        parts = []
        for component in value:
            # Modern Pillow: IFDRational is float()-castable directly
            # Legacy Pillow: component is a (numerator, denominator) tuple
            try:
                parts.append(float(component))
            except (TypeError, ValueError):
                parts.append(component[0] / component[1])
        if len(parts) != 3:
            return None
        degrees, minutes, seconds = parts
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    except (TypeError, ZeroDivisionError, IndexError):
        return None


def _extract_gps(exif_data: Dict) -> Dict[str, Optional[float]]:
    gps_info = exif_data.get("GPSInfo")
    if not gps_info:
        return {"latitude": None, "longitude": None, "altitude": None}

    gps_parsed = {}
    for key, val in gps_info.items():
        tag = ExifTags.GPSTAGS.get(key, key)
        gps_parsed[tag] = val

    lat = _convert_to_degrees(gps_parsed.get("GPSLatitude"))
    lon = _convert_to_degrees(gps_parsed.get("GPSLongitude"))
    if lat is not None and gps_parsed.get("GPSLatitudeRef") == "S":
        lat = -lat
    if lon is not None and gps_parsed.get("GPSLongitudeRef") == "W":
        lon = -lon

    altitude = None
    alt_raw = gps_parsed.get("GPSAltitude")
    if alt_raw is not None:
        try:
            altitude = float(alt_raw)
        except (TypeError, ValueError):
            try:
                altitude = alt_raw[0] / alt_raw[1]
            except (TypeError, ZeroDivisionError, IndexError):
                altitude = None

    return {"latitude": lat, "longitude": lon, "altitude": altitude}


def extract_exif(image_path: str) -> Dict[str, Optional[str]]:
    try:
        with Image.open(image_path) as image:
            raw_exif = image._getexif() or {}
    except FileNotFoundError:
        return {"error": f"Image file not found: {image_path}"}
    except Exception as exc:
        return {"error": f"Failed to read image: {exc}"}

    exif_data = {}
    for tag_id, value in raw_exif.items():
        tag = ExifTags.TAGS.get(tag_id, tag_id)
        exif_data[tag] = value

    gps = _extract_gps(exif_data)

    return {
        "error": None,
        "camera_make": exif_data.get("Make"),
        "camera_model": exif_data.get("Model"),
        "software": exif_data.get("Software"),
        "datetime_original": exif_data.get("DateTimeOriginal"),
        "datetime": exif_data.get("DateTime"),
        "gps_latitude": gps["latitude"],
        "gps_longitude": gps["longitude"],
        "gps_altitude": gps["altitude"],
    }
