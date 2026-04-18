# -----------------------------
# App Information
# -----------------------------
APP_NAME = "KFUPM Parking System (KFUPM-PS)"
APP_SHORT_NAME = "KFUPM-PS"
UNIVERSITY_NAME = "King Fahd University of Petroleum & Minerals"

APP_TAGLINE = "Smart parking guidance for KFUPM students"
APP_FOOTER = "Developed by Moussa REDAH"

# -----------------------------
# Theme Colors (KFUPM Style)
# -----------------------------
PRIMARY_COLOR = "#006C35"      # KFUPM green
SECONDARY_COLOR = "#A7C957"
BACKGROUND_COLOR = "#F7F7F7"
TEXT_COLOR = "#333333"
BORDER_COLOR = "#D9D9D9"

STATUS_COLORS = {
    "available": "#2ECC71",
    "busy": "#F1C40F",
    "full": "#E74C3C",
    "recommended": "#3498DB",
    "restricted": "#9B59B6"
}

# -----------------------------
# Parking Thresholds
# -----------------------------
PARKING_THRESHOLDS = {
    "available": 0.50,   # less than 50% occupied
    "busy": 0.80,        # 50% to less than 80%
    "full": 1.00         # 80% and above
}

# -----------------------------
# Recommendation Engine Weights
# -----------------------------
RECOMMENDATION_WEIGHTS = {
    "availability": 0.30,
    "distance": 0.25,
    "congestion": 0.15,
    "eligibility": 0.10,
    "building_match": 0.10,
    "gate_match": 0.10
}

# -----------------------------
# Walking Speed (meters/min)
# -----------------------------
WALKING_SPEED = 80

# -----------------------------
# Default User Preferences
# -----------------------------
DEFAULT_USER = {
    "residency": "non_resident",
    "gender": "male",
    "permit_type": "student",
    "walking_tolerance": "medium",
    "preferred_gate": None
}

# -----------------------------
# Walking Distance Categories (meters)
# -----------------------------
WALKING_TOLERANCE = {
    "short": 300,
    "medium": 700,
    "long": 1200
}

# -----------------------------
# Time Settings
# -----------------------------
DEFAULT_TIME_FORMAT = "%H:%M"

# -----------------------------
# Campus Map Settings
# -----------------------------
ASSETS = {
    "campus_map": "assets/kfupm_campus_map.jpg",
    "logo": "assets/logo.png"
}

MAP_IMAGE_SETTINGS = {
    "width": 1200,
    "height": 800
}

MAP_DEFAULT_LOCATION = {
    "lat": 26.3123,
    "lon": 50.1440
}

MAP_ZOOM_LEVEL = 15

# -----------------------------
# File Paths
# -----------------------------
DATA_PATHS = {
    "parking_lots": "data/parking_lots.xlsx",
    "occupancy": "data/mock_live_occupancy.xlsx",
    "buildings": "data/buildings.xlsx",
    "permits": "data/permits.xlsx",
    "gates": "data/gates.xlsx"
}

# -----------------------------
# Parking Categories
# -----------------------------
PARKING_CATEGORIES = [
    "student",
    "non_resident",
    "resident",
    "visitor",
    "staff",
    "faculty"
]

# -----------------------------
# Supported User Values
# -----------------------------
SUPPORTED_GENDERS = ["male", "female"]
SUPPORTED_RESIDENCY = ["resident", "non_resident"]
SUPPORTED_WALKING_TOLERANCE = ["short", "medium", "long"]

# -----------------------------
# Feature Flags
# -----------------------------
FEATURES = {
    "enable_live_data": False,
    "enable_routing": True,
    "enable_analytics": True,
    "enable_gate_support": True,
    "enable_image_map": True,
    "enable_bilingual_labels": True
}