import streamlit as st
import pandas as pd

from config import APP_FOOTER, ASSETS
from services.occupancy_service import get_parking_status_table

st.set_page_config(page_title="Map | KFUPM Smart Parking", page_icon="🗺️", layout="wide")

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .map-header {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    .map-subtitle {
        font-size: 15px;
        color: rgba(255,255,255,0.5);
        margin-bottom: 20px;
    }
    .metric-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }
    .metric-box {
        flex: 1;
        min-width: 100px;
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 16px 14px;
        text-align: center;
    }
    .metric-box .val {
        font-size: 24px;
        font-weight: 800;
        color: #FFFFFF;
    }
    .metric-box .val.green { color: #2ECC71; }
    .metric-box .val.yellow { color: #F1C40F; }
    .metric-box .val.red { color: #E74C3C; }
    .metric-box .lbl {
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    .section-head {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        margin: 20px 0 12px 0;
    }
    .lot-card {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .lot-card:hover {
        border-color: rgba(0,108,53,0.3);
    }
    .lot-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .status-dot.available { background: #2ECC71; box-shadow: 0 0 8px rgba(46,204,113,0.4); }
    .status-dot.busy { background: #F1C40F; box-shadow: 0 0 8px rgba(241,196,15,0.4); }
    .status-dot.full { background: #E74C3C; box-shadow: 0 0 8px rgba(231,76,60,0.4); }
    .lot-name { font-size: 15px; font-weight: 600; color: #FFFFFF; }
    .lot-meta { font-size: 12px; color: rgba(255,255,255,0.4); }
    .lot-occ { font-size: 16px; font-weight: 700; }
    .lot-occ.available { color: #2ECC71; }
    .lot-occ.busy { color: #F1C40F; }
    .lot-occ.full { color: #E74C3C; }

    .alert-card {
        background: rgba(231,76,60,0.1);
        border: 1px solid rgba(231,76,60,0.3);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        color: #E74C3C;
        font-size: 14px;
        font-weight: 500;
    }

    .app-footer {
        text-align: center;
        color: rgba(255,255,255,0.25);
        margin-top: 40px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="map-header">🗺️ Live Parking Map</div>', unsafe_allow_html=True)
st.markdown('<div class="map-subtitle">View parking lot availability across KFUPM campus</div>', unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
df = get_parking_status_table()

if df.empty:
    st.error("No parking data available. Please check your data files.")
else:
    # Sidebar Filters
    st.sidebar.header("Map Filters")

    selected_status = st.sidebar.multiselect(
        "Filter by Status",
        options=["available", "busy", "full"],
        default=["available", "busy", "full"]
    )

    zone_options = sorted(df["zone"].dropna().astype(str).unique().tolist())
    selected_zone = st.sidebar.multiselect(
        "Filter by Zone",
        options=zone_options,
        default=zone_options
    )

    category_options = sorted(df["category"].dropna().astype(str).unique().tolist())
    selected_category = st.sidebar.multiselect(
        "Filter by Category",
        options=category_options,
        default=category_options
    )

    filtered_df = df[
        df["status"].isin(selected_status) &
        df["zone"].isin(selected_zone) &
        df["category"].isin(selected_category)
    ].copy()

    # Summary Metrics
    total = len(filtered_df)
    avail_spaces = int(filtered_df["available_spaces"].sum())
    avg_occ = filtered_df["occupancy_percent"].mean() if not filtered_df.empty else 0
    full_count = int((filtered_df["status"] == "full").sum())

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box"><div class="val">{total}</div><div class="lbl">Visible Lots</div></div>
        <div class="metric-box"><div class="val green">{avail_spaces}</div><div class="lbl">Available Spaces</div></div>
        <div class="metric-box"><div class="val yellow">{round(avg_occ, 1)}%</div><div class="lbl">Avg Occupancy</div></div>
        <div class="metric-box"><div class="val red">{full_count}</div><div class="lbl">Full Lots</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Campus Map Image
    st.markdown('<div class="section-head">KFUPM Campus Map</div>', unsafe_allow_html=True)

    try:
        st.image(
            ASSETS["campus_map"],
            caption="KFUPM campus reference map",
            use_container_width=True
        )
    except Exception:
        st.warning("Campus map image not found. Please add assets/kfupm_campus_map.jpg")

    # Coordinate Map (if available)
    map_columns = ["lat", "lon"]
    has_coordinate_columns = all(column in filtered_df.columns for column in map_columns)

    if has_coordinate_columns:
        map_df = filtered_df[map_columns].dropna().copy()
        map_df.columns = ["lat", "lon"]

        if not map_df.empty:
            st.markdown('<div class="section-head">📍 Interactive Map View</div>', unsafe_allow_html=True)
            st.map(map_df, use_container_width=True)

    # Parking Lot Details
    st.markdown('<div class="section-head">Parking Lot Details</div>', unsafe_allow_html=True)

    for _, row in filtered_df.iterrows():
        lot_name = row.get("lot_name", "Unknown")
        status = row.get("status", "available")
        occupied = int(row.get("occupied", 0))
        capacity = int(row.get("capacity", 0))
        zone = row.get("zone", "")
        gate = row.get("nearest_gate", "")

        st.markdown(f"""
        <div class="lot-card">
            <div class="lot-left">
                <div class="status-dot {status}"></div>
                <div>
                    <div class="lot-name">{lot_name}</div>
                    <div class="lot-meta">{zone} • Gate {gate}</div>
                </div>
            </div>
            <div class="lot-occ {status}">{occupied} / {capacity}</div>
        </div>
        """, unsafe_allow_html=True)

    # Full Lots Alerts
    full_lots = filtered_df[filtered_df["status"] == "full"]

    if not full_lots.empty:
        st.markdown('<div class="section-head">⚠️ Full Lots Alert</div>', unsafe_allow_html=True)
        for _, row in full_lots.iterrows():
            st.markdown(f"""
            <div class="alert-card">
                🚫 {row['lot_name']} in {row['zone']} is currently full.
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)