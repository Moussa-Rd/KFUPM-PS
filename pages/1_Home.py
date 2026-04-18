import streamlit as st

from config import APP_NAME, APP_TAGLINE, APP_FOOTER
from services.occupancy_service import (
    get_summary_metrics,
    get_hotspot_lots,
    get_underused_lots,
    get_zone_summary,
    get_parking_status_table
)
from services.recommendation_engine import get_best_lot

st.set_page_config(page_title="Home | KFUPM Smart Parking", page_icon="🏠", layout="wide")

# -----------------------------
# Dark Theme CSS
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .page-header {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .page-subtitle {
        font-size: 15px;
        color: rgba(255,255,255,0.5);
        margin-bottom: 24px;
    }
    .dark-card {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 12px;
    }
    .dark-card h4 {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .dark-card p {
        color: rgba(255,255,255,0.55);
        font-size: 14px;
        margin: 0;
    }
    .rec-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.3);
    }
    .rec-card .rec-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .rec-card .rec-name {
        font-size: 26px;
        font-weight: 800;
        color: #111;
        margin-bottom: 6px;
    }
    .rec-card .rec-detail {
        font-size: 14px;
        color: #555;
        margin-bottom: 3px;
    }
    .rec-badge {
        display: inline-block;
        background: linear-gradient(135deg, #006C35 0%, #00913E 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        margin-top: 8px;
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
    .lot-row {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .lot-row:hover {
        border-color: rgba(0,108,53,0.3);
    }
    .lot-row .name {
        font-size: 15px;
        font-weight: 600;
        color: #FFFFFF;
    }
    .lot-row .zone-tag {
        font-size: 12px;
        color: rgba(255,255,255,0.4);
    }
    .lot-row .occ {
        font-size: 16px;
        font-weight: 700;
    }
    .lot-row .occ.green { color: #2ECC71; }
    .lot-row .occ.yellow { color: #F1C40F; }
    .lot-row .occ.red { color: #E74C3C; }
    .section-head {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 12px;
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
# Sample user profile for demo
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

# -----------------------------
# Load data
# -----------------------------
metrics = get_summary_metrics()
hotspot_lots = get_hotspot_lots(top_n=5)
underused_lots = get_underused_lots(top_n=5)
zone_summary = get_zone_summary()
best_lot = get_best_lot(demo_user_profile)

# Fallback: pick best available lot directly
if not best_lot:
    parking_df = get_parking_status_table()
    if not parking_df.empty:
        available_lots = parking_df[parking_df["status"] != "full"].copy()
        if not available_lots.empty:
            best_row = available_lots.sort_values("available_spaces", ascending=False).iloc[0]
            best_lot = best_row.to_dict()

# -----------------------------
# Page Header
# -----------------------------
st.markdown(f'<div class="page-header">🏠 {APP_NAME}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-subtitle">{APP_TAGLINE}</div>', unsafe_allow_html=True)

# -----------------------------
# Summary Metrics
# -----------------------------
st.markdown('<div class="section-head">Campus Parking Overview</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-row">
    <div class="metric-box"><div class="val">{metrics['total_lots']}</div><div class="lbl">Total Lots</div></div>
    <div class="metric-box"><div class="val green">{metrics['available_lots']}</div><div class="lbl">Available</div></div>
    <div class="metric-box"><div class="val yellow">{metrics['busy_lots']}</div><div class="lbl">Busy</div></div>
    <div class="metric-box"><div class="val red">{metrics['full_lots']}</div><div class="lbl">Full</div></div>
</div>
<div class="metric-row">
    <div class="metric-box"><div class="val">{metrics['total_capacity']}</div><div class="lbl">Total Capacity</div></div>
    <div class="metric-box"><div class="val">{metrics['total_occupied']}</div><div class="lbl">Occupied</div></div>
    <div class="metric-box"><div class="val green">{metrics['total_available_spaces']}</div><div class="lbl">Available Spaces</div></div>
    <div class="metric-box"><div class="val">{metrics['average_occupancy_percent']}%</div><div class="lbl">Avg Occupancy</div></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Best Recommendation
# -----------------------------
st.markdown('<div class="section-head">Recommended Parking</div>', unsafe_allow_html=True)

if best_lot:
    lot_name = best_lot.get("lot_name", "N/A")
    zone = best_lot.get("zone", "N/A")
    category = best_lot.get("category", "N/A")
    available = int(best_lot.get("available_spaces", 0))
    walking = best_lot.get("walking_time_min", "N/A")
    status = best_lot.get("status", "N/A")
    score = round(best_lot.get("final_score", 0), 3)
    gate = best_lot.get("nearest_gate", "N/A")

    st.markdown(f"""
    <div class="rec-card">
        <div class="rec-label">Best Match for You</div>
        <div class="rec-name">{lot_name}</div>
        <div class="rec-detail">📍 Zone: {zone} &nbsp;|&nbsp; 🏷️ Category: {category}</div>
        <div class="rec-detail">🚶 Walking: {walking} min &nbsp;|&nbsp; 🚪 Gate: {gate}</div>
        <div class="rec-detail">🅿️ Available: {available} spaces &nbsp;|&nbsp; 📊 Score: {score}</div>
        <div class="rec-badge">✅ {status.upper()}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No recommendation is available yet. Please check your data files.")

# -----------------------------
# Hotspot and Underused Lots
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-head">🔥 Hotspot Lots</div>', unsafe_allow_html=True)
    if not hotspot_lots.empty:
        for _, row in hotspot_lots.iterrows():
            name = row.get("lot_name", "Unknown")
            zone = row.get("zone", "")
            occ = int(row.get("occupied", 0))
            cap = int(row.get("capacity", 0))
            status = row.get("status", "available")
            color = "green" if status == "available" else ("yellow" if status == "busy" else "red")
            st.markdown(f"""
            <div class="lot-row">
                <div><div class="name">{name}</div><div class="zone-tag">{zone}</div></div>
                <div class="occ {color}">{occ} / {cap}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hotspot data available.")

with col2:
    st.markdown('<div class="section-head">💚 Underused Lots</div>', unsafe_allow_html=True)
    if not underused_lots.empty:
        for _, row in underused_lots.iterrows():
            name = row.get("lot_name", "Unknown")
            zone = row.get("zone", "")
            occ = int(row.get("occupied", 0))
            cap = int(row.get("capacity", 0))
            status = row.get("status", "available")
            color = "green" if status == "available" else ("yellow" if status == "busy" else "red")
            st.markdown(f"""
            <div class="lot-row">
                <div><div class="name">{name}</div><div class="zone-tag">{zone}</div></div>
                <div class="occ {color}">{occ} / {cap}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No underused lot data available.")

# -----------------------------
# Zone Summary
# -----------------------------
st.markdown("---")
st.markdown('<div class="section-head">📊 Campus Zone Summary</div>', unsafe_allow_html=True)

if not zone_summary.empty:
    st.dataframe(zone_summary, use_container_width=True)
else:
    st.info("No zone summary data available.")

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)