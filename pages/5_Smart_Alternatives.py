import streamlit as st

from config import (
    APP_FOOTER,
    PARKING_CATEGORIES,
    SUPPORTED_GENDERS,
    SUPPORTED_RESIDENCY,
    SUPPORTED_WALKING_TOLERANCE
)
from utils.loaders import load_buildings, load_parking_lots, load_gates
from services.rules_engine import is_lot_eligible
from services.recommendation_engine import get_alternative_lots
from services.occupancy_service import get_lot_by_id

# -----------------------------
# Custom CSS
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
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 15px;
        color: rgba(255,255,255,0.5);
        margin-bottom: 20px;
    }
    .section-head {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        margin: 16px 0 12px 0;
    }

    .pref-card {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .pref-card .pref-name {
        font-size: 20px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 8px;
    }
    .pref-detail {
        font-size: 14px;
        color: rgba(255,255,255,0.5);
        margin-bottom: 4px;
    }
    .pref-metrics {
        display: flex;
        gap: 12px;
        margin-top: 12px;
    }
    .pref-metric {
        background: rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 10px 16px;
        text-align: center;
        flex: 1;
    }
    .pref-metric .pm-val {
        font-size: 18px;
        font-weight: 700;
        color: #FFFFFF;
    }
    .pref-metric .pm-val.green { color: #2ECC71; }
    .pref-metric .pm-val.yellow { color: #F1C40F; }
    .pref-metric .pm-val.red { color: #E74C3C; }
    .pref-metric .pm-lbl {
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
        margin-top: 2px;
    }

    .alt-card {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s;
    }
    .alt-card:hover {
        border-color: rgba(0,108,53,0.3);
        transform: translateX(3px);
    }
    .alt-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .alt-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 800;
        color: white;
    }
    .alt-icon.available { background: linear-gradient(135deg, #006C35, #2ECC71); }
    .alt-icon.busy { background: linear-gradient(135deg, #E67E22, #F1C40F); }
    .alt-icon.full { background: linear-gradient(135deg, #C0392B, #E74C3C); }
    .alt-name { font-size: 16px; font-weight: 600; color: #FFFFFF; }
    .alt-meta { font-size: 12px; color: rgba(255,255,255,0.4); }
    .alt-right {
        text-align: right;
    }
    .alt-spaces { font-size: 16px; font-weight: 700; color: #2ECC71; }
    .alt-time { font-size: 12px; color: rgba(255,255,255,0.4); }

    .best-alt-card {
        background: rgba(46,204,113,0.08);
        border: 1px solid rgba(46,204,113,0.2);
        border-radius: 14px;
        padding: 18px 22px;
        margin-top: 16px;
    }
    .best-alt-card .ba-title {
        font-size: 15px;
        font-weight: 700;
        color: #2ECC71;
        margin-bottom: 6px;
    }
    .best-alt-card .ba-desc {
        font-size: 14px;
        color: rgba(255,255,255,0.6);
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
st.markdown('<div class="page-header">🔄 Smart Alternatives</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Get better suggestions when your preferred lot isn\'t ideal</div>', unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
buildings_df = load_buildings()
lots_df = load_parking_lots()
gates_df = load_gates()

building_options = []
building_map = {}

if not buildings_df.empty:
    for _, row in buildings_df.iterrows():
        building_id = str(row["building_id"])
        building_name_en = row.get("building_name_en", row.get("building_name", "Unknown Building"))
        building_name_ar = row.get("building_name_ar", "")

        if building_name_ar:
            label = f"{building_id} - {building_name_en} / {building_name_ar}"
        else:
            label = f"{building_id} - {building_name_en}"

        building_options.append(label)
        building_map[label] = building_id

lot_options = []
lot_map = {}

if not lots_df.empty:
    for _, row in lots_df.iterrows():
        lot_id = str(row["lot_id"])
        lot_name = row.get("lot_name", "Unknown Lot")
        lot_name_ar = row.get("lot_name_ar", "")

        if lot_name_ar:
            label = f"{lot_id} - {lot_name} / {lot_name_ar}"
        else:
            label = f"{lot_id} - {lot_name}"

        lot_options.append(label)
        lot_map[label] = lot_id

gate_options = []
gate_map = {}

if not gates_df.empty:
    for _, row in gates_df.iterrows():
        gate_id = str(row["gate_id"])
        gate_name = row.get("gate_name", f"Gate {gate_id}")
        gate_name_ar = row.get("gate_name_ar", "")

        if gate_name_ar:
            label = f"{gate_name} / {gate_name_ar}"
        else:
            label = gate_name

        gate_options.append(label)
        gate_map[label] = gate_id

# -----------------------------
# User Profile Input
# -----------------------------
with st.form("alternatives_form"):
    col1, col2 = st.columns(2)

    with col1:
        permit_type = st.selectbox("Permit Type", PARKING_CATEGORIES)
        gender = st.selectbox("Gender", SUPPORTED_GENDERS)
        residency = st.selectbox("Residency", SUPPORTED_RESIDENCY)
        preferred_gate_label = st.selectbox(
            "Preferred Gate",
            gate_options if gate_options else ["No gate data available"]
        )

    with col2:
        arrival_time = st.text_input("Arrival Time (HH:MM)", value="08:30")
        destination_label = st.selectbox(
            "Destination Building",
            building_options if building_options else ["No building data available"]
        )
        walking_tolerance = st.selectbox("Walking Tolerance", SUPPORTED_WALKING_TOLERANCE)

    preferred_lot_label = st.selectbox(
        "Preferred Parking Lot",
        lot_options if lot_options else ["No parking lot data available"]
    )

    submitted = st.form_submit_button("🔄 Find Smart Alternatives", use_container_width=True)

# -----------------------------
# Results
# -----------------------------
if submitted:
    if buildings_df.empty or lots_df.empty:
        st.error("Required data files are missing.")
    else:
        destination = building_map.get(destination_label)
        preferred_gate = gate_map.get(preferred_gate_label) if not gates_df.empty else None
        preferred_lot_id = lot_map.get(preferred_lot_label)
        preferred_lot = get_lot_by_id(preferred_lot_id)

        user_profile = {
            "permit_type": permit_type,
            "gender": gender,
            "residency": residency,
            "arrival_time": arrival_time,
            "destination": destination,
            "walking_tolerance": walking_tolerance,
            "preferred_gate": preferred_gate
        }

        st.markdown('<div class="section-head">Preferred Lot Check</div>', unsafe_allow_html=True)

        if preferred_lot is None:
            st.error("Preferred lot could not be found.")
        else:
            eligible = is_lot_eligible(user_profile, preferred_lot)
            status = preferred_lot.get("status", "unknown")
            available_spaces = int(preferred_lot.get("available_spaces", 0))
            capacity = int(preferred_lot.get("capacity", 0))
            occupied = int(preferred_lot.get("occupied", 0))

            status_color = "green" if status == "available" else ("yellow" if status == "busy" else "red")

            st.markdown(f"""
            <div class="pref-card">
                <div class="pref-name">{preferred_lot.get('lot_name', 'N/A')}</div>
                <div class="pref-detail">📍 Zone: {preferred_lot.get('zone', 'N/A')} • 🏷️ {preferred_lot.get('category', 'N/A')}</div>
                <div class="pref-detail">🚪 Gate: {preferred_lot.get('nearest_gate', 'N/A')}</div>
                <div class="pref-metrics">
                    <div class="pref-metric">
                        <div class="pm-val {status_color}">{status.upper()}</div>
                        <div class="pm-lbl">Status</div>
                    </div>
                    <div class="pref-metric">
                        <div class="pm-val">{available_spaces}</div>
                        <div class="pm-lbl">Available</div>
                    </div>
                    <div class="pref-metric">
                        <div class="pm-val">{'✅' if eligible else '❌'}</div>
                        <div class="pm-lbl">Eligible</div>
                    </div>
                    <div class="pref-metric">
                        <div class="pm-val">{occupied}/{capacity}</div>
                        <div class="pm-lbl">Occupancy</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            needs_alternative = (
                (not eligible) or
                (status == "full") or
                (available_spaces <= 0)
            )

            if not needs_alternative:
                st.success("✅ Your preferred lot is legal and currently available.")
            else:
                st.warning("⚠️ Your preferred lot is not the best option. See alternatives below.")

            st.markdown('<div class="section-head">Suggested Alternatives</div>', unsafe_allow_html=True)

            alternatives_df = get_alternative_lots(
                user_profile,
                exclude_lot_id=preferred_lot_id,
                top_n=5
            )

            if alternatives_df.empty:
                st.warning("No suitable alternatives were found.")
            else:
                for _, alt_row in alternatives_df.iterrows():
                    alt_name = alt_row.get("lot_name", "Unknown")
                    alt_status = alt_row.get("status", "available")
                    alt_avail = int(alt_row.get("available_spaces", 0))
                    alt_walk = alt_row.get("walking_time_min", "N/A")
                    alt_zone = alt_row.get("zone", "")
                    alt_gate = alt_row.get("nearest_gate", "")

                    st.markdown(f"""
                    <div class="alt-card">
                        <div class="alt-left">
                            <div class="alt-icon {alt_status}">P</div>
                            <div>
                                <div class="alt-name">{alt_name}</div>
                                <div class="alt-meta">{alt_zone} • Gate {alt_gate}</div>
                            </div>
                        </div>
                        <div class="alt-right">
                            <div class="alt-spaces">{alt_avail} spaces</div>
                            <div class="alt-time">{alt_walk} min walk</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                top_alt = alternatives_df.iloc[0]
                st.markdown(f"""
                <div class="best-alt-card">
                    <div class="ba-title">🏆 Best Alternative: {top_alt['lot_name']}</div>
                    <div class="ba-desc">
                        {int(top_alt['available_spaces'])} available spaces •
                        Gate {top_alt.get('nearest_gate', 'N/A')} •
                        {top_alt.get('walking_time_min', 'N/A')} min walk
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)