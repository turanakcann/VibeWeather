# web_connection.py — YENİ HALİ (kopyala-yapıştır yap)

import streamlit as st
from streamlit_js_eval import get_geolocation
import time

def render_ui_and_get_location():
    st.markdown("<h1 style='text-align: center; color:#ff3366; margin-bottom:10px;'>VibeWeather</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#ccc; margin-bottom:40px;'>Hava durumuna göre film + içecek önerisi</p>", unsafe_allow_html=True)

    # ORTALI TEXT INPUT
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        manual_input = st.text_input(
            "",
            placeholder="Şehir yaz... (Örn: Urla, Şırnak, Hakkari)",
            label_visibility="collapsed",
            key="city_input"
        )

    # GPS BUTONU (küçük, sağ altta 5 saniyelik bildirim)
    if st.button("Konumumu Kullan", use_container_width=False):
        with st.spinner("Konum alınıyor..."):
            geo = get_geolocation()
            if geo and geo.get("coords"):
                lat = geo["coords"]["latitude"]
                lon = geo["coords"]["longitude"]
                # Koordinat yerine şehir ismi gelsin (weather_set.py'de zaten yapıyor)
                placeholder = st.empty()
                placeholder.success("Konum alındı! Yükleniyor...")
                time.sleep(3)
                placeholder.empty()
                return f"{lat},{lon}", True
            else:
                st.error("Konum alınamadı")
                return None, False

    # YEŞİL "GPS Konumu Hazır" YAZISI KALKMASIN DİYE
    # Hiçbir şey yazdırma, sadece buton olsun

    calc_button = st.button('Modumu Yakala & Önerileri Getir', use_container_width=True, type="primary")

    if manual_input:
        return manual_input.strip(), calc_button
    return None, calc_button