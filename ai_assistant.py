import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('GPT_API_KEY'))

def extract_city_request(user_input):
    """
    Kullanıcı mesajından şehir ismini çeker.
    """
    system_msg = """
    GÖREV: Kullanıcı mesajındaki lokasyon ismini bul.
    KURALLAR: Sadece il veya ilçe ismini yalın halde ver. Yoksa null ver.
    ÇIKTI JSON: {"city": "ŞehirAdı"}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_input}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content).get("city")
    except:
        return None

def get_chat_response(messages_history, weather_info, movie_data, drink_data, user_preferences=""):
    """
    user_preferences: Kullanıcının selectbox'tan seçtiği kategori ve içecek türü.
    """
    
    system_message = f"""
    Sen VibeWeather asistanısın.
    
    MEVCUT DURUM:
    📍 Konum: {weather_info['city']}
    🌡️ Hava: {weather_info['current_degree']}°C, {weather_info['condition']}
    
    KULLANICI TERCİHLERİ:
    {user_preferences}
    *(Kullanıcı aksi bir şey demedikçe bu tercihleri uygula)*
    
    VERİTABANI ÖNERİLERİ:
    🎬 Filmler: {movie_data}
    🥤 İçecekler: {drink_data}
    
    ⚠️ KESİN KURALLAR (GUARDRAILS):
    1. SADECE Film/Dizi, İçecek ve Hava Durumu konuş. Başka konuları (siyaset, spor vb.) nazikçe reddet.
    
    📝 CEVAP FORMATI VE STİLİ (ÖNEMLİ):
    - **Ton:** Samimi, enerjik ve emojili olsun.
    - **Uzunluk:** Cevapları çok kısa kesip atma. Önerdiğin filmin konusuna veya içeceğin tadına kısaca değinerek cevabı biraz zenginleştir (Normalden %5-10 daha detaylı).
    - **YAPI (ÇOK ÖNEMLİ):** - Önce hava durumuna dair kısa bir yorum yap.
      - Sonra **FİLM** önerini bir paragrafta anlat.
      - Daha sonra **İÇECEK** önerini TAMAMEN AYRI bir paragrafta anlat.
      - (Film ve İçeceği aynı paragrafın içine sıkıştırma).
    - Cevabı mutlaka bir soruyla bitir (Örn: "Nasıl, beğendin mi?").
    """

    full_messages = [{"role": "system", "content": system_message}] + messages_history

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=full_messages,
            temperature=0.75 # Yaratıcılığı çok az artırdım ki daha detaylı konuşsun
        )
        return response.choices[0].message.content
    except:
        return "Bağlantıda küçük bir sorun oldu, ama modumuz yerinde! Tekrar dener misin?"