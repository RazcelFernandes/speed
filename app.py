import streamlit as st
from streamlit_js_eval import get_geolocation
from geopy.distance import geodesic
from streamlit_folium import st_folium
import folium
import pandas as pd
import time

# ====================================
# CONFIG PAGE
# ====================================
st.set_page_config(
    page_title="Smart GPS Tracker",
    page_icon="🚗",
    layout="wide"
)

# ====================================
# CUSTOM CSS
# ====================================
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.title {
    font-size: 42px;
    font-weight: bold;
    color: white;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    color: #B0B0B0;
    text-align: center;
    margin-bottom: 30px;
}

.card {
    background-color: #1E1E1E;
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0px 0px 10px rgba(255,255,255,0.05);
}

.speed-box {
    background: linear-gradient(135deg, #00B4DB, #0083B0);
    padding: 35px;
    border-radius: 25px;
    text-align: center;
    color: white;
    font-size: 45px;
    font-weight: bold;
    margin-top: 20px;
}

.status-safe {
    color: #00FF99;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

.status-normal {
    color: #FFD700;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

.status-fast {
    color: red;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ====================================
# HEADER
# ====================================
st.markdown(
    '<div class="title">🚗 Smart GPS Vehicle Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Monitoring kecepatan kendaraan menggunakan GPS HP secara realtime</div>',
    unsafe_allow_html=True
)

# ====================================
# SESSION STATE
# ====================================
if "history" not in st.session_state:
    st.session_state.history = []

if "top_speed" not in st.session_state:
    st.session_state.top_speed = 0

# ====================================
# BUTTON
# ====================================
start = st.button("▶️ Mulai Tracking")

if start:

    # ====================================
    # GPS PERTAMA
    # ====================================
    location1 = get_geolocation(component_key="loc1")

    if location1 is not None:

        lat1 = location1["coords"]["latitude"]
        lon1 = location1["coords"]["longitude"]

        st.success("✅ GPS berhasil terdeteksi")

        # ====================================
        # DASHBOARD
        # ====================================
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="card">
                <h3>📍 Latitude</h3>
                <h2>{lat1:.6f}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <h3>📍 Longitude</h3>
                <h2>{lon1:.6f}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # ====================================
        # MAP
        # ====================================
        st.subheader("🗺️ Lokasi Kendaraan")

        m = folium.Map(location=[lat1, lon1], zoom_start=17)

        folium.Marker(
            [lat1, lon1],
            tooltip="Posisi Kendaraan",
            icon=folium.Icon(color="red", icon="car")
        ).add_to(m)

        st_folium(m, width=1200, height=450)

        # ====================================
        # LOADING
        # ====================================
        st.info("⏱ Menghitung kecepatan kendaraan...")

        point1 = (lat1, lon1)

        time.sleep(5)

        # ====================================
        # GPS KEDUA
        # ====================================
        location2 = get_geolocation(component_key="loc2")

        if location2 is not None:

            lat2 = location2["coords"]["latitude"]
            lon2 = location2["coords"]["longitude"]

            point2 = (lat2, lon2)

            # ====================================
            # HITUNG JARAK
            # ====================================
            distance = geodesic(point1, point2).meters

            # ====================================
            # HITUNG SPEED
            # ====================================
            speed_mps = distance / 5
            speed_kmh = speed_mps * 3.6

            # ====================================
            # UPDATE TOP SPEED
            # ====================================
            if speed_kmh > st.session_state.top_speed:
                st.session_state.top_speed = speed_kmh

            # ====================================
            # SPEED DASHBOARD
            # ====================================
            col_speed1, col_speed2 = st.columns(2)

            with col_speed1:
                st.markdown(f"""
                <div class="speed-box">
                    🚗<br>
                    {speed_kmh:.2f} KM/J
                    <br>
                    <span style="font-size:20px;">
                    Kecepatan Saat Ini
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col_speed2:
                st.markdown(f"""
                <div class="speed-box">
                    🏁<br>
                    {st.session_state.top_speed:.2f} KM/J
                    <br>
                    <span style="font-size:20px;">
                    Top Speed
                    </span>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            # ====================================
            # STATUS
            # ====================================
            if speed_kmh < 20:
                st.markdown(
                    '<div class="status-safe">🟢 Kecepatan Rendah</div>',
                    unsafe_allow_html=True
                )

            elif speed_kmh < 60:
                st.markdown(
                    '<div class="status-normal">🟡 Kecepatan Normal</div>',
                    unsafe_allow_html=True
                )

            else:
                st.markdown(
                    '<div class="status-fast">🔴 Kendaraan Melaju Cepat</div>',
                    unsafe_allow_html=True
                )

            st.write("")

            # ====================================
            # SAVE HISTORY
            # ====================================
            history_data = {
                "Latitude": lat2,
                "Longitude": lon2,
                "Speed (KM/J)": round(speed_kmh, 2)
            }

            st.session_state.history.append(history_data)

            # ====================================
            # HISTORY TABLE
            # ====================================
            st.subheader("📊 Riwayat Kecepatan")

            df = pd.DataFrame(st.session_state.history)

            st.dataframe(df, use_container_width=True)

    else:
        st.error("❌ GPS tidak aktif atau izin lokasi ditolak")