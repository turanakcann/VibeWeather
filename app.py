# app.py

import streamlit as st
import sqlite3
import time
import web_connection
import weather_set
import ai_assistant
import vector_store

def main():
    # --- SAYFA AYARLARI ---
    st.set_page_config(page_title="VibeWeather", page_icon="🦆", layout="centered")

    # --- SIDEBAR (FİLTRELER & GEÇMİŞ) ---
    with st.sidebar:
        st.header("⚙️ Tercihler")
        
        # 1. FİLTRELER (Burada olunca SABİT kalırlar)
        film_kategorileri = [
            "Karışık (Önerilen)", "Aksiyon / Macera", "Bilim Kurgu / Fantastik", 
            "Komedi", "Dram", "Gerilim / Gizem", "Korku", "Romantik", 
            "Suç / Polisiye", "Animasyon / Anime", "Belgesel / Biyografi"
        ]
        kategori_secim = st.selectbox("🎬 Film Türü:", film_kategorileri, key="sb_film")
        
        icecek_kategorileri = [
            "Karışık (Önerilen)", "Sıcak", "Soğuk", "Kahve", "Çay", "Meyveli", "Alkolsüz Kokteyl"
        ]
        icecek_secim = st.selectbox("🥤 İçecek:", icecek_kategorileri, key="sb_icecek")
        
        st.markdown("---")
        
        # 2. GEÇMİŞ SOHBETLER
        st.header("🗂️ Geçmiş")
        try:
            conn = sqlite3.connect('vibeweather_chat.db')
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY, request TEXT, response TEXT)')
            c.execute("SELECT id, request, response FROM chats ORDER BY id DESC LIMIT 10")
            rows = c.fetchall()
            conn.close()
            
            if rows:
                for chat_id, req, res in rows:
                    btn_label = req[:22] + "..." if len(req) > 22 else req
                    if st.button(f"💬 {btn_label}", key=f"hist_{chat_id}", use_container_width=True):
                        st.session_state.messages = [
                            {"role": "user", "content": req},
                            {"role": "assistant", "content": res}
                        ]
                        st.rerun()
            else:
                st.caption("Henüz geçmiş yok.")
        except:
            st.error("Geçmiş yüklenemedi.")

        st.markdown("---")
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # --- BAŞLANGIÇ ---
    if "db_ready" not in st.session_state:
        with st.spinner("Sistem hazırlanıyor..."):
            if vector_store.initialize_vector_db() is None:
                st.error("Veritabanı hatası!")
                st.stop()
            st.session_state.db_ready = True

    if "last_top_location" not in st.session_state: st.session_state.last_top_location = None
    if "weather_cache" not in st.session_state: st.session_state.weather_cache = None
    if "messages" not in st.session_state: st.session_state.messages = []

    # CSS (TURUNCU KART TASARIMI)
    st.markdown("""
    <style>
    .weather-card {
        background: linear-gradient(135deg, #FF512F, #DD2476); /* Turuncu-Pembe Gradient */
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        border: none;
        box-shadow: 0 10px 30px rgba(221, 36, 118, 0.4);
        margin-top: 20px;
        margin-bottom: 30px;
        color: white;
    }
    .weather-temp { font-size: 64px; font-weight: 800; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .weather-city { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .weather-desc { font-size: 20px; font-weight: 500; opacity: 0.9; }
    .weather-detail { font-size: 14px; margin-top: 10px; opacity: 0.8; }
    
    /* Yan menü butonu */
    section[data-testid="stSidebar"] button { text-align: left; }
    </style>
    """, unsafe_allow_html=True)

    # 1. UI ve Konum Al
    konum_verisi, is_process_triggered = web_connection.render_ui_and_get_location()

    # 2. ANA İŞLEM (GPS/Manuel)
    if is_process_triggered and konum_verisi:
        # Eğer yeni bir üst konum geldiyse çalıştır
        if konum_verisi != st.session_state.last_top_location or st.session_state.weather_cache is None:
            with st.spinner(f"🚀 '{konum_verisi}' analiz ediliyor..."):
                w = weather_set.get_weather_data(konum_verisi)
                
                if w.get("error"):
                    st.error(w["error"])
                else:
                    st.session_state.weather_cache = w
                    st.session_state.last_top_location = konum_verisi
                    
                    # İlk Sorgu
                    prefs = f"Tercih: {kategori_secim}, İçecek: {icecek_secim}"
                    q = f"{w['condition']} {w['current_degree']} derece {prefs}"
                    movies = vector_store.search_by_weather(q, "movies")
                    drinks = vector_store.search_by_weather(q, "drinks")
                    
                    st.session_state.messages = []
                    resp = ai_assistant.get_chat_response([], w, movies, drinks, user_preferences=prefs)
                    st.session_state.messages.append({"role": "assistant", "content": resp})

    # --- EKRAN GÖSTERİMİ ---
    
    # HAVA DURUMU KARTI
    if st.session_state.weather_cache:
        w = st.session_state.weather_cache
        country_display = w.get('country', 'TR')

        st.markdown(f"""
        <div class="weather-card">
            <div class="weather-desc">{w['condition']}</div>
            <div class="weather-city">{w['city']}</div>
            <div class="weather-temp">{w['current_degree']}°C</div>
            <div class="weather-detail">{country_display} | Nem: %{w['humidity']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # SOHBET ALANI
        st.subheader("💬 Sohbet")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # CHAT INPUT
        if prompt := st.chat_input("Başka bir yer? (Örn: Urla) veya 'Film öner'"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Dedektif
            new_city = ai_assistant.extract_city_request(prompt)
            active_w = st.session_state.weather_cache
            location_changed = False

            # Şehir değişimi
            if new_city:
                with st.status(f"🌍 {new_city} aranıyor...") as status:
                    new_w_data = weather_set.get_weather_data(new_city)
                    if not new_w_data.get("error"):
                        st.session_state.weather_cache = new_w_data
                        active_w = new_w_data
                        status.update(label=f"✅ {new_w_data['city']} bulundu!", state="complete")
                        location_changed = True
                    else:
                        status.update(label="❌ Bulunamadı", state="error")
            
            # Cevap Üret
            if active_w:
                prefs = f"Tür: {kategori_secim}, İçecek: {icecek_secim}"
                search_q = f"{active_w['condition']} {active_w['current_degree']} derece {prompt} {prefs}"
                
                movies = vector_store.search_by_weather(search_q, "movies")
                drinks = vector_store.search_by_weather(search_q, "drinks")
                
                with st.spinner("Yazıyor..."):
                    ai_response = ai_assistant.get_chat_response(
                        st.session_state.messages, active_w, movies, drinks, user_preferences=prefs
                    )
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant"):
                    st.markdown(ai_response)

                try:
                    conn = sqlite3.connect('vibeweather_chat.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO chats (request, response) VALUES (?, ?)", (prompt, ai_response))
                    conn.commit()
                    conn.close()
                except: pass

                if location_changed:
                    time.sleep(1)
                    st.rerun()

if __name__ == '__main__':
    main()