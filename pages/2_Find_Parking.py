import streamlit as st

from config import (
    APP_FOOTER,
    SUPPORTED_GENDERS,
    SUPPORTED_RESIDENCY,
    SUPPORTED_WALKING_TOLERANCE,
    PARKING_CATEGORIES
)
from utils.loaders import load_buildings, load_gates
from services.recommendation_engine import (
    get_best_lot,
    get_recommended_lots,
    get_alternative_lots
)
from services.occupancy_service import get_parking_status_table

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .fp-header {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    .fp-subtitle {
        font-size: 15px;
        color: rgba(255,255,255,0.5);
        margin-bottom: 20px;
    }

    /* Filter tabs */
    .filter-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
    }
    .filter-tab {
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        border: 1px solid rgba(255,255,255,0.15);
        color: rgba(255,255,255,0.7);
        background: transparent;
        transition: all 0.2s;
    }
    .filter-tab.active {
        background: linear-gradient(135deg, #006C35 0%, #00913E 100%);
        color: white;
        border-color: #006C35;
    }

    /* Parking lot card */
    .parking-card {
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
    .parking-card:hover {
        border-color: rgba(0,108,53,0.3);
        transform: translateX(3px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .parking-card-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .p-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 800;
        color: white;
        flex-shrink: 0;
    }
    .p-icon.available { background: linear-gradient(135deg, #006C35, #2ECC71); }
    .p-icon.busy { background: linear-gradient(135deg, #E67E22, #F1C40F); }
    .p-icon.full { background: linear-gradient(135deg, #C0392B, #E74C3C); }

    .parking-info .pk-name {
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .parking-info .pk-avail {
        font-size: 13px;
        color: rgba(255,255,255,0.5);
    }
    .parking-info .pk-walk {
        font-size: 12px;
        color: rgba(255,255,255,0.35);
        font-weight: 500;
    }

    .parking-card-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .arrow-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .arrow-btn.available { background: #2ECC71; color: white; }
    .arrow-btn.busy { background: #F1C40F; color: white; }
    .arrow-btn.full { background: #E74C3C; color: white; }

    /* Start Navigation button */
    .start-nav-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: linear-gradient(135deg, #006C35 0%, #00913E 100%);
        color: white;
        padding: 14px;
        border-radius: 12px;
        font-size: 17px;
        font-weight: 700;
        margin-top: 20px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,108,53,0.3);
        transition: all 0.2s;
    }
    .start-nav-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0,108,53,0.4);
    }

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
# Header
# -----------------------------
st.markdown('<div class="fp-header">Find Your Parking</div>', unsafe_allow_html=True)
st.markdown('<div class="fp-subtitle">Search and filter KFUPM campus parking lots</div>', unsafe_allow_html=True)

# -----------------------------
# Search bar
# -----------------------------
search_query = st.text_input(
    "🔍 Search destination",
    placeholder="Search by lot name, building, or zone...",
    label_visibility="collapsed"
)

# -----------------------------
# Filter tabs (using Streamlit columns as buttons)
# -----------------------------
col_all, col_avail, col_full, _ = st.columns([1, 1, 1, 3])

if "parking_filter" not in st.session_state:
    st.session_state.parking_filter = "All"

with col_all:
    if st.button("🟢 All", use_container_width=True, type="primary" if st.session_state.parking_filter == "All" else "secondary"):
        st.session_state.parking_filter = "All"
with col_avail:
    if st.button("✅ Available", use_container_width=True, type="primary" if st.session_state.parking_filter == "Available" else "secondary"):
        st.session_state.parking_filter = "Available"
with col_full:
    if st.button("🔴 Full", use_container_width=True, type="primary" if st.session_state.parking_filter == "Full" else "secondary"):
        st.session_state.parking_filter = "Full"

# -----------------------------
# Load parking data
# -----------------------------
parking_df = get_parking_status_table()

if not parking_df.empty:
    # Apply filter
    if st.session_state.parking_filter == "Available":
        parking_df = parking_df[parking_df["status"] != "full"].copy()
    elif st.session_state.parking_filter == "Full":
        parking_df = parking_df[parking_df["status"] == "full"].copy()

    # Apply search
    if search_query:
        search_lower = search_query.lower()
        parking_df = parking_df[
            parking_df.apply(lambda row:
                search_lower in str(row.get("lot_name", "")).lower() or
                search_lower in str(row.get("zone", "")).lower() or
                search_lower in str(row.get("lot_name_ar", "")).lower() or
                search_lower in str(row.get("category", "")).lower(),
                axis=1
            )
        ].copy()

    # Render lot cards
    st.markdown('<div class="section-head">Parking Lots</div>', unsafe_allow_html=True)

    for _, row in parking_df.iterrows():
        lot_name = row.get("lot_name", "Unknown")
        status = row.get("status", "available")
        occupied = int(row.get("occupied", 0))
        capacity = int(row.get("capacity", 0))
        available = int(row.get("available_spaces", 0))
        zone = row.get("zone", "")

        # Calculate walking time estimate (rough)
        walking = row.get("walking_time_min", None)
        if walking is None or walking == 0:
            # Use a simple estimate based on position
            walking = "—"
        else:
            walking = f"{walking} min walk"

        avail_text = f"{available} / {capacity} available"
        if status == "full":
            avail_text = f"{occupied} / {capacity} available"
            walking = "FULL"

        st.markdown(f"""
        <div class="parking-card">
            <div class="parking-card-left">
                <div class="p-icon {status}">P</div>
                <div class="parking-info">
                    <div class="pk-name">{lot_name}</div>
                    <div class="pk-avail">{avail_text}</div>
                    <div class="pk-walk">{walking}</div>
                </div>
            </div>
            <div class="parking-card-right">
                <div class="arrow-btn {status}">➜</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Start Navigation button
    st.markdown('<div class="start-nav-btn">Start Navigation</div>', unsafe_allow_html=True)
else:
    st.warning("No parking data available. Please check your data files.")

# -----------------------------
# User Profile Form (collapsed)
# -----------------------------
with st.expander("⚙️ Advanced — Set Your Profile", expanded=False):
    buildings_df = load_buildings()
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

    with st.form("parking_form"):
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

        submitted = st.form_submit_button("🔍 Find Best Parking", use_container_width=True)

    if submitted:
        if buildings_df.empty:
            st.error("Building data is missing.")
        else:
            destination = building_map.get(destination_label)
            preferred_gate = gate_map.get(preferred_gate_label) if not gates_df.empty else None

            user_profile = {
                "permit_type": permit_type,
                "gender": gender,
                "residency": residency,
                "arrival_time": arrival_time,
                "destination": destination,
                "walking_tolerance": walking_tolerance,
                "preferred_gate": preferred_gate
            }

            best_lot = get_best_lot(user_profile)
            recommended_lots = get_recommended_lots(user_profile, top_n=5)

            if best_lot is None or recommended_lots.empty:
                st.warning("No suitable parking lots were found for your profile.")
            else:
                st.success(f"✅ Best Lot: **{best_lot['lot_name']}** — {int(best_lot.get('available_spaces', 0))} spaces, {best_lot.get('walking_time_min', 'N/A')} min walk")

                display_columns = [
                    "lot_id", "lot_name", "zone", "category", "nearest_gate",
                    "available_spaces", "walking_time_min", "status", "final_score"
                ]
                available_display_columns = [
                    column for column in display_columns if column in recommended_lots.columns
                ]
                st.dataframe(
                    recommended_lots[available_display_columns].copy(),
                    use_container_width=True
                )

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)