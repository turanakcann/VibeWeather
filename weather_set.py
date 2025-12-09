import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = "http://api.weatherapi.com/v1/current.json"

# API’nin saçma döndürdüğü isimler
BANNED_NAMES = ["Turkey", "Türkiye", "Truthahn", "Турция", "Null", "Asia/Istanbul"]


def get_weather_data(query_location):
    """
    Şehir adı ya da koordinat (lat,lon) alır → her zaman gerçek şehir ismi döner.
    """
    if not query_location or str(query_location).strip() in ["", "None", "null"]:
        return {"error": "Konum verisi bekleniyor..."}

    if not WEATHER_API_KEY:
        return {"error": "Weather API key eksik!"}

    clean_query = str(query_location).strip()

    # 1. Koordinat mı geldi? (örnek: "41.01,28.97")
    is_coordinate = "," in clean_query and all(part.replace(".", "").replace("-", "").isdigit() for part in clean_query.split(",") if part.strip())

    # 2. Şehir adıysa sonuna “, Turkey” ekle (daha iyi sonuç verir)
    if not is_coordinate:
        search_query = f"{clean_query}, Turkey"
    else:
        search_query = clean_query  # koordinat olduğu için direkt gönder

    params = {
        "key": WEATHER_API_KEY,
        "q": search_query,
        "lang": "tr"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=12)

        # İlk deneme başarısızsa (bazı koordinatlarda olur) sade haliyle tekrar dene
        if response.status_code != 200 and not is_coordinate:
            params["q"] = clean_query
            response = requests.get(BASE_URL, params=params, timeout=12)

        if response.status_code == 200:
            data = response.json()

            city_name = data["location"]["name"]
            region = data["location"]["region"]

            # API saçma isim döndürürse (Turkey, Null vs.) → kullanıcı ne girdiyse onu göster
            if city_name in BANNED_NAMES or not city_name:
                # Koordinat geldiyse bölgeyi (il) al, yoksa kullanıcı girdisini al
                city_name = region if region and region not in BANNED_NAMES else clean_query.split(",")[0]

            return {
                "city": city_name.strip(),
                "region": region,
                "country": data["location"]["country"],
                "current_degree": int(round(data["current"]["temp_c"])),
                "condition": data["current"]["condition"]["text"],
                "humidity": data["current"]["humidity"],
                "feelslike_c": data["current"]["feelslike_c"],
                "error": None
            }
        else:
            error_msg = response.json().get("error", {}).get("message", "Bilinmeyen hata")
            return {"error": f"'{clean_query}' bulunamadı → {error_msg}"}

    except Exception as e:
        return {"error": "İnternet bağlantısı hatası veya API sorunu."}