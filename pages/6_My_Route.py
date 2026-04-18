import streamlit as st
import pandas as pd

from config import APP_FOOTER, ASSETS
from utils.loaders import load_buildings
from services.occupancy_service import get_parking_status_table
from utils.helpers import euclidean_distance, calculate_walking_time

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

    .route-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .route-card .route-title {
        font-size: 20px;
        font-weight: 800;
        color: #111;
        margin-bottom: 12px;
    }
    .route-metrics {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
    }
    .route-metric {
        flex: 1;
        text-align: center;
        padding: 12px 8px;
        background: #f5f5f5;
        border-radius: 10px;
    }
    .route-metric .rm-val {
        font-size: 22px;
        font-weight: 800;
        color: #111;
    }
    .route-metric .rm-val.green { color: #006C35; }
    .route-metric .rm-lbl {
        font-size: 11px;
        color: #888;
        text-transform: uppercase;
        margin-top: 2px;
    }

    .route-details {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 16px;
    }
    .route-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .route-row:last-child { border-bottom: none; }
    .route-lbl { font-size: 13px; color: rgba(255,255,255,0.4); }
    .route-val { font-size: 13px; color: #FFFFFF; font-weight: 600; }

    .navigate-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: linear-gradient(135deg, #006C35 0%, #00913E 100%);
        color: white;
        padding: 14px;
        border-radius: 12px;
        font-size: 17px;
        font-weight: 700;
        margin-top: 12px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,108,53,0.3);
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
st.markdown('<div class="page-header">🧭 My Route</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Estimate the route from your lot to your destination</div>', unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
buildings_df = load_buildings()
lots_df = get_parking_status_table()

if buildings_df.empty or lots_df.empty:
    st.error("Required data is missing. Please check buildings and parking data.")
else:
    # Build options
    building_options = []
    building_map = {}

    for _, row in buildings_df.iterrows():
        building_id = str(row["building_id"])
        building_name_en = row.get("building_name_en", row.get("building_name", "Unknown Building"))
        building_name_ar = row.get("building_name_ar", "")

        if building_name_ar:
            label = f"{building_id} - {building_name_en} / {building_name_ar}"
        else:
            label = f"{building_id} - {building_name_en}"

        building_options.append(label)
        building_map[label] = row.to_dict()

    lot_options = []
    lot_map = {}

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

    # User selections
    col1, col2 = st.columns(2)

    with col1:
        selected_lot_label = st.selectbox("🅿️ Select Parking Lot", lot_options)

    with col2:
        selected_building_label = st.selectbox("🏢 Select Destination", building_options)

    calculate_clicked = st.button("🧭 Calculate Route", use_container_width=True, type="primary")

    if calculate_clicked:
        selected_lot = lot_map[selected_lot_label]
        selected_building = building_map[selected_building_label]

        # Get GPS coordinates
        lot_lat = selected_lot.get("lat")
        lot_lon = selected_lot.get("lon")
        building_lat = selected_building.get("lat")
        building_lon = selected_building.get("lon")

        distance_meters = None
        has_coords = False

        if pd.notna(lot_lat) and pd.notna(lot_lon) and pd.notna(building_lat) and pd.notna(building_lon):
            distance_meters = euclidean_distance(lot_lat, lot_lon, building_lat, building_lon)
            has_coords = True

        walking_time = calculate_walking_time(distance_meters)
        dist_str = f"{round(distance_meters)} m" if distance_meters is not None else "N/A"
        status = selected_lot.get("status", "N/A")
        lot_name = str(selected_lot.get("lot_name", "N/A"))
        dest_name = str(selected_building.get("building_name_en", selected_building.get("building_name", "N/A")))

        # Google Maps URLs
        if has_coords:
            gmaps_directions_url = (
                f"https://www.google.com/maps/dir/{lot_lat},{lot_lon}/{building_lat},{building_lon}"
                f"/@{(lot_lat+building_lat)/2},{(lot_lon+building_lon)/2},17z/data=!3m1!4b1!4m2!4m1!3e2"
            )
            gmaps_embed_url = (
                f"https://www.google.com/maps/embed/v1/directions"
                f"?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8"
                f"&origin={lot_lat},{lot_lon}"
                f"&destination={building_lat},{building_lon}"
                f"&mode=walking"
                f"&zoom=17"
            )
        else:
            gmaps_directions_url = "https://www.google.com/maps/place/KFUPM"
            gmaps_embed_url = None

        # Status color for the card
        status_upper = status.upper() if isinstance(status, str) else "N/A"
        status_color = "#2ECC71" if status == "available" else ("#F1C40F" if status == "busy" else "#E74C3C")

        # Route summary card
        st.markdown(f"""
        <div class="route-card">
            <div class="route-title">📍 {lot_name} → 🏢 {dest_name}</div>
            <div class="route-metrics">
                <div class="route-metric">
                    <div class="rm-val">{dist_str}</div>
                    <div class="rm-lbl">Distance</div>
                </div>
                <div class="route-metric">
                    <div class="rm-val green">{walking_time} min</div>
                    <div class="rm-lbl">Walking</div>
                </div>
                <div class="route-metric">
                    <div class="rm-val" style="color:{status_color}">{status_upper}</div>
                    <div class="rm-lbl">Lot Status</div>
                </div>
                <div class="route-metric">
                    <div class="rm-val">{selected_lot.get('nearest_gate', 'N/A')}</div>
                    <div class="rm-lbl">Nearest Gate</div>
                </div>
            </div>
            <a href="{gmaps_directions_url}" target="_blank" style="text-decoration:none;">
                <div class="navigate-btn">🧭 Start Navigation in Google Maps</div>
            </a>
        </div>
        """, unsafe_allow_html=True)

        # Google Maps embed
        if has_coords:
            st.markdown('<div class="section-head">🗺️ Walking Route (Google Maps)</div>', unsafe_allow_html=True)

            # Embed Google Maps with walking directions
            st.markdown(f"""
            <div style="border-radius:14px; overflow:hidden; border:1px solid rgba(255,255,255,0.1); margin-bottom:20px;">
                <iframe
                    width="100%"
                    height="450"
                    style="border:0"
                    loading="lazy"
                    referrerpolicy="no-referrer-when-downgrade"
                    src="https://www.google.com/maps/embed?pb=!1m28!1m12!1m3!1d2000!2d{(lot_lon+building_lon)/2}!3d{(lot_lat+building_lat)/2}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!4m13!3e2!4m5!1s!2s{lot_lat}%2C{lot_lon}!3m2!1d{lot_lat}!2d{lot_lon}!4m5!1s!2s{building_lat}%2C{building_lon}!3m2!1d{building_lat}!2d{building_lon}!5e0!3m2!1sen!2ssa"
                    allowfullscreen>
                </iframe>
            </div>
            """, unsafe_allow_html=True)

            # Also show Streamlit's built-in map with the two points
            st.markdown('<div class="section-head">📍 Route Points on Map</div>', unsafe_allow_html=True)
            map_points = pd.DataFrame([
                {"lat": float(lot_lat), "lon": float(lot_lon)},
                {"lat": float(building_lat), "lon": float(building_lon)}
            ])
            st.map(map_points, use_container_width=True, zoom=16)
        else:
            st.warning("GPS coordinates are not available for the selected lot or building. Map cannot be displayed.")

        # Route Details
        st.markdown('<div class="section-head">Route Details</div>', unsafe_allow_html=True)

        details = [
            ("Parking Lot", lot_name),
            ("Zone", str(selected_lot.get("zone", "N/A"))),
            ("Lot Type", str(selected_lot.get("type", "N/A"))),
            ("Destination", str(dest_name)),
            ("Lot GPS", f"{lot_lat}, {lot_lon}" if has_coords else "N/A"),
            ("Building GPS", f"{building_lat}, {building_lon}" if has_coords else "N/A"),
        ]

        for lbl, val in details:
            st.markdown(f'<div class="route-details" style="margin-bottom:2px;padding:10px 18px;"><div class="route-row"><span class="route-lbl">{lbl}</span><span class="route-val">{val}</span></div></div>', unsafe_allow_html=True)

# Footer
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)