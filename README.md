# 🌤️ VibeWeather - Mood & Weather Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vibeweather.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4o-green)
![Pinecone](https://img.shields.io/badge/Vector%20DB-Pinecone-orange)

**VibeWeather**, bulunduğunuz konumun hava durumuna ve atmosferine göre size en uygun **film** ve **içecek** önerilerini sunan, RAG (Retrieval-Augmented Generation) tabanlı akıllı bir yaşam tarzı asistanıdır.

---

## 🎯 Ne İşe Yarar?

"Bugün hava çok kasvetli, ne izlesem?" veya "Bu sıcakta ne içilir?" derdine son!

VibeWeather:
1.  **Konumunuzu Algılar:** GPS üzerinden veya manuel girdiğiniz İl/İlçe bilgisini (Örn: *Torbalı, İzmir*) alır.
2.  **Hava Durumunu Analiz Eder:** WeatherAPI ile anlık sıcaklık ve hava koşullarını çeker.
3.  **Vektörel Arama Yapar (RAG):** Havanın "moduna" (Örn: Soğuk, Yağmurlu, Melankolik) en uygun filmleri ve içecekleri Pinecone vektör veritabanından anlamsal olarak arar.
4.  **Kişiselleştirilmiş Öneri Sunar:** GPT-4o-mini, bulduğu verileri yorumlayarak size samimi bir dille nokta atışı öneriler yapar.

---

## 🚀 Temel Özellikler

* **📍 Hassas Konum Tespiti:** Sadece illeri değil, ilçeleri de tanır (Örn: *Kadıköy, İstanbul*).
* **🕵️‍♂️ Akıllı Dedektif (Agent):** Sohbet sırasında *"Peki Antalya'da durum ne?"* dediğinizde, yapay zeka bunu algılar ve arka planda konumu ve önerileri otomatik günceller.
* **☁️ Bulut Tabanlı RAG:** Film ve içecek veritabanı Pinecone üzerinde tutulur (Serverless), bu sayede hızlı ve akıllı eşleşme sağlanır.
* **🧠 Semantik Arama:** Sadece kelime eşleşmesi değil, anlam eşleşmesi yapar. *"İçimi ısıtacak bir şey"* dediğinizde kahve veya çay önerir.
* **🎨 Modern Arayüz:** Streamlit ile geliştirilmiş, kullanıcı dostu ve şık tasarım.

---

## 🛠️ Kullanılan Teknolojiler

* **Frontend:** [Streamlit](https://streamlit.io/)
* **LLM (Yapay Zeka):** OpenAI GPT-4o-mini
* **Vector Database:** [Pinecone](https://www.pinecone.io/)
* **Embedding Model:** `paraphrase-multilingual-MiniLM-L12-v2` (Sentence Transformers)
* **Weather Data:** [WeatherAPI](https://www.weatherapi.com/)
* **Data Source:** Hugging Face Datasets & Custom Gourmet Drink Dataset

---

## ⚙️ Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için adımları takip edin:

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/turanakcann/VibeWeather.git](https://github.com/turanakcann/VibeWeather.git)
    cd VibeWeather
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment (.env) Dosyasını Oluşturun:**
    Proje ana dizinine `.env` adında bir dosya açın ve aşağıdaki API anahtarlarınızı ekleyin:
    ```env
    OPENAI_API_KEY="sk-..."
    WEATHER_API_KEY="..."
    PINECONE_API_KEY="..."
    ```

4.  **Uygulamayı Başlatın:**
    ```bash
    streamlit run app.py
    ```

---

## 📸 Ekran Görüntüleri

*(Buraya uygulamanın ekran görüntülerini ekleyebilirsiniz)*

---

## 🤝 Katkıda Bulunma

1.  Fork'layın.
2.  Yeni bir branch oluşturun (`git checkout -b ozellik/YeniOzellik`).
3.  Değişikliklerinizi commit'leyin (`git commit -m 'Yeni özellik eklendi'`).
4.  Branch'inizi push'layın (`git push origin ozellik/YeniOzellik`).
5.  Pull Request oluşturun.

---

## 📞 İletişim

**Geliştirici:** Turan Akcan  
**E-posta:** [turannakcan@gmail.com](mailto:turannakcan@gmail.com)  
GitHub: [@turanakcann](https://github.com/turanakcann)
