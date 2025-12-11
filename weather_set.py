# weather_set.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = "http://api.weatherapi.com/v1/current.json"
BANNED_NAMES = ["Turkey", "Türkiye", "Null", "Asia/Istanbul"]

def get_weather_data(query_location):
    if not query_location or str(query_location).strip() in ["", "None", "null"]:
        return {"error": "Konum verisi bekleniyor..."}

    if not WEATHER_API_KEY:
        return {"error": "API key eksik!"}

    clean_query = str(query_location).strip()

    # KOORDİNAT MI?
    is_coordinate = "," in clean_query and "Turkey" not in clean_query
    
    # HER ZAMAN TÜRKİYE EKLE (İlçeleri bulması için)
    if not is_coordinate:
        search_query = f"{clean_query}, Türkiye"
    else:
        search_query = clean_query

    params = {"key": WEATHER_API_KEY, "q": search_query, "lang": "tr"}
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=12)
        
        if response.status_code == 200:
            data = response.json()
            city_name = data["location"]["name"]
            region = data["location"]["region"]
            country_name = data["location"]["country"] # YENİ EKLENDİ

            # SAÇMA İSİM GELİRSE DÜZELT
            if city_name in BANNED_NAMES or "North" in city_name or "South" in city_name:
                city_name = region or clean_query.split(",")[0]

            return {
                "city": city_name.strip(),
                "country": country_name, # ARTIK BU VERİ VAR
                "current_degree": int(round(data["current"]["temp_c"])),
                "condition": data["current"]["condition"]["text"],
                "humidity": data["current"]["humidity"],
                "feelslike_c": data["current"]["feelslike_c"],
                "error": None
            }
        else:
            return {"error": "Şehir bulunamadı. Örnek: Çankırı, Van"}
    except:
        return {"error": "Bağlantı hatası"}