import pandas as pd

from utils.loaders import merge_parking_and_occupancy
from utils.helpers import (
    calculate_available_spaces,
    calculate_occupancy_percentage,
    get_parking_status,
    safe_lower
)


def get_parking_status_table():
    """
    Return KFUPM parking data enriched with occupancy metrics and status.
    """

    df = merge_parking_and_occupancy()

    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    # -----------------------------
    # Required numeric cleanup
    # -----------------------------
    df["occupied"] = pd.to_numeric(df.get("occupied", 0), errors="coerce").fillna(0)
    df["capacity"] = pd.to_numeric(df.get("capacity", 0), errors="coerce").fillna(0)

    # -----------------------------
    # Optional KFUPM fields
    # -----------------------------
    optional_columns_defaults = {
        "zone": "Unknown Zone",
        "category": "student",
        "nearest_gate": "",
        "status_note": "",
        "lot_name_ar": "",
    }

    # Columns that should exist but can remain NaN
    optional_nullable_columns = ["map_x", "map_y"]

    for column, default_value in optional_columns_defaults.items():
        if column not in df.columns:
            df[column] = default_value
        else:
            df[column] = df[column].fillna(default_value)

    for column in optional_nullable_columns:
        if column not in df.columns:
            df[column] = None

    # -----------------------------
    # Occupancy calculations
    # -----------------------------
    df["available_spaces"] = df.apply(
        lambda row: calculate_available_spaces(row["capacity"], row["occupied"]),
        axis=1
    )

    df["occupancy_ratio"] = df.apply(
        lambda row: calculate_occupancy_percentage(row["capacity"], row["occupied"]),
        axis=1
    )

    df["occupancy_percent"] = (df["occupancy_ratio"] * 100).round(1)

    df["status"] = df.apply(
        lambda row: get_parking_status(row["capacity"], row["occupied"]),
        axis=1
    )

    # -----------------------------
    # Text cleanup
    # -----------------------------
    df["zone"] = df["zone"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["nearest_gate"] = df["nearest_gate"].astype(str).str.strip()

    return df


def get_lot_by_id(lot_id):
    """
    Return one parking lot row by lot_id.
    """
    df = get_parking_status_table()

    if df.empty or lot_id is None:
        return None

    result = df[df["lot_id"].astype(str) == str(lot_id)]

    if result.empty:
        return None

    return result.iloc[0].to_dict()


def get_available_lots():
    """
    Return only lots that are not full.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    return df[df["status"] != "full"].copy()


def get_full_lots():
    """
    Return only full lots.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    return df[df["status"] == "full"].copy()


def get_busy_lots():
    """
    Return only busy lots.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    return df[df["status"] == "busy"].copy()


def get_hotspot_lots(top_n=5):
    """
    Return the most congested parking lots.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    return df.sort_values(by="occupancy_ratio", ascending=False).head(top_n).copy()


def get_underused_lots(top_n=5):
    """
    Return the least occupied parking lots.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    return df.sort_values(by="occupancy_ratio", ascending=True).head(top_n).copy()


def get_lots_by_zone(zone_name):
    """
    Return lots in a specific campus zone.
    """
    df = get_parking_status_table()

    if df.empty or not zone_name:
        return pd.DataFrame()

    return df[df["zone"].apply(safe_lower) == safe_lower(zone_name)].copy()


def get_lots_by_category(category_name):
    """
    Return lots by category such as student, non_resident, staff, visitor.
    """
    df = get_parking_status_table()

    if df.empty or not category_name:
        return pd.DataFrame()

    return df[df["category"].apply(safe_lower) == safe_lower(category_name)].copy()


def get_lots_by_gate(gate_id):
    """
    Return lots linked to a specific gate.
    """
    df = get_parking_status_table()

    if df.empty or gate_id is None:
        return pd.DataFrame()

    return df[df["nearest_gate"].astype(str) == str(gate_id)].copy()


def get_summary_metrics():
    """
    Return dashboard summary metrics for KFUPM parking overview.
    """
    df = get_parking_status_table()

    if df.empty:
        return {
            "total_lots": 0,
            "available_lots": 0,
            "busy_lots": 0,
            "full_lots": 0,
            "total_capacity": 0,
            "total_occupied": 0,
            "total_available_spaces": 0,
            "average_occupancy_percent": 0.0
        }

    return {
        "total_lots": int(len(df)),
        "available_lots": int((df["status"] == "available").sum()),
        "busy_lots": int((df["status"] == "busy").sum()),
        "full_lots": int((df["status"] == "full").sum()),
        "total_capacity": int(df["capacity"].sum()),
        "total_occupied": int(df["occupied"].sum()),
        "total_available_spaces": int(df["available_spaces"].sum()),
        "average_occupancy_percent": round(float(df["occupancy_percent"].mean()), 1)
    }


def get_zone_summary():
    """
    Return occupancy summary grouped by campus zone.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby("zone", dropna=False)
        .agg(
            total_lots=("lot_id", "count"),
            total_capacity=("capacity", "sum"),
            total_occupied=("occupied", "sum"),
            total_available_spaces=("available_spaces", "sum"),
            avg_occupancy_percent=("occupancy_percent", "mean")
        )
        .reset_index()
    )

    summary["avg_occupancy_percent"] = summary["avg_occupancy_percent"].round(1)

    return summary.sort_values(by="avg_occupancy_percent", ascending=False).copy()


def get_category_summary():
    """
    Return occupancy summary grouped by lot category.
    """
    df = get_parking_status_table()

    if df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby("category", dropna=False)
        .agg(
            total_lots=("lot_id", "count"),
            total_capacity=("capacity", "sum"),
            total_occupied=("occupied", "sum"),
            total_available_spaces=("available_spaces", "sum"),
            avg_occupancy_percent=("occupancy_percent", "mean")
        )
        .reset_index()
    )

    summary["avg_occupancy_percent"] = summary["avg_occupancy_percent"].round(1)

    return summary.sort_values(by="avg_occupancy_percent", ascending=False).copy()