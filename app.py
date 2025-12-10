# app.py – SON HALİ (hepsi düzeltildi)

import streamlit as st
import web_connection
import weather_set
import ai_assistant
import vector_store

def main():
    st.set_page_config(page_title="VibeWeather", page_icon="logo.png", layout="centered")

    # DB başlatma
    if "db_ready" not in st.session_state:
        with st.spinner(""):
            placeholder = st.empty()
            placeholder.markdown("<h3 style='text-align:center;color:#ff6b35;'>VibeWeather hazırlanıyor...</h3>", unsafe_allow_html=True)
            if vector_store.initialize_vector_db() is None:
                st.error("Pinecone bağlantı hatası!")
                st.stop()
            placeholder.empty()
            st.session_state.db_ready = True

    konum_verisi, is_push_button = web_connection.render_ui_and_get_location()

    if "weather_cache" not in st.session_state:
        st.session_state.weather_cache = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # İlk giriş
    if not st.session_state.weather_cache and not is_push_button:
        st.markdown("<h2 style='text-align:center;color:#fff;margin-top:40px;'>Bugün hangi vibe'dasın?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#ffdda1;font-size:18px;margin-bottom:40px;'>Şehir gir, sana özel film + içecek önerisi al</p>", unsafe_allow_html=True)

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

    # HAVA KARTI – TAMAMEN TÜRKÇE + RESPONSIVE
    if st.session_state.weather_cache:
        w = st.session_state.weather_cache
        temp = float(w['current_degree'])

        # Türkçe durum çevirisi
        durum_dict = {
            "Sunny": "Güneşli", "Clear": "Açık", "Partly cloudy": "Parçalı Bulutlu",
            "Cloudy": "Bulutlu", "Overcast": "Kapalı", "Rain": "Yağmurlu", "Snow": "Karlı",
            "Mist": "Sisli", "Fog": "Sisli", "Thunder": "Gök Gürültülü"
        }
        turkce_durum = w['condition']
        for eng, tr in durum_dict.items():
            if eng.lower() in w['condition'].lower():
                turkce_durum = tr
                break

        emoji = "Güneşli" if "güneş" in turkce_durum.lower() else \
                "Yağmurlu" if "yağ" in turkce_durum.lower() else \
                "Karlı" if "kar" in turkce_durum.lower() else "Bulutlu"

        st.markdown(f"""
        <style>
        .stApp {{background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.9)), 
                 url("https://source.unsplash.com/random/2560x1440/?cozy+winter+night&{temp}") fixed cover center}}
        @media (min-width: 769px) {{
            .weather-card {{
                position: fixed; top: 20px; right: 20px; width: 340px;
                background: linear-gradient(135deg, #ee5a24, #ff6b35);
                backdrop-filter: blur(16px); border-radius: 24px; padding: 22px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.7); z-index: 9999;
                color: white; text-align: center; border: 1px solid #ff9f1c;
            }}
        }}
        </style>

        <div class="weather-card">
            <div style="font-size:56px;">{emoji}</div>
            <div style="font-size:28px;font-weight:bold;margin:10px 0">{w['city']}</div>
            <div style="font-size:60px;font-weight:900;color:#fff;margin:12px 0">{temp}°C</div>
            <div style="font-size:18px">{turkce_durum}</div>
            <div style="font-size:14px;opacity:0.8;margin-top:8px">
                Nem: %{w['humidity']} • Hissedilen: {w.get('feelslike_c', temp)}°C
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ÖNERİLER
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # CHAT – TÜM PARAMETRELER KULLANILIYOR
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            prompt = st.chat_input("Sohbet et, şehir sor, kategori seç... (Örn: Ankara'da korku filmi öner)")
        with col1:
            kategori = st.selectbox("Film Türü:", ["Herhangi", "Aksiyon", "Komedi", "Drama", "Korku", "Bilim Kurgu"], key="film_cat")
        with col3:
            icecek = st.selectbox("İçecek:", ["Herhangi", "Sıcak", "Soğuk", "Kahve", "Çay"], key="icecek_pref")

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)

            # ŞEHİR VAR MI?
            new_city = ai_assistant.extract_city_request(prompt)
            current_city = st.session_state.weather_cache['city'] if st.session_state.weather_cache else "İstanbul"

            city_to_use = new_city or current_city
            new_w = weather_set.get_weather_data(city_to_use)
            if new_w.get("error"):
                st.error(new_w["error"])
                st.stop()

            st.session_state.weather_cache = new_w

            # PROMPT OLUŞTUR – KATEGORİ + İÇECEK + KULLANICI MESAJI
            full_prompt = f"{prompt} | {kategori} film | {icecek} içecek"
            q = f"{new_w['condition']} {new_w['current_degree']} derece {kategori.lower()} {icecek.lower()}"
            movies = vector_store.search_by_weather(q, "movies")
            drinks = vector_store.search_by_weather(q, "drinks")

            resp = ai_assistant.get_chat_response([{"role": "user", "content": full_prompt}], new_w, movies, drinks)

            with st.chat_message("assistant"):
                st.markdown(resp)
            st.rerun()

if __name__ == "__main__":
    main()