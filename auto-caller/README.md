# AutoCaller API

Avtomatik qo'ng'iroq tizimi uchun FastAPI asosida yaratilgan API.

## Xususiyatlar

- ✅ MySQL ma'lumotlar bazasi bilan integratsiya
- ✅ TTS (Text-to-Speech) orqali audio fayl yaratish
- ✅ Asterisk PBX bilan integratsiya
- ✅ Kompaniyalar, matnlar va qo'ng'iroqlarni boshqarish
- ✅ SIP orqali avtomatik qo'ng'iroqlar
- ✅ Audio fayllarni turli formatlarga o'tkazish (WAV, ALAW, GSM)

## O'rnatish

### 1. Tizim talablari

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg mysql-client

# CentOS/RHEL
sudo yum install python3 python3-pip ffmpeg mysql
```

### 2. Loyihani klonlash va o'rnatish

```bash
git clone <repository-url>
cd auto-caller

# Virtual environment yaratish
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Dependencies o'rnatish
pip install -r requirements.txt
```

### 3. Ma'lumotlar bazasi sozlash

MySQL ma'lumotlar bazasida quyidagi jadvalni yarating:

```sql
-- audio_filename ustunini qo'shish (agar yo'q bo'lsa)
ALTER TABLE `texts` ADD COLUMN `audio_filename` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL AFTER `link`;
```

### 4. Environment faylini sozlash

`.env` faylini yarating:

```env
# Database Configuration
DB_HOST=46.202.143.229
DB_PORT=3306
DB_NAME=auto_caller
DB_USER=root
DB_PASSWORD=your_password_here

# TTS API Configuration
TTS_API_KEY=DeTeJl_xqq31RQqUfqMD8XkOhXneBRxvB2howHgC
MUXLISA_TTS_URL=https://service.muxlisa.uz/api/v2/tts

# Asterisk Configuration
CALL_DIR=/var/spool/asterisk/outgoing
ASTERISK_SOUNDS_DIR=/var/lib/asterisk/sounds

# SIP Configuration
SIP_HOST=pbx.skyline.uz
SIP_USERNAME=781137767
SIP_SECRET=VUi0vaqS15M8yXkNK
SIP_CONTEXT=outgoing
```

### 5. Loyihani ishga tushirish

```bash
# Setup scriptini ishga tushirish
python setup.py

# API serverni ishga tushirish
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpointlar

### Kompaniyalar

- `POST /companies/` - Yangi kompaniya yaratish
- `GET /companies/` - Barcha kompaniyalarni olish

### Matnlar

- `POST /texts/` - Yangi matn yaratish
- `GET /texts/` - Barcha matnlarni olish

### Qo'ng'iroqlar

- `POST /phone-calls/` - Yangi qo'ng'iroq yaratish
- `GET /phone-calls/` - Barcha qo'ng'iroqlarni olish

### Foydalanuvchilar

- `POST /users/` - Yangi foydalanuvchi yaratish
- `GET /users/` - Barcha foydalanuvchilarni olish

### Health Check

- `GET /health` - Tizim holatini tekshirish

## API Foydalanish misollari

### Kompaniya yaratish

```bash
curl -X POST "http://localhost:8000/companies/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "link": "https://example.com",
    "login": "testuser",
    "password": "testpass"
  }'
```

### Matn yaratish

```bash
curl -X POST "http://localhost:8000/texts/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "text": "Salom, bu test xabar",
    "link": "https://example.com"
  }'
```

### Qo'ng'iroq yaratish

```bash
curl -X POST "http://localhost:8000/phone-calls/" \
  -H "Content-Type: application/json" \
  -d '{
    "text_id": 1,
    "phone": "998901234567",
    "date": "2025-08-05"
  }'
```

## Fayl tuzilishi

```
auto-caller/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI asosiy fayl
│   ├── config.py        # Konfiguratsiya
│   ├── database.py      # Ma'lumotlar bazasi ulanishi
│   ├── models.py        # SQLAlchemy modellar
│   ├── schemas.py       # Pydantic sxemalar
│   ├── call.py          # Qo'ng'iroq funksiyalari
│   └── tts.py           # Text-to-Speech
├── agi/
│   └── play_audio.agi   # Asterisk AGI script
├── asterisk-config/
│   ├── extensions.conf  # Asterisk extensions
│   └── sip.conf         # SIP konfiguratsiya
├── audio/               # Audio fayllar
├── logs/                # Log fayllar
├── temp_calls/          # Vaqtinchalik qo'ng'iroq fayllari
├── requirements.txt     # Python dependencies
├── setup.py            # O'rnatish scripti
└── README.md           # Bu fayl
```

## Xatoliklarni tuzatish

### Ma'lumotlar bazasi ulanishi

```bash
# MySQL ulanishini tekshirish
mysql -h 46.202.143.229 -u root -p auto_caller
```

### FFmpeg o'rnatish

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### Asterisk huquqlari

```bash
# Asterisk foydalanuvchisi uchun huquqlar
sudo chown -R asterisk:asterisk /var/spool/asterisk/outgoing
sudo chown -R asterisk:asterisk /var/lib/asterisk/sounds
```

## API Dokumentatsiya

API dokumentatsiyasini ko'rish uchun:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Log fayllar

Log fayllar `logs/` papkasida saqlanadi:
- `call.log` - Qo'ng'iroq loglari
- API loglari uvicorn orqali chiqadi

## Xavfsizlik

- API kalitlarini `.env` faylida saqlang
- Ma'lumotlar bazasi parolini kuchli qiling
- Firewall sozlamalarini tekshiring
- HTTPS ishlatish tavsiya etiladi

## Yordam

Muammolar bo'lsa:
1. Log fayllarni tekshiring
2. Ma'lumotlar bazasi ulanishini tekshiring
3. FFmpeg o'rnatilganligini tekshiring
4. Asterisk huquqlarini tekshiring
