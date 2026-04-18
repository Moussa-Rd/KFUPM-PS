import pandas as pd

from config import RECOMMENDATION_WEIGHTS, WALKING_TOLERANCE
from utils.loaders import load_buildings
from utils.helpers import (
    euclidean_distance,
    calculate_walking_time,
    format_lot_display,
    safe_split
)
from services.rules_engine import is_lot_eligible
from services.occupancy_service import get_parking_status_table


def get_destination_record(destination_building):
    """
    Return the building record for the selected destination.
    Supports KFUPM building-based data.
    """
    buildings_df = load_buildings()

    if buildings_df.empty or destination_building is None:
        return None

    result = buildings_df[
        buildings_df["building_id"].astype(str) == str(destination_building)
    ]

    if result.empty:
        return None

    return result.iloc[0].to_dict()


def prepare_candidate_lots(user_profile):
    """
    Return candidate lots after eligibility filtering.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    eligible_rows = []

    for _, row in df.iterrows():
        if is_lot_eligible(user_profile, row):
            eligible_rows.append(row.to_dict())

    if not eligible_rows:
        return pd.DataFrame()

    return pd.DataFrame(eligible_rows)


def _get_distance_between_points(lot_row, destination_record):
    """
    Compute distance using lat/lon if available.
    Otherwise fall back to map_x/map_y for image-based campus map support.
    """
    if destination_record is None:
        return None

    lot_lat = lot_row.get("lat")
    lot_lon = lot_row.get("lon")
    dest_lat = destination_record.get("lat")
    dest_lon = destination_record.get("lon")

    if pd.notna(lot_lat) and pd.notna(lot_lon) and pd.notna(dest_lat) and pd.notna(dest_lon):
        return euclidean_distance(lot_lat, lot_lon, dest_lat, dest_lon)

    lot_x = lot_row.get("map_x")
    lot_y = lot_row.get("map_y")
    dest_x = destination_record.get("map_x")
    dest_y = destination_record.get("map_y")

    if pd.notna(lot_x) and pd.notna(lot_y) and pd.notna(dest_x) and pd.notna(dest_y):
        try:
            dx = float(dest_x) - float(lot_x)
            dy = float(dest_y) - float(lot_y)
            return (dx ** 2 + dy ** 2) ** 0.5
        except Exception:
            return None

    return None


def add_distance_metrics(df, destination_building):
    """
    Add distance and walking time from each lot to the destination building.
    """
    if df.empty:
        return df

    destination_record = get_destination_record(destination_building)

    df = df.copy()
    df["distance_meters"] = df.apply(
        lambda row: _get_distance_between_points(row, destination_record),
        axis=1
    )
    df["walking_time_min"] = df["distance_meters"].apply(calculate_walking_time)

    return df


def apply_walking_tolerance(df, walking_tolerance):
    """
    Filter lots based on the user's walking tolerance.
    """
    if df.empty:
        return df

    max_distance = WALKING_TOLERANCE.get(
        walking_tolerance,
        WALKING_TOLERANCE["medium"]
    )

    if "distance_meters" not in df.columns:
        return df

    return df[df["distance_meters"].fillna(float("inf")) <= max_distance].copy()


def add_building_match_score(df, destination_building):
    """
    Add building match score based on near_buildings field.
    """
    if df.empty:
        return df

    destination_building = str(destination_building) if destination_building is not None else ""

    df = df.copy()

    def compute_building_score(near_buildings_value):
        buildings_list = [str(x) for x in safe_split(near_buildings_value)]
        if destination_building in buildings_list:
            return 1.0
        if not buildings_list:
            return 0.5
        return 0.6

    df["building_match_score"] = df["near_buildings"].apply(compute_building_score)

    return df


def add_gate_match_score(df, preferred_gate):
    """
    Add gate match score based on nearest_gate.
    """
    if df.empty:
        return df

    df = df.copy()

    def compute_gate_score(nearest_gate):
        if preferred_gate is None or preferred_gate == "":
            return 0.7
        if str(nearest_gate) == str(preferred_gate):
            return 1.0
        return 0.6

    df["gate_match_score"] = df["nearest_gate"].apply(compute_gate_score)

    return df


def score_parking_lots(df):
    """
    Score lots based on:
    - availability
    - distance
    - congestion
    - eligibility
    - building match
    - gate match
    """
    if df.empty:
        return df

    df = df.copy()

    max_spaces = df["available_spaces"].max() if "available_spaces" in df.columns else 1
    max_distance = df["distance_meters"].max() if "distance_meters" in df.columns else 1
    max_congestion = df["occupancy_ratio"].max() if "occupancy_ratio" in df.columns else 1

    if pd.isna(max_spaces) or max_spaces == 0:
        max_spaces = 1
    if pd.isna(max_distance) or max_distance == 0:
        max_distance = 1
    if pd.isna(max_congestion) or max_congestion == 0:
        max_congestion = 1

    df["availability_score"] = df["available_spaces"].fillna(0) / max_spaces
    df["distance_score"] = 1 - (df["distance_meters"].fillna(max_distance) / max_distance)
    df["congestion_score"] = 1 - (df["occupancy_ratio"].fillna(max_congestion) / max_congestion)
    df["eligibility_score"] = 1.0

    if "building_match_score" not in df.columns:
        df["building_match_score"] = 0.5

    if "gate_match_score" not in df.columns:
        df["gate_match_score"] = 0.7

    weights = RECOMMENDATION_WEIGHTS

    df["final_score"] = (
        df["availability_score"] * weights["availability"] +
        df["distance_score"] * weights["distance"] +
        df["congestion_score"] * weights["congestion"] +
        df["eligibility_score"] * weights["eligibility"] +
        df["building_match_score"] * weights["building_match"] +
        df["gate_match_score"] * weights["gate_match"]
    )

    return df.sort_values(by="final_score", ascending=False).copy()


def get_recommended_lots(user_profile, top_n=5):
    """
    Main function to return the best KFUPM parking lot recommendations.
    """
    destination = user_profile.get("destination")
    walking_tolerance = user_profile.get("walking_tolerance", "medium")
    preferred_gate = user_profile.get("preferred_gate")

    df = prepare_candidate_lots(user_profile)

    if df.empty:
        return pd.DataFrame()

    df = add_distance_metrics(df, destination)
    df = apply_walking_tolerance(df, walking_tolerance)

    if df.empty:
        return pd.DataFrame()

    df = add_building_match_score(df, destination)
    df = add_gate_match_score(df, preferred_gate)
    df = score_parking_lots(df)

    return df.head(top_n).copy()


def get_best_lot(user_profile):
    """
    Return the single best lot recommendation.
    """
    df = get_recommended_lots(user_profile, top_n=1)

    if df.empty:
        return None

    row = df.iloc[0].to_dict()
    row["display_name"] = format_lot_display(row)
    return row


def get_alternative_lots(user_profile, exclude_lot_id=None, top_n=3):
    """
    Return alternative recommended lots, excluding one selected lot if needed.
    """
    df = get_recommended_lots(user_profile, top_n=10)

    if df.empty:
        return pd.DataFrame()

    if exclude_lot_id:
        df = df[df["lot_id"].astype(str) != str(exclude_lot_id)].copy()

    return df.head(top_n).copy()