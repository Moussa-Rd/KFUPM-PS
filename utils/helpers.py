import math
import pandas as pd

from config import PARKING_THRESHOLDS, WALKING_SPEED


def safe_split(value, separator=","):
    """
    Convert a comma-separated string into a clean Python list.
    Example:
    "student,resident" -> ["student", "resident"]
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []

    if isinstance(value, list):
        return value

    return [item.strip() for item in str(value).split(separator) if item.strip()]


def safe_lower(text):
    """
    Safely convert text to lowercase string.
    """
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    return str(text).strip().lower()


def matches_rule(user_value, allowed_values):
    """
    Check whether a user value matches allowed values.
    Supports 'all' as a universal value.
    """
    user_value = safe_lower(user_value)
    allowed_values = [safe_lower(v) for v in allowed_values]

    return "all" in allowed_values or user_value in allowed_values


def calculate_occupancy_percentage(capacity, occupied):
    """
    Return occupancy ratio between 0 and 1.
    """
    try:
        capacity = float(capacity)
        occupied = float(occupied)
    except Exception:
        return 0

    if capacity <= 0:
        return 0

    return occupied / capacity


def calculate_available_spaces(capacity, occupied):
    """
    Return available spaces, never below zero.
    """
    try:
        capacity = float(capacity)
        occupied = float(occupied)
    except Exception:
        return 0

    return max(int(capacity - occupied), 0)


def get_parking_status(capacity, occupied):
    """
    Return parking status based on occupancy ratio.
    """
    occupancy_ratio = calculate_occupancy_percentage(capacity, occupied)

    if occupancy_ratio < PARKING_THRESHOLDS["available"]:
        return "available"
    elif occupancy_ratio < PARKING_THRESHOLDS["busy"]:
        return "busy"
    return "full"


def calculate_walking_time(distance_meters):
    """
    Estimate walking time in minutes.
    """
    if distance_meters is None:
        return 0

    try:
        distance_meters = float(distance_meters)
    except Exception:
        return 0

    if distance_meters < 0:
        return 0

    return round(distance_meters / WALKING_SPEED)


def euclidean_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance in meters between two GPS points using Haversine formula.
    Accurate for the KFUPM campus scale.
    """
    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
    except Exception:
        return None

    R = 6_371_000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def image_distance(x1, y1, x2, y2):
    """
    Distance helper for image-based campus map coordinates.
    """
    try:
        x1 = float(x1)
        y1 = float(y1)
        x2 = float(x2)
        y2 = float(y2)
    except Exception:
        return None

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def is_within_walking_tolerance(distance, max_distance):
    """
    Check whether a distance is within walking tolerance.
    """
    if distance is None or max_distance is None:
        return False

    try:
        return float(distance) <= float(max_distance)
    except Exception:
        return False


def normalize_score(value, min_value, max_value):
    """
    Normalize a value between 0 and 1.
    """
    try:
        value = float(value)
        min_value = float(min_value)
        max_value = float(max_value)
    except Exception:
        return 0

    if max_value == min_value:
        return 0

    return (value - min_value) / (max_value - min_value)


def format_lot_display(row):
    """
    Format a clean display name for a parking lot row.
    """
    lot_name = row.get("lot_name", "Unknown Lot")
    zone = row.get("zone", "Unknown Zone")
    available_spaces = row.get("available_spaces", 0)

    return f"{lot_name} ({zone}) - {available_spaces} spaces available"


def format_building_display(row):
    """
    Format a building label with optional Arabic support.
    """
    building_id = row.get("building_id", "")
    building_name_en = row.get("building_name_en", row.get("building_name", "Unknown Building"))
    building_name_ar = row.get("building_name_ar", "")

    if building_name_ar:
        return f"{building_id} - {building_name_en} / {building_name_ar}"

    return f"{building_id} - {building_name_en}"


def format_gate_display(row):
    """
    Format a gate label with optional Arabic support.
    """
    gate_name = row.get("gate_name", "Unknown Gate")
    gate_name_ar = row.get("gate_name_ar", "")

    if gate_name_ar:
        return f"{gate_name} / {gate_name_ar}"

    return gate_name


def format_time_range(time_rules):
    """
    Return a cleaner display value for time rules.
    """
    rule = safe_lower(time_rules)

    if rule in ["", "all", "none"]:
        return "All times"

    return str(time_rules)


def safe_int(value, default=0):
    """
    Safe integer conversion.
    """
    try:
        return int(float(value))
    except Exception:
        return default


def safe_float(value, default=0.0):
    """
    Safe float conversion.
    """
    try:
        return float(value)
    except Exception:
        return default