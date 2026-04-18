import streamlit as st
import pandas as pd

from config import APP_FOOTER
from services.occupancy_service import (
    get_summary_metrics,
    get_parking_status_table,
    get_hotspot_lots,
    get_underused_lots,
    get_zone_summary
)

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
st.markdown('<div class="page-header">📊 Admin Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Campus parking analytics and occupancy overview</div>', unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
metrics = get_summary_metrics()
parking_df = get_parking_status_table()

if parking_df.empty:
    st.error("No parking data available. Please check your data files.")
else:
    # -----------------------------
    # Key Metrics
    # -----------------------------
    st.markdown('<div class="section-head">Key Metrics</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Lots", metrics["total_lots"])
    with col2:
        st.metric("Total Capacity", metrics["total_capacity"])
    with col3:
        st.metric("Total Occupied", metrics["total_occupied"])
    with col4:
        st.metric("Avg Occupancy", f"{metrics['average_occupancy_percent']}%")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Available Lots", metrics["available_lots"])
    with col6:
        st.metric("Busy Lots", metrics["busy_lots"])
    with col7:
        st.metric("Full Lots", metrics["full_lots"])
    with col8:
        st.metric("Free Spaces", metrics["total_available_spaces"])

    st.markdown("---")

    # -----------------------------
    # Occupancy Distribution Chart
    # -----------------------------
    st.markdown('<div class="section-head">Occupancy Distribution</div>', unsafe_allow_html=True)

    if "occupancy_percent" in parking_df.columns and "lot_name" in parking_df.columns:
        chart_df = parking_df[["lot_name", "occupancy_percent"]].copy()
        chart_df = chart_df.set_index("lot_name")
        st.bar_chart(chart_df, use_container_width=True, color="#006C35")

    st.markdown("---")

    # -----------------------------
    # Status Breakdown
    # -----------------------------
    st.markdown('<div class="section-head">Status Breakdown</div>', unsafe_allow_html=True)

    if "status" in parking_df.columns:
        status_counts = parking_df["status"].value_counts()
        col1, col2 = st.columns([1, 2])
        with col1:
            for status_name, count in status_counts.items():
                emoji = "🟢" if status_name == "available" else ("🟡" if status_name == "busy" else "🔴")
                st.write(f"{emoji} **{status_name.capitalize()}**: {count} lots")
        with col2:
            st.bar_chart(status_counts, use_container_width=True, color="#006C35")

    st.markdown("---")

    # -----------------------------
    # Zone Summary
    # -----------------------------
    st.markdown('<div class="section-head">Zone Summary</div>', unsafe_allow_html=True)

    zone_summary = get_zone_summary()
    if not zone_summary.empty:
        st.dataframe(zone_summary, use_container_width=True)
    else:
        st.info("No zone data available.")

    st.markdown("---")

    # -----------------------------
    # Hotspot & Underused Lots
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-head">🔥 Hotspot Lots (Most Full)</div>', unsafe_allow_html=True)
        hotspot = get_hotspot_lots(top_n=5)
        if not hotspot.empty:
            display_cols = ["lot_name", "zone", "occupied", "capacity", "occupancy_percent", "status"]
            avail_cols = [c for c in display_cols if c in hotspot.columns]
            st.dataframe(hotspot[avail_cols], use_container_width=True)
        else:
            st.info("No data.")

    with col2:
        st.markdown('<div class="section-head">💚 Underused Lots (Most Free)</div>', unsafe_allow_html=True)
        underused = get_underused_lots(top_n=5)
        if not underused.empty:
            display_cols = ["lot_name", "zone", "occupied", "capacity", "occupancy_percent", "status"]
            avail_cols = [c for c in display_cols if c in underused.columns]
            st.dataframe(underused[avail_cols], use_container_width=True)
        else:
            st.info("No data.")

    st.markdown("---")

    # -----------------------------
    # Full Parking Data Table
    # -----------------------------
    st.markdown('<div class="section-head">Full Parking Data</div>', unsafe_allow_html=True)

    display_cols = [
        "lot_id", "lot_name", "zone", "category", "nearest_gate",
        "capacity", "occupied", "available_spaces", "occupancy_percent", "status"
    ]
    avail_cols = [c for c in display_cols if c in parking_df.columns]
    st.dataframe(parking_df[avail_cols], use_container_width=True)

# Footer
st.markdown(
    f'<div class="app-footer">{APP_FOOTER}</div>',
    unsafe_allow_html=True
)
