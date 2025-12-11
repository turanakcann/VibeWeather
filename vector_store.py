import streamlit as st
import os
import time
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "vibeweather-db"
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# --- EKSTRA MANUEL FİLM/DİZİ LİSTESİ (ÖZEL SEÇKİ) ---
MANUAL_MOVIES = [
    # TÜRK YAPIMLARI
    {"title": "Gibi", "type": "Dizi", "genre": "Komedi", "summary": "Yılmaz ve İlkkan'ın sıradan hayatlarında başlarına gelen tuhaf, absürt ve komik olaylar silsilesi.", "context": "komedi türk dizisi absürt eğlenceli gülmek"},
    {"title": "Şahsiyet", "type": "Dizi", "genre": "Suç/Dram", "summary": "Emekli adliye memuru Agâh Beyoğlu'nun, Alzheimer teşhisi konduktan sonra yıllardır planladığı cinayetleri işlemeye başlaması.", "context": "suç polisiye gerilim türk dizisi ödüllü"},
    {"title": "Bir Başkadır", "type": "Dizi", "genre": "Dram", "summary": "Farklı sosyo-ekonomik geçmişlerden gelen insanların yollarının İstanbul'da kesişmesi ve birbirlerinin hayatlarına dokunması.", "context": "dram istanbul toplumsal gerçekçi türk"},
    {"title": "Kış Uykusu", "type": "Film", "genre": "Dram", "summary": "Nuri Bilge Ceylan'ın başyapıtı. Emekli bir tiyatrocunun Kapadokya'daki otelinde kışın bastırmasıyla yaşadığı içsel krizler.", "context": "sanat filmi kış karlı kapadokya ağır melankolik"},
    {"title": "Ölümlü Dünya", "type": "Film", "genre": "Komedi/Aksiyon", "summary": "Nesillerdir kiralık katillik yapan Mermer ailesinin, örgütle ters düşüp hayatta kalma mücadelesi verirken yaşadığı komik olaylar.", "context": "komedi aksiyon türk aile eğlenceli"},

    # YABANCI DİZİLER (GÜNCEL & KÜLT)
    {"title": "Succession", "type": "Dizi", "genre": "Dram/Hiciv", "summary": "Küresel bir medya imparatorluğunu yöneten Roy ailesinin içindeki güç savaşları, ihanetler ve trajikomik olaylar.", "context": "iş dünyası güç savaşı zenginlik dram entrika"},
    {"title": "Severance", "type": "Dizi", "genre": "Bilim Kurgu/Gerilim", "summary": "Bir şirketin çalışanlarının iş ve özel hayat anılarını cerrahi bir işlemle ayırması sonucu ortaya çıkan gizemli olaylar.", "context": "gizem ofis distopya beyin yakan gerilim"},
    {"title": "The Bear", "type": "Dizi", "genre": "Dram/Komedi", "summary": "Genç ve yetenekli bir şefin, ailesinin salaş sandviç dükkanını devralıp onu bir restorana dönüştürme çabası ve mutfak kaosu.", "context": "mutfak stres kaos tutku yemek"},
    {"title": "Ted Lasso", "type": "Dizi", "genre": "Komedi/Spor", "summary": "Amerikan futbolu koçu Ted Lasso'nun, hiç bilmediği İngiliz futbol takımını yönetmek için İngiltere'ye gitmesi ve iyimserliğiyle herkesi değiştirmesi.", "context": "iyi hissettiren feel good pozitif komedi spor"},
    {"title": "Dark", "type": "Dizi", "genre": "Bilim Kurgu/Gizem", "summary": "Almanya'da bir kasabada kaybolan çocukların ardından ortaya çıkan zaman yolculuğu ve paradokslarla dolu karmaşık bir hikaye.", "context": "zaman yolculuğu kafa karıştırıcı gizem karanlık yağmurlu"},
    {"title": "Fleabag", "type": "Dizi", "genre": "Komedi/Dram", "summary": "Londra'da yaşayan, zeki, kederli ve öfkeli bir kadının modern hayatla başa çıkma çabası. Dördüncü duvarı yıkan bir anlatım.", "context": "komedi dram ingiliz modern yalnızlık"},

    # ANIME & ANİMASYON
    {"title": "Spirited Away (Ruhların Kaçışı)", "type": "Film", "genre": "Anime/Fantastik", "summary": "Küçük Chihiro'nun ruhlar dünyasında kaybolması ve ailesini kurtarmak için verdiği büyülü mücadele. Studio Ghibli klasiği.", "context": "anime fantastik büyüleyici renkli huzurlu"},
    {"title": "Cowboy Bebop", "type": "Dizi", "genre": "Anime/Bilim Kurgu", "summary": "Gelecekte geçen, uzay kovboylarının maceralarını caz müzikleri eşliğinde anlatan stilize bir anime.", "context": "anime uzay aksiyon caz müzik cool"},
    {"title": "Arcane", "type": "Dizi", "genre": "Animasyon/Aksiyon", "summary": "Piltover ve Zaun şehirleri arasındaki çatışmanın ortasında kalan iki kız kardeşin hikayesi. Görsel bir şölen.", "context": "animasyon aksiyon fantastik görsel şölen"},

    # FİLMLER (MODA GÖRE)
    {"title": "Blade Runner 2049", "type": "Film", "genre": "Bilim Kurgu", "summary": "Distopik bir gelecekte, sırları açığa çıkaran bir replicant avcısının hikayesi. Muazzam görsellik ve atmosfer.", "context": "görsel şölen bilim kurgu distopya neon karanlık"},
    {"title": "Grand Budapest Hotel", "type": "Film", "genre": "Komedi/Macera", "summary": "Wes Anderson'ın simetrik ve renkli dünyasında geçen, bir otel görevlisi ve lobicinin maceraları.", "context": "renkli eğlenceli estetik masalsı"},
    {"title": "Pride & Prejudice (2005)", "type": "Film", "genre": "Romantik/Dram", "summary": "Jane Austen'ın klasik romanından uyarlama. Elizabeth Bennet ve Bay Darcy'nin gurur ve önyargı dolu aşk hikayesi.", "context": "romantik dönem filmi aşk yağmurlu duygusal"},
    {"title": "The Batman (2022)", "type": "Film", "genre": "Aksiyon/Suç", "summary": "Gotham'ın karanlık sokaklarında seri katil Riddler'ın peşine düşen dedektif Batman'in noir tarzı hikayesi.", "context": "karanlık yağmurlu suç aksiyon dedektif"},
    {"title": "Knives Out", "type": "Film", "genre": "Gizem/Komedi", "summary": "Ünlü bir yazarın ölümünün ardından, eksantrik bir dedektifin tuhaf aile üyelerini sorgulayarak cinayeti çözmesi.", "context": "gizem dedektif katil kim eğlenceli"},
    {"title": "About Time", "type": "Film", "genre": "Romantik/Fantastik", "summary": "Zamanda yolculuk yapabildiğini keşfeden bir gencin, bu yeteneğini aşk hayatını düzeltmek için kullanması.", "context": "romantik duygusal iyi hissettiren aşk"},
    {"title": "Interstellar", "type": "Film", "genre": "Bilim Kurgu", "summary": "İnsanlığın sonu gelirken, yaşanabilir yeni gezegenler bulmak için solucan deliğinden geçen bir grup astronotun hikayesi.", "context": "uzay bilim kurgu epik duygusal hans zimmer"},
    {"title": "Whiplash", "type": "Film", "genre": "Dram/Müzik", "summary": "Genç bir baterist ve onun sınırlarını zorlayan acımasız hocası arasındaki psikolojik savaş.", "context": "gerilim müzik tutku hırs"},
    {"title": "Paddington 2", "type": "Film", "genre": "Aile/Komedi", "summary": "Londra'ya yerleşen sevimli ayı Paddington'ın, teyzesine hediye almak için çalışması ve bir hırsızlık olayına karışması.", "context": "aile sıcak sevimli mutlu eden"},
    {"title": "Chungking Express", "type": "Film", "genre": "Romantik/Dram", "summary": "Wong Kar-wai'nin yönettiği, Hong Kong'da geçen, melankolik ve stilize iki aşk hikayesi.", "context": "sanat filmi melankolik aşk estetik gece"},
    {"title": "Parasite", "type": "Film", "genre": "Gerilim/Kara Komedi", "summary": "Yoksul Kim ailesinin, zengin Park ailesinin evine yavaş yavaş sızmasıyla gelişen olaylar.", "context": "gerilim oscarlı kore sosyal eleştiri"},
    {"title": "Before Sunrise", "type": "Film", "genre": "Romantik", "summary": "Viyana'da trende tanışan iki gencin, sabaha kadar şehri gezip hayat ve aşk üzerine sohbet etmeleri.", "context": "romantik sohbet gezi aşk samimi"},
    {"title": "The Menu", "type": "Film", "genre": "Gerilim/Korku", "summary": "Ünlü bir şefin özel adasındaki restoranına giden bir çiftin, menüdeki şok edici sürprizlerle karşılaşması.", "context": "gerilim yemek gizem karanlık"},
    {"title": "Everything Everywhere All At Once", "type": "Film", "genre": "Bilim Kurgu/Aksiyon", "summary": "Sıradan bir kadının, dünyayı kurtarmak için çoklu evrenlerdeki diğer versiyonlarıyla bağlantı kurması.", "context": "kaos aksiyon eğlenceli duygusal aile"}
]

