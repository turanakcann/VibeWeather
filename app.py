# app.py – SON HALİ

import streamlit as st
import web_connection
import weather_set
import ai_assistant
import vector_store
import time

def main():
    st.set_page_config(page_title="VibeWeather", page_icon="logo.png", layout="centered")

    # LOGO (isteğe bağlı ama çok yakışır)
    try:
        st.image("logo.png", width=100)
    except:
        pass  # logo yoksa hata verme

    # DB başlatma (sessiz)
    if "db_ready" not in st.session_state:
        with st.spinner(""):
            placeholder = st.empty()
            placeholder.markdown("<h3 style='text-align:center;color:#ff3366;'>VibeWeather uyanıyor...</h3>", unsafe_allow_html=True)
            if vector_store.initialize_vector_db() is None:
                st.error("Bağlantı hatası! API key kontrol et.")
                st.stop()
            placeholder.empty()
            st.session_state.db_ready = True

    # ARTIK BURADA "Hava durumuna göre..." YAZISI YOK!
    # Sadece web_connection'dan gelen UI var

    konum_verisi, is_push_button = web_connection.render_ui_and_get_location()

    if "weather_cache" not in st.session_state:
        st.session_state.weather_cache = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # İlk giriş butonları
    if not st.session_state.weather_cache and not is_push_button:
        st.markdown("<h2 style='text-align:center;color:#fff;'>Bugün hangi vibe'dasın?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#aaa;font-size:18px;margin-bottom:30px;'>Şehir gir, sana özel film + içecek önerisi al</p>", unsafe_allow_html=True)
        cols = st.columns(6)
        sehirler = ["İstanbul", "Ankara", "İzmir", "Şanlıurfa", "Ağrı", "Van"]
        for col, sehir in zip(cols, sehirler):
            if col.button(sehir, use_container_width=True):
                konum_verisi = sehir
                is_push_button = True

    # Ana işlem
    if is_push_button or (konum_verisi and not st.session_state.weather_cache):
        if not konum_verisi:
            st.stop()

        with st.spinner(""):
            w = weather_set.get_weather_data(konum_verisi)
            if w.get("error"):
                st.error(w["error"])
                st.stop()

            st.session_state.weather_cache = w
            q = f"{w['condition']} {w['current_degree']} derece"
            movies = vector_store.search_by_weather(q, "movies")
            drinks = vector_store.search_by_weather(q, "drinks")

            resp = ai_assistant.get_chat_response([], w, movies, drinks)
            st.session_state.messages = [{"role": "assistant", "content": resp}]

    # STICKY KART + DİNAMİK ARKA PLAN + RESPONSIVE
    if st.session_state.weather_cache:
        w = st.session_state.weather_cache
        temp = float(w['current_degree'])
        bg = "heavy+rain+night" if "yağ" in w['condition'].lower() else \
             "sunny+day" if "güneş" in w['condition'].lower() else \
             "cloudy+sky" if "bulut" in w['condition'].lower() else "cozy+weather"

        card_color = "#1e3c72" if temp <= 15 else "#ee5a24"

                # RESPONSIVE HAVA KARTI – MOBİLDE GÖRÜNMEZ, SADECE MASAÜSTÜNDE GÖRÜNÜR
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)),
                        url("https://source.unsplash.com/random/2560x1440/?{bg}&{temp}") fixed cover center fixed;
        }}

        /* SADECE 769px VE ÜZERİ EKRANLARDA GÖSTER (telefonlarda kart yok) */
        @media (min-width: 769px) {{
            .weather-card {{
                position: fixed;
                top: 20px;
                right: 20px;
                width: 340px;
                background: {card_color};
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 24px;
                padding: 22px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.6);
                z-index: 9999;
                color: white;
                text-align: center;
            }}
        }}
        </style>

        <!-- Sadece masaüstünde göster -->
        <div class="weather-card">
            <div style="font-size:56px;">{"Heavy Rain" if "yağ" in w['condition'].lower() else "Sunny" if "güneş" in w['condition'].lower() else "Cloudy"}</div>
            <div style="font-size:28px;font-weight:bold;margin:10px 0">{w['city']}</div>
            <div style="font-size:60px;font-weight:900;color:#ff3366;margin:12px 0">{temp}°C</div>
            <div style="font-size:18px">{w['condition']}</div>
            <div style="font-size:14px;opacity:0.7;margin-top:8px">
                Nem: %{w['humidity']} • Hissedilen: {w.get('feelslike_c', temp)}°C
            </div>
        </div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Başka bir yer? (Örn: Urla, Şırnak, Hakkari)"):
            with st.chat_message("user"):
                st.markdown(prompt)
            new_city = ai_assistant.extract_city_request(prompt)
            if not new_city:
                st.error("Sadece şehir/ilçe adı gir lütfen")
                st.stop()
            new_w = weather_set.get_weather_data(new_city)
            if new_w.get("error"):
                st.error(new_w["error"])
                st.stop()
            st.session_state.weather_cache = new_w
            q = f"{new_w['condition']} {new_w['current_degree']} derece"
            movies = vector_store.search_by_weather(q, "movies")
            drinks = vector_store.search_by_weather(q, "drinks")
            resp = ai_assistant.get_chat_response([], new_w, movies, drinks)
            with st.chat_message("assistant"):
                st.markdown(resp)
            st.rerun()

if __name__ == "__main__":
    main()