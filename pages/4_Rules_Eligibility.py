import streamlit as st

from config import (
    APP_FOOTER,
    PARKING_CATEGORIES,
    SUPPORTED_GENDERS,
    SUPPORTED_RESIDENCY
)
from utils.loaders import load_parking_lots
from services.rules_engine import get_eligibility_details

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

    .result-card {
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .result-card.pass {
        background: rgba(46,204,113,0.1);
        border: 1px solid rgba(46,204,113,0.3);
    }
    .result-card.fail {
        background: rgba(231,76,60,0.1);
        border: 1px solid rgba(231,76,60,0.3);
    }
    .result-text {
        font-size: 18px;
        font-weight: 700;
    }
    .result-text.pass { color: #2ECC71; }
    .result-text.fail { color: #E74C3C; }

    .rule-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 10px;
        margin-bottom: 16px;
    }
    .rule-item {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
    }
    .rule-item .rule-name {
        font-size: 12px;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .rule-item .rule-status {
        font-size: 16px;
        font-weight: 700;
    }
    .rule-item .rule-status.pass { color: #2ECC71; }
    .rule-item .rule-status.fail { color: #E74C3C; }

    .info-card {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .info-row:last-child { border-bottom: none; }
    .info-label {
        font-size: 13px;
        color: rgba(255,255,255,0.4);
    }
    .info-value {
        font-size: 13px;
        color: #FFFFFF;
        font-weight: 600;
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
st.markdown('<div class="page-header">📋 Rules & Eligibility</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Check whether a parking lot is legal for your profile</div>', unsafe_allow_html=True)

# -----------------------------
# Load parking lots
# -----------------------------
lots_df = load_parking_lots()

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
        lot_map[label] = row.to_dict()

# -----------------------------
# User Input
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    permit_type = st.selectbox("Permit Type", PARKING_CATEGORIES)
    gender = st.selectbox("Gender", SUPPORTED_GENDERS)

with col2:
    residency = st.selectbox("Residency", SUPPORTED_RESIDENCY)
    arrival_time = st.text_input("Arrival Time (HH:MM)", value="08:30")

selected_lot_label = st.selectbox(
    "Choose a Parking Lot",
    lot_options if lot_options else ["No parking lot data available"]
)

check_clicked = st.button("🔍 Check Eligibility", use_container_width=True, type="primary")

# -----------------------------
# Eligibility Result
# -----------------------------
if check_clicked:
    if lots_df.empty:
        st.error("Parking lot data is missing.")
    else:
        selected_lot = lot_map.get(selected_lot_label)

        user_profile = {
            "permit_type": permit_type,
            "gender": gender,
            "residency": residency,
            "arrival_time": arrival_time
        }

        details = get_eligibility_details(user_profile, selected_lot)

        # Result card
        if details["eligible"]:
            st.markdown("""
            <div class="result-card pass">
                <div class="result-text pass">✅ You are allowed to park in this lot</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-card fail">
                <div class="result-text fail">❌ You are NOT allowed to park in this lot</div>
            </div>
            """, unsafe_allow_html=True)

        # Rule breakdown grid
        st.markdown('<div class="section-head">Rule Breakdown</div>', unsafe_allow_html=True)

        rules = [
            ("Permit", details["permit_ok"]),
            ("Gender", details["gender_ok"]),
            ("Residency", details["residency_ok"]),
            ("Category", details["category_ok"]),
            ("Time", details["time_ok"]),
            ("Restriction", details["restricted_ok"]),
        ]

        rule_cols = st.columns(3)
        for idx, (rule_name, passed) in enumerate(rules):
            with rule_cols[idx % 3]:
                if passed:
                    st.success(f"**{rule_name}**\n\n✅ Pass")
                else:
                    st.error(f"**{rule_name}**\n\n❌ Fail")

        # Lot Information
        st.markdown('<div class="section-head">Lot Information</div>', unsafe_allow_html=True)

        info_items = [
            ("Lot ID", selected_lot.get("lot_id", "N/A")),
            ("Lot Name", selected_lot.get("lot_name", "N/A")),
            ("Arabic Name", selected_lot.get("lot_name_ar", "N/A")),
            ("Zone", selected_lot.get("zone", "N/A")),
            ("Category", selected_lot.get("category", "N/A")),
            ("Nearest Gate", selected_lot.get("nearest_gate", "N/A")),
            ("Allowed Permits", selected_lot.get("allowed_permits", "N/A")),
            ("Gender Access", selected_lot.get("gender_access", "N/A")),
            ("Allowed Residency", selected_lot.get("allowed_residency", "N/A")),
            ("Time Rules", selected_lot.get("time_rules", "N/A")),
            ("Restricted", selected_lot.get("restricted", "false")),
        ]

        for label, value in info_items:
            st.markdown(f'<div class="info-card" style="margin-bottom:2px;padding:10px 18px;"><div class="info-row"><span class="info-label">{label}</span><span class="info-value">{value}</span></div></div>', unsafe_allow_html=True)

# Footer
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)