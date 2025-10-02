# AIDAS-HT Chatbot (MVP)

Eğitim amaçlı hasar tespit chatbot'u. FastAPI + basit RAG (TF–IDF) kullanır. KB olarak `kb/` klasöründeki PDF'leri tarar.

## Hızlı Kurulum (Lokal)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Tarayıcıda: http://127.0.0.1:8000/ (API) ve frontend/index.html dosyasını açıp kullanın.
```

## Render'a Dağıtım
1. Bu dizini bir GitHub deposuna gönderin.
2. [render.com](https://render.com) → New → Web Service.
3. Depoyu seçin, *Build Command*: `pip install -r requirements.txt`.
4. *Start Command*: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Deploy.

`render.yaml` eklenmiştir; isterseniz *Blueprint* olarak da kurabilirsiniz.

## KB Güncelleme
- Yeni PDF'leri `kb/` klasörüne ekleyin ve yeniden deploy edin.
- Uygulama açılışta PDF'leri parçalara ayırır ve TF–IDF indeksi oluşturur.

## Uç Noktalar
- `GET /health` — durum ve KB sayısı
- `POST /ask` — { question } alır, KB parçalarından özet döndürür
- `GET /quiz/start` — örnek sorular
- `POST /quiz/submit` — cevapları değerlendirir

## Uyarı
Bu yazılım **eğitim amaçlıdır** ve **resmi** hasar tespiti yerine geçmez. Yetkili kurum mevzuatı (AFAD/ÇŞİDB) ve uzman onayı esastır.
