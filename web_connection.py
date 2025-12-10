# web_connection.py – KONUM TEK TIK + TÜRKİYE ZORLAMASI

import streamlit as st
from streamlit_js_eval import get_geolocation
import time

def render_ui_and_get_location():
    st.markdown("<h1 style='text-align:center;color:#ff6b35;margin:30px 0;'>VibeWeather</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        manual_input = st.text_input("", placeholder="Şehir yaz... (Örn: Çankırı, Van, Hakkari)", label_visibility="collapsed")

    # GPS – TEK TIKTA ÇALIŞIYOR + TÜRKİYE ZORLAMASI
    if st.button("Konumumu Kullan", use_container_width=True, type="secondary"):
        placeholder = st.empty()
        placeholder.info("Konum alınıyor...")
        geo = get_geolocation()
        if geo and geo.get("coords"):
            lat = geo["coords"]["latitude"]
            lon = geo["coords"]["longitude"]
            # TÜRKİYE ZORLAMASI
            placeholder.success("Konum alındı! Türkiye’de olduğun varsayılıyor...")
            time.sleep(1.5)
            placeholder.empty()
            return f"{lat},{lon}, Turkey", True
        else:
            placeholder.error("Konum alınamadı. Manuel şehir gir.")
            time.sleep(2)
            placeholder.empty()
            return None, False

    calc_button = st.button('Önerileri Getir', use_container_width=True, type="primary")
    return manual_input.strip() if manual_input else None, calc_button