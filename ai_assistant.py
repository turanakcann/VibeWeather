# ai_assistant.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('GPT_API_KEY'))

def extract_city_request(user_input):
    system_msg = """
    Kullanıcı mesajından sadece şehir/ilçe ismini çıkar.
    Eğer yoksa null dön.
    ÇIKTI: {"city": "ŞehirAdı"}
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

def get_chat_response(messages_history, weather_info, movie_data, drink_data):
    system_message = f"""
    Sen VibeWeather asistanısın. Konum: {weather_info['city']}, {weather_info['current_degree']}°C, {weather_info['condition']}
    
    Kullanıcı film/dizi ve içecek önerisi istiyor.
    - Samimi, enerjik, motive edici ol
    - Film önerirken (Film/Dizi • Tür) mutlaka yaz
    - İçecek önerirken (Sıcak/Soğuk) yaz
    - Kullanıcı kategori seçtiyse ona göre öner
    - Sonunda soru sor
    """

    full_messages = [{"role": "system", "content": system_message}] + messages_history

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=full_messages,
            temperature=0.8
        )
        return response.choices[0].message.content
    except:
        return "Bir hata oldu, tekrar dene."