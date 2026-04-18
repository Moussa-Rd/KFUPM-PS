import pandas as pd
import streamlit as st

from config import DATA_PATHS


@st.cache_data
def load_parking_lots():
    """
    Load KFUPM parking lots data.
    Expected core columns:
    lot_id, lot_name, zone, capacity

    Optional columns:
    lot_name_ar, category, allowed_permits, gender_access,
    allowed_residency, time_rules, near_buildings, nearest_gate,
    map_x, map_y, lat, lon, status_note, restricted
    """
    try:
        df = pd.read_excel(DATA_PATHS["parking_lots"])

        if "lot_id" not in df.columns:
            st.error("parking_lots.csv must contain 'lot_id'.")
            return pd.DataFrame()

        return df

    except FileNotFoundError:
        st.error("parking_lots.csv file not found in data folder.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading parking lots data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_occupancy_data():
    """
    Load mock or live occupancy data.
    Expected columns:
    lot_id, occupied
    """
    try:
        df = pd.read_excel(DATA_PATHS["occupancy"])

        if "lot_id" not in df.columns or "occupied" not in df.columns:
            st.error("mock_live_occupancy.csv must contain 'lot_id' and 'occupied'.")
            return pd.DataFrame()

        return df

    except FileNotFoundError:
        st.error("mock_live_occupancy.csv file not found in data folder.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading occupancy data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_buildings():
    """
    Load KFUPM buildings data.

    Supported columns:
    building_id
    building_name_en or building_name
    building_name_ar
    zone
    map_x, map_y
    lat, lon
    """
    try:
        df = pd.read_excel(DATA_PATHS["buildings"])

        if "building_id" not in df.columns:
            st.error("buildings.csv must contain 'building_id'.")
            return pd.DataFrame()

        return df

    except FileNotFoundError:
        st.error("buildings.csv file not found in data folder.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading buildings data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_permits():
    """
    Load permit rules data.
    Expected columns:
    permit_type, description
    """
    try:
        df = pd.read_excel(DATA_PATHS["permits"])
        return df

    except FileNotFoundError:
        st.error("permits.csv file not found in data folder.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading permits data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_gates():
    """
    Load KFUPM gates data.

    Supported columns:
    gate_id, gate_name
    Optional:
    gate_name_ar, map_x, map_y, notes
    """
    try:
        df = pd.read_excel(DATA_PATHS["gates"])

        if "gate_id" not in df.columns:
            st.error("gates.csv must contain 'gate_id'.")
            return pd.DataFrame()

        return df

    except FileNotFoundError:
        st.error("gates.csv file not found in data folder.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading gates data: {e}")
        return pd.DataFrame()


def merge_parking_and_occupancy():
    """
    Merge parking lot data with occupancy data.
    Returns a combined dataframe.
    """
    lots_df = load_parking_lots()
    occupancy_df = load_occupancy_data()

    if lots_df.empty:
        return pd.DataFrame()

    if occupancy_df.empty:
        merged_df = lots_df.copy()
        merged_df["occupied"] = 0
    else:
        merged_df = lots_df.merge(occupancy_df, on="lot_id", how="left")
        merged_df["occupied"] = merged_df["occupied"].fillna(0)

    if "capacity" in merged_df.columns:
        merged_df["capacity"] = pd.to_numeric(
            merged_df["capacity"], errors="coerce"
        ).fillna(0)
    else:
        merged_df["capacity"] = 0

    merged_df["occupied"] = pd.to_numeric(
        merged_df["occupied"], errors="coerce"
    ).fillna(0)

    merged_df["available_spaces"] = merged_df["capacity"] - merged_df["occupied"]
    merged_df["available_spaces"] = merged_df["available_spaces"].clip(lower=0)

    return merged_df