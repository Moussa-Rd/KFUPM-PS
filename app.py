import streamlit as st

from config import (
    APP_NAME,
    APP_SHORT_NAME,
    APP_TAGLINE,
    APP_FOOTER,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    STATUS_COLORS,
    ASSETS
)
from services.occupancy_service import (
    get_summary_metrics,
    get_parking_status_table,
    get_zone_summary
)
from services.recommendation_engine import get_best_lot

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="KFUPM Smart Parking",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="auto"
)

# -----------------------------
# Custom CSS — Dark Mobile-Inspired Theme
# -----------------------------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    * { font-family: 'Inter', sans-serif !important; }

    .stApp {
        background-color: #0E1117;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ===== TOP HEADER BAR ===== */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 16px 20px;
        background: linear-gradient(135deg, #0E1117 0%, #161B22 100%);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin: -1rem -1rem 1.5rem -1rem;
    }
    .app-header-title {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    .app-header-icon {
        font-size: 22px;
        color: rgba(255,255,255,0.5);
    }

    /* ===== GREETING ===== */
    .greeting {
        padding: 0 4px;
        margin-bottom: 20px;
    }
    .greeting h2 {
        font-size: 22px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    .greeting p {
        font-size: 15px;
        color: rgba(255,255,255,0.55);
        margin: 0;
    }

    /* ===== NEAREST AVAILABLE CARD ===== */
    .nearest-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    .nearest-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #006C35, #2ECC71);
    }
    .nearest-label {
        font-size: 13px;
        color: #888;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .nearest-lot-name {
        font-size: 32px;
        font-weight: 800;
        color: #111;
        margin-bottom: 4px;
        letter-spacing: -1px;
    }
    .nearest-distance {
        font-size: 15px;
        color: #666;
        margin-bottom: 16px;
    }
    .nearest-bottom {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .nearest-spots {
        font-size: 26px;
        font-weight: 700;
        color: #333;
    }
    .nearest-spots span {
        color: #999;
        font-weight: 400;
    }
    .navigate-btn {
        display: inline-block;
        background: linear-gradient(135deg, #006C35 0%, #00913E 100%);
        color: white !important;
        padding: 12px 36px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(0,108,53,0.3);
    }
    .navigate-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0,108,53,0.4);
    }

    /* ===== CAMPUS PARKING SECTION ===== */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 14px;
        padding: 0 4px;
    }

    /* ===== PARKING LOT ROW CARD ===== */
    .lot-card {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }
    .lot-card:hover {
        border-color: rgba(0,108,53,0.3);
        transform: translateX(2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .lot-info {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .status-dot.available { background-color: #2ECC71; box-shadow: 0 0 8px rgba(46,204,113,0.4); }
    .status-dot.busy { background-color: #F1C40F; box-shadow: 0 0 8px rgba(241,196,15,0.4); }
    .status-dot.full { background-color: #E74C3C; box-shadow: 0 0 8px rgba(231,76,60,0.4); }

    .lot-details {
        display: flex;
        flex-direction: column;
    }
    .lot-name {
        font-size: 16px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .lot-status-text {
        font-size: 13px;
        font-weight: 500;
    }
    .lot-status-text.available { color: #2ECC71; }
    .lot-status-text.busy { color: #F1C40F; }
    .lot-status-text.full { color: #E74C3C; }

    .lot-occupancy {
        font-size: 20px;
        font-weight: 700;
        text-align: right;
    }
    .lot-occupancy.available { color: #2ECC71; }
    .lot-occupancy.busy { color: #F1C40F; }
    .lot-occupancy.full { color: #E74C3C; }

    /* ===== METRICS ROW ===== */
    .metrics-row {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    .metric-card {
        flex: 1;
        min-width: 120px;
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 18px 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
    }
    .metric-value.green { color: #2ECC71; }
    .metric-value.yellow { color: #F1C40F; }
    .metric-value.red { color: #E74C3C; }
    .metric-value.blue { color: #3498DB; }
    .metric-label {
        font-size: 12px;
        color: rgba(255,255,255,0.45);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }

    /* ===== NAV BAR ===== */
    .nav-bar {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: linear-gradient(180deg, #161B22 0%, #0E1117 100%);
        border-top: 1px solid rgba(255,255,255,0.06);
        padding: 12px 0;
        margin: 30px -1rem -1rem -1rem;
        border-radius: 0;
    }
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        text-decoration: none;
        color: rgba(255,255,255,0.4);
        font-size: 11px;
        font-weight: 500;
        transition: color 0.2s;
        cursor: pointer;
    }
    .nav-item.active {
        color: #2ECC71;
    }
    .nav-item:hover {
        color: #2ECC71;
    }
    .nav-icon {
        font-size: 20px;
    }

    /* ===== FOOTER ===== */
    .app-footer {
        text-align: center;
        color: rgba(255,255,255,0.25);
        margin-top: 40px;
        font-size: 12px;
        padding-bottom: 10px;
    }

    /* Streamlit metric overrides for dark theme */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="app-header">
    <span class="app-header-title">🅿️ KFUPM Smart Parking</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Greeting
# -----------------------------
st.markdown("""
<div class="greeting">
    <h2>Hello, Student!</h2>
    <p>Find your parking, the smart way.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Load Data
# -----------------------------
demo_user_profile = {
    "permit_type": "student",
    "gender": "male",
    "residency": "non_resident",
    "arrival_time": "08:30",
    "destination": "22",
    "walking_tolerance": "medium",
    "preferred_gate": "1"
}

metrics = get_summary_metrics()
parking_df = get_parking_status_table()
best_lot = get_best_lot(demo_user_profile)

# Fallback: if recommendation engine can't find a match, pick the best available lot directly
if not best_lot and not parking_df.empty:
    available_lots = parking_df[parking_df["status"] != "full"].copy()
    if not available_lots.empty:
        best_row = available_lots.sort_values("available_spaces", ascending=False).iloc[0]
        best_lot = best_row.to_dict()

# -----------------------------
# Nearest Available Card
# -----------------------------
if best_lot:
    lot_name = best_lot.get("lot_name", "N/A")
    walking_time = best_lot.get("walking_time_min", "N/A")
    distance = best_lot.get("distance_meters", None)
    if distance and distance > 0:
        distance_str = f"{int(distance)} m away"
    elif walking_time and walking_time != "N/A" and walking_time > 0:
        distance_str = f"{walking_time} min walk"
    else:
        distance_str = "On campus"
    available = int(best_lot.get("available_spaces", 0))
    capacity = int(best_lot.get("capacity", 0))
    occupied = int(best_lot.get("occupied", 0))

    st.markdown(f"""
    <div class="nearest-card">
        <div class="nearest-label">Nearest Available</div>
        <div class="nearest-lot-name">{lot_name}</div>
        <div class="nearest-distance">{distance_str}</div>
        <div class="nearest-bottom">
            <div class="navigate-btn">Navigate</div>
            <div class="nearest-spots">{occupied} <span>/ {capacity}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No recommended lot available. Check your data files.")

# -----------------------------
# Quick Metrics Bar
# -----------------------------
st.markdown(f"""
<div class="metrics-row">
    <div class="metric-card">
        <div class="metric-value blue">{metrics['total_lots']}</div>
        <div class="metric-label">Total Lots</div>
    </div>
    <div class="metric-card">
        <div class="metric-value green">{metrics['available_lots']}</div>
        <div class="metric-label">Available</div>
    </div>
    <div class="metric-card">
        <div class="metric-value yellow">{metrics['busy_lots']}</div>
        <div class="metric-label">Busy</div>
    </div>
    <div class="metric-card">
        <div class="metric-value red">{metrics['full_lots']}</div>
        <div class="metric-label">Full</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Campus Parking List
# -----------------------------
st.markdown('<div class="section-title">Campus Parking</div>', unsafe_allow_html=True)

if not parking_df.empty:
    for _, row in parking_df.iterrows():
        lot_name = row.get("lot_name", "Unknown")
        status = row.get("status", "available")
        occupied = int(row.get("occupied", 0))
        capacity = int(row.get("capacity", 0))

        # Status label mapping
        status_labels = {
            "available": "Available",
            "busy": "High Occupancy",
            "full": "Full"
        }
        status_label = status_labels.get(status, "Unknown")

        st.markdown(f"""
        <div class="lot-card">
            <div class="lot-info">
                <div class="status-dot {status}"></div>
                <div class="lot-details">
                    <div class="lot-name">{lot_name}</div>
                    <div class="lot-status-text {status}">{status_label}</div>
                </div>
            </div>
            <div class="lot-occupancy {status}">{occupied} / {capacity}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No parking data available. Please check your data files.")

# -----------------------------
# Bottom Nav Bar
# -----------------------------
st.markdown("""
<div class="nav-bar">
    <div class="nav-item active">
        <span class="nav-icon">🏠</span>
        <span>Home</span>
    </div>
    <div class="nav-item">
        <span class="nav-icon">🗺️</span>
        <span>Map</span>
    </div>
    <div class="nav-item">
        <span class="nav-icon">🔔</span>
        <span>Activity</span>
    </div>
    <div class="nav-item">
        <span class="nav-icon">👤</span>
        <span>Profile</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)