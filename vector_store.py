# vector_store.py – SON HALİ (kopyala-yapıştır yap)
import streamlit as st
import os
import time
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "vitaminco-db"
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

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

    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        try:
            pc.create_index(name=INDEX_NAME, dimension=384, metric="cosine",
                          spec=ServerlessSpec(cloud="aws", region="us-east-1"))
            time.sleep(15)
        except:
            pass

    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()

    # Sadece eksikse yükle
    if 'movies' not in stats.namespaces or stats.namespaces.get('movies', {}).get('vector_count', 0) == 0:
        try:
            dataset = load_dataset("gamzeyy/film_data", split="train")
            vectors = []
            for i, item in enumerate(dataset):
                text = f"{item.get('title','')} {item.get('overview','')} {item.get('genres','')} {item.get('keywords','')}"
                vectors.append({
                    "id": f"movie_{i}",
                    "values": model.encode(text).tolist(),
                    "metadata": {"text": f"**{item.get('title','Film')}** — {str(item.get('overview',''))[:180]}...", "type": "movie"}
                })
                if len(vectors) >= 100:
                    index.upsert(vectors, namespace="movies")
                    vectors = []
            if vectors:
                index.upsert(vectors, namespace="movies")
        except:
            pass

    return "ready"

@st.cache_data(ttl=3600)
def search_by_weather(weather_desc, namespace, top_k=4):
    pc = get_pinecone_client()
    if not pc: return "Bağlantı hatası"
    index = pc.Index(INDEX_NAME)
    model = load_embedding_model()

    try:
        temp = float(weather_desc.split()[-2])
    except:
        temp = 20

    if namespace == "drinks":
        if temp <= 15:
            weather_desc = f"sıcak içecek kahve çay latte menengiç {weather_desc}"
        elif temp >= 25:
            weather_desc = f"soğuk içecek buzlu ferah frozen {weather_desc}"

    results = index.query(vector=model.encode(weather_desc).tolist(), top_k=top_k,
                         include_metadata=True, namespace=namespace)
    return "\n".join([f"• {m.metadata['text']}" for m in results.matches]) if results.matches else "Öneri bulunamadı"