# İÇECEK LİSTESİ (AYNEN KORUNDU)
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
    {"id": "cold_004", "category": "Soğuk", "name": "Cold Brew", "description": "Soğuk demleme kahve.", "context": "yaz enerjik kahve serin"},
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

    # 1. FİLMLERİ YÜKLE (Hugging Face + Manuel Liste)
    # Sadece veritabanı boşsa veya eksikse yükler.
    # Ancak manuel listeyi eklemek için ufak bir kontrol ekleyelim.
    stats = index.describe_index_stats()
    
    # Eğer namespace hiç yoksa veya çok az veri varsa yükle
    if 'movies' not in stats.namespaces or stats.namespaces.get('movies', {}).get('vector_count', 0) < 50:
        try:
            # A. Önce Hugging Face Verisi
            dataset = load_dataset("gamzeyy/film_data", split="train")
            vectors = []
            
            # Hugging Face verilerini ekle
            for i, item in enumerate(dataset):
                title   = item.get('title', 'İsimsiz Film')
                mtype   = item.get('type', 'Film')
                summary = item.get('summary', '') or ''
                genre   = item.get('genre', 'Bilinmeyen Tür')
                search_text = f"{title} {mtype} {genre} {summary}"
                display_text = f"**{title}** ({mtype} • {genre}) — {summary[:200]}{'...' if len(summary)>200 else ''}"

                vectors.append({
                    "id": f"movie_hf_{i}",
                    "values": model.encode(search_text).tolist(),
                    "metadata": {"text": display_text, "type": "movie"}
                })
                if len(vectors) >= 100:
                    index.upsert(vectors, namespace="movies")
                    vectors = []
            
            # B. Şimdi Bizim Manuel Listeyi Ekle (Vibe İçin Kritik!)
            for i, item in enumerate(MANUAL_MOVIES):
                search_text = f"{item['title']} {item['type']} {item['genre']} {item['summary']} {item['context']}"
                display_text = f"**{item['title']}** ({item['type']} • {item['genre']}) — {item['summary']}"
                
                vectors.append({
                    "id": f"movie_manual_{i}", # Özel ID
                    "values": model.encode(search_text).tolist(),
                    "metadata": {"text": display_text, "type": "movie"}
                })
            
            # Kalanları gönder
            if vectors:
                index.upsert(vectors, namespace="movies")
                
        except Exception as e:
            print("Film yükleme hatası:", e)

    # 2. İÇECEKLERİ YÜKLE
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