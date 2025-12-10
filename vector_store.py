# vector_store.py – VibeWeather için son hali (temiz, optimize)
import streamlit as st
import os
import time
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "vibeweather-db"  # senin index adı buysa bırak
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# 40+ GENİŞLETİLMİŞ İÇECEK LİSTESİ
DRINK_DATASET = [
    {"id": "hot_001", "category": "Sıcak", "name": "Türk Kahvesi", "description": "Klasik Türk kahvesi, köpüklü ve telveli.", "context": "soğuk kış geleneksel kahve odaklanma"},
    {"id": "hot_002", "category": "Sıcak", "name": "Sıcak Çikolata", "description": "Koyu çikolata ve süt karışımı, üstü kremalı.", "context": "karlı kış tatlı kriz cozy"},
    {"id": "hot_003", "category": "Sıcak", "name": "Sahlep", "description": "Süt, sahlep tozu ve tarçın.", "context": "kış karlı tatlı geleneksel cozy"},
    {"id": "hot_004", "category": "Sıcak", "name": "Menengiç Kahvesi", "description": "Yabani fıstık macunu ve süt.", "context": "kafeinsiz akşam yumuşak geleneksel kış"},
    {"id": "hot_005", "category": "Sıcak", "name": "Adaçayı", "description": "Rahatlatıcı adaçayı, boğaz için ideal.", "context": "hasta kış bitki çay kafeinsiz"},
    {"id": "hot_006", "category": "Sıcak", "name": "Chai Latte", "description": "Baharatlı çay latte, tarçın ve zencefil.", "context": "sonbahar baharatlı rüzgarlı kış"},
    {"id": "hot_007", "category": "Sıcak", "name": "Pumpkin Spice Latte", "description": "Balkabağı, tarçın, espresso ve süt.", "context": "sonbahar yağmurlu baharatlı kış"},
    {"id": "hot_008", "category": "Sıcak", "name": "White Chocolate Mocha", "description": "Beyaz çikolata, espresso ve süt.", "context": "soğuk karlı tatlı kriz yağmurlu kış"},
    {"id": "hot_009", "category": "Sıcak", "name": "Cortado", "description": "Eşit espresso ve sıcak süt.", "context": "sabah ayılmak sert kahve odaklanma"},
    {"id": "hot_010", "category": "Sıcak", "name": "Filtre Kahve (V60)", "description": "Özel demleme ile berrak kahve.", "context": "nitelikli kahve gurme sabah"},
    {"id": "hot_011", "category": "Sıcak", "name": "Golden Milk", "description": "Zerdeçal, süt, bal ve baharat.", "context": "kış bağışıklık sağlıklı baharat"},
    {"id": "hot_012", "category": "Sıcak", "name": "Bitki Çayı Karışımı", "description": "Ihlamur, zencefil, limon.", "context": "hasta kış bağışıklık kafeinsiz"},
    {"id": "hot_013", "category": "Sıcak", "name": "Matcha Latte", "description": "Matcha tozu ve süt.", "context": "sağlıklı yeşil çay enerjik sabah"},
    {"id": "hot_014", "category": "Sıcak", "name": "Hot Toddy", "description": "Viski, bal, limon ve sıcak su.", "context": "gece kış alkollü rahatlatıcı"},
    {"id": "hot_015", "category": "Sıcak", "name": "Espresso", "description": "Yoğun espresso shot.", "context": "sabah enerjik sert kahve"},

    {"id": "cold_001", "category": "Soğuk", "name": "Limonata", "description": "Taze limon suyu ve şeker.", "context": "yaz sıcak ferah limonlu"},
    {"id": "cold_002", "category": "Soğuk", "name": "Ice Tea", "description": "Buzlu siyah çay, limonlu.", "context": "yaz güneşli serin çay"},
    {"id": "cold_003", "category": "Soğuk", "name": "Ayran", "description": "Soğuk ayran, tuzlu ve ferah.", "context": "yaz geleneksel serin tuzlu"},
    {"id": "cold_004", "category": "Soğuk", "name": "Cold Brew", "description": "Soğuk demleme kahve.", "context": "yaz enerjik kahve serin"},  # cold_cold_004 düzeltildi
    {"id": "cold_005", "category": "Soğuk", "name": "Frappe", "description": "Buzlu kahve frappe.", "context": "sıcak tatlı buzlu kahve"},
    {"id": "cold_006", "category": "Soğuk", "name": "Smoothie", "description": "Meyve ve yoğurt karışımı.", "context": "sıcak plaj meyveli sağlıklı"},
    {"id": "cold_007", "category": "Soğuk", "name": "Iced Latte", "description": "Buzlu sütlü kahve.", "context": "sıcak sütlü kahve"},
    {"id": "cold_008", "category": "Soğuk", "name": "Iced Americano", "description": "Buzlu sade espresso.", "context": "sıcak yaz güneşli sade ayılmak"},
    {"id": "cold_009", "category": "Soğuk", "name": "Cool Lime", "description": "Lime, nane ve şeker.", "context": "çok sıcak bunaltıcı yaz ferah"},
    {"id": "cold_010", "category": "Soğuk", "name": "Milkshake", "description": "Süt, dondurma ve meyve.", "context": "yaz tatlı dondurucu meyveli"},
    {"id": "cold_011", "category": "Soğuk", "name": "Dalgona Kahve", "description": "Çırpılmış kahve köpüğü ve soğuk süt.", "context": "trend tatlı sütlü soğuk"},
    {"id": "cold_012", "category": "Soğuk", "name": "Bumble Coffee (Portakallı)", "description": "Portakal suyu üzerine espresso.", "context": "yaz sabah enerji farklı modern"},
    {"id": "cold_013", "category": "Soğuk", "name": "Mojito (Alkolsüz)", "description": "Nane, lime, soda.", "context": "sıcak yaz ferah alkolsüz"},
    {"id": "cold_014", "category": "Soğuk", "name": "Cold Press Juice", "description": "Soğuk sıkım meyve suyu.", "context": "yaz sağlıklı detoks"},
    {"id": "cold_015", "category": "Soğuk", "name": "Kombucha", "description": "Fermente çay içeceği.", "context": "sağlıklı probiyotik ferah"}
]

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_pinecone_client():
    if not PINECONE_API_KEY:
        return None
    return Pinecone(api_key=PINECONE_API_KEY)

