# web_connection.py

import streamlit as st
from streamlit_js_eval import get_geolocation
import time

def render_ui_and_get_location():
    # Başlık
    st.markdown("<h1 style='text-align: center; color:#ff6b35; margin-bottom: 20px;'>VibeWeather 🦆</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#ccc; margin-bottom: 30px;'>Ne izlerken ne içersin?</p>", unsafe_allow_html=True)

    # GPS İsteği Durumu (Hafıza)
    if "gps_clicked" not in st.session_state:
        st.session_state.gps_clicked = False

    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Manuel Giriş
        manual_input = st.text_input("", placeholder="Şehir yaz... (Örn: Kadıköy, İzmir)", label_visibility="collapsed")

    with col2:
        # GPS Butonu (Tıklanınca hafızayı True yapar)
        if st.button("📍 GPS", use_container_width=True, help="Konumumu Bul"):
            st.session_state.gps_clicked = True

    # --- KONUM MANTIĞI ---
    
    # 1. Manuel Giriş Varsa (En Yüksek Öncelik)
    if manual_input:
        # Manuel girildiyse GPS isteğini iptal et
        st.session_state.gps_clicked = False 
        return manual_input, True

    # 2. GPS Butonuna Basıldıysa
    if st.session_state.gps_clicked:
        # Konum verisini çekmeye çalış
        gps_data = get_geolocation(component_key="gps_tracker")
        
        if gps_data and gps_data.get("coords"):
            lat = gps_data["coords"]["latitude"]
            lon = gps_data["coords"]["longitude"]
            # Konum alındı, işlemi bitir
            st.session_state.gps_clicked = False 
            return f"{lat},{lon}", True
        else:
            # Veri henüz gelmediyse kullanıcıyı beklet (Streamlit sayfayı yeniler ve tekrar dener)
            st.info("Uyduya bağlanılıyor... 🛰️")
            time.sleep(1) # Çok hızlı dönmesin diye minik bekleme
            return None, False # Henüz hazır değil

    # 3. Ana Tetikleyici Buton
    calc_button = st.button('Modumu Yakala & Önerileri Getir 🚀', use_container_width=True, type="primary")
    
    return None, calc_button