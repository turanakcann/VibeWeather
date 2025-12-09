import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GPT_API_KEY') or os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def extract_city_request(user_input):
    """
    Mesajdan sadece YER ismini çeker.
    """
    system_msg = """
    GÖREV: Kullanıcı mesajındaki LOKASYON (İlçe veya Şehir) ismini bul ve JSON ver.
    
    KURALLAR:
    1. Mesajda bir yer ismi varsa (Örn: "Torbalı", "Çankaya", "İzmir", "Bodrum"), o ismi YALIN halde ver.
    2. "İlçe İl" formatındaysa (Örn: "İzmir Buca"), SADECE İLÇEYİ ("Buca") ver.
    3. Yer ismi yoksa null ver.
    
    ÇIKTI: {"city": "YerIsmi"}
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
    Sen 'Mood & Weather Asistanı'sın.
    
    DURUM:
    Konum: {weather_info['city']}
    Hava: {weather_info['current_degree']}°C, {weather_info['condition']}
    
    ÖNERİLEN FİLMLER (Database):
    {movie_data}
    
    ÖNERİLEN İÇECEKLER (Database):
    {drink_data}
    
    GÖREV:
    1. Havanın durumuna göre en uygun filmi ve içeceği seçip öner.
    2. Neden bunları seçtiğini detaylı ve uzun bir şekilde anlat (en az 3-4 cümle, örneklerle).
    3. Samimi, enerjik ve motive edici ol. Sohbeti uzat, alternatif öneriler ver.
    """

    full_messages = [{"role": "system", "content": system_message}] + messages_history

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=full_messages,
            temperature=0.8  # Yaratıcılık için artırıldı
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Bağlantı hatası."