def initialize_vector_db():
    pc = get_pinecone_client()
    if not pc:
        return None

    model = load_embedding_model()

    # Index var mı kontrol et, yoksa oluştur
    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        pc.create_index(name=INDEX_NAME, dimension=384, metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"))
        time.sleep(15)

    index = pc.Index(INDEX_NAME)

    # VERİTABANI TEMİZLEME KODU KALDIRILDI – ARTIK GEREK YOK
    # İlk deploy'da çalıştı, şimdi sadece eksikse yükle

    # FİLMLER – TÜM ALANLARI KULLAN + TÜR GÖSTER
    stats = index.describe_index_stats()
    if 'movies' not in stats.namespaces or stats.namespaces.get('movies', {}).get('vector_count', 0) == 0:
        try:
            dataset = load_dataset("gamzeyy/film_data", split="train")
            vectors = []
            for i, item in enumerate(dataset):
                title   = item.get('title', 'İsimsiz Film')
                mtype   = item.get('type', 'Film')        # Film ya da Dizi
                summary = item.get('summary', '') or ''
                genre   = item.get('genre', 'Bilinmeyen Tür')

                # Vektör için zenginleştirilmiş metin
                search_text = f"{title} {mtype} {genre} {summary}"

                # Kullanıcıya gösterilecek metin
                display_text = f"**{title}** ({mtype} • {genre}) — {summary[:200]}{'...' if len(summary)>200 else ''}"

                vectors.append({
                    "id": f"movie_{i}",
                    "values": model.encode(search_text).tolist(),
                    "metadata": {"text": display_text, "type": "movie"}
                })

                if len(vectors) >= 100:
                    index.upsert(vectors, namespace="movies")
                    vectors = []
            if vectors:
                index.upsert(vectors, namespace="movies")
        except Exception as e:
            print("Film yükleme hatası:", e)

    # İÇECEKLER – SADECE EKSİKSE YÜKLE
    if 'drinks' not in stats.namespaces or stats.namespaces.get('drinks', {}).get('vector_count', 0) == 0:
        try:
            vectors = []
            for item in DRINK_DATASET:
                search_text = f"{item['context']} {item['description']} {item['name']} {item['category']}"
                display = f"**{item['name']}** ({item['category']}): {item['description']}"
                vectors.append({
                    "id": item["id"],
                    "values": model.encode(search_text).tolist(),
                    "metadata": {"text": display, "type": "drink"}
                })
            index.upsert(vectors, namespace="drinks")
        except Exception as e:
            print("İçecek yükleme hatası:", e)

    return "ready"

@st.cache_data(ttl=3600)
def search_by_weather(weather_desc, namespace, top_k=4):
    pc = get_pinecone_client()
    if not pc:
        return "Bağlantı hatası"
    index = pc.Index(INDEX_NAME)
    model = load_embedding_model()

    try:
        temp = float(weather_desc.split()[-2])
    except:
        temp = 20

    if namespace == "drinks":
        if temp <= 15:
            weather_desc = f"sıcak içecek kahve çay latte menengiç sahlep {weather_desc}"
        elif temp >= 25:
            weather_desc = f"soğuk içecek buzlu ferah frozen limonata ayran {weather_desc}"

    results = index.query(
        vector=model.encode(weather_desc).tolist(),
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    items = [f"• {m.metadata['text']}" for m in results.matches]
    return "\n".join(items) if items else "Öneri bulunamadı"