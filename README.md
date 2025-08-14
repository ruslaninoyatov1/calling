# AutoCaller API

Avtomatik qo'ng'iroq tizimi uchun FastAPI asosida yaratilgan API.

## Xususiyatlar

- ✅ MySQL ma'lumotlar bazasi bilan integratsiya
- ✅ TTS (Text-to-Speech) orqali audio fayl yaratish yoki audio linkdan import
- ✅ Asterisk PBX bilan integratsiya
- ✅ Kompaniyalar, matnlar va qo'ng'iroqlarni boshqarish
- ✅ Har bir kompaniya uchun alohida SIP trunk (avtomatik yaratiladi)
- ✅ SIP orqali avtomatik qo'ng'iroqlar
- ✅ Audio fayllarni turli formatlarga o'tkazish (WAV, ALAW, GSM)
- ✅ Ish vaqti oynasi bo'yicha qo'ng'iroqlarni cheklash (masalan 07:15–21:59)
- ✅ 5 daqiqada bir marta cron orqali avtomatik tekshirish

## O'rnatish

### 1. Tizim talablari

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg mysql-client asterisk

# CentOS/RHEL
sudo yum install python3 python3-pip ffmpeg mysql asterisk
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

MySQL ma'lumotlar bazasida quyidagi ustunlarni tekshiring va yo'q bo'lsa qo'shing:

```sql
-- audio_filename ustunini qo'shish (agar yo'q bo'lsa)
ALTER TABLE `texts` ADD COLUMN `audio_filename` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL AFTER `link`;

-- kompaniya uchun trunk nomi (har bir kompaniya uchun avtomatik acc_{id})
ALTER TABLE `companies` ADD COLUMN `trunk_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL AFTER `token`;
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
# Agar SQLite ishlatmoqchi bo'lsangiz
# USE_SQLITE=true

# TTS API Configuration
MUXLISA_API_KEY=your_muxlisa_api_key_here
MUXLISA_TTS_URL=https://service.muxlisa.uz/api/v2/tts

# Asterisk Configuration
CALL_DIR=/var/spool/asterisk/outgoing
ASTERISK_SOUNDS_DIR=/var/lib/asterisk/sounds
# SIP trunk snippetlari uchun papka (sip.conf ichidan include qilinadi)
SIP_AUTOCALLER_DIR=/etc/asterisk/sip_autocaller.d

# Qo'ng'iroq vaqti oynasi (Asia/Tashkent) — ish vaqtidan tashqarida qo'ng'iroq qilinmaydi
CALL_START=07:15
CALL_END=21:59
```

### 5. Asterisk konfiguratsiyasi

- `sip.conf` ichiga quyidagi qatorni qo'shing (oxiriga):

```ini
#include sip_autocaller.d/*.conf
```

- `extensions.conf` da `outgoing` kontekstida `AUDIOFILE` o'zgaruvchidan foydalaning:

```ini
[outgoing]
exten => s,1,NoOp(Outgoing call started for ${CALLERID(num)})
same  => n,Answer()
same  => n,Wait(1)
; Audio fayl: /var/lib/asterisk/sounds/project-audio/<name>.wav
same  => n,Playback(project-audio/${AUDIOFILE})
same  => n,Hangup()
```

- Huquqlar:

```bash
sudo mkdir -p /etc/asterisk/sip_autocaller.d
sudo chown -R asterisk:asterisk /var/spool/asterisk/outgoing
sudo chown -R asterisk:asterisk /var/lib/asterisk/sounds
sudo chown -R asterisk:asterisk /etc/asterisk/sip_autocaller.d
```

Agar kompaniya yaratilsa, dastur avtomatik tarzda `/etc/asterisk/sip_autocaller.d/acc_<id>.conf` faylini yaratadi va `asterisk -rx "sip reload"` bajaradi.

### 6. Loyihani ishga tushirish

```bash
# API serverni ishga tushirish
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpointlar

### Kompaniyalar

- `POST /companies/` - Yangi kompaniya yaratish (SIP trunk avtomatik yaratiladi)
- `GET /companies/` - Barcha kompaniyalarni olish

Kompaniya yaratish JSON:

```json
{
  "name": "Kompaniya nomi",
  "link": "SIP olingan link (masalan: pbx.skyline.uz)",
  "login": "SIP olingan logini (masalan: 781137767)",
  "password": "SIP ning paroli (masalan: VUi0vaqS15M8yXkNK)"
}
```

### Matnlar

- `POST /texts/` - Yangi matn yaratish (TTS yoki audio link orqali)
- `GET /texts/` - Barcha matnlarni olish

Matn yaratish JSON:

```json
{
  "company_id": 1,
  "text": "Assalomu alaykum, yaxshimisiz?",
  "link": null
}
```

Agar `link` berilsa (masalan, MP3/WAV URL), tizim linkdan audioni yuklab oladi va kerakli formatlarga konvertatsiya qiladi.

### Qo'ng'iroqlar

- `POST /phone-calls/` - Yangi qo'ng'iroq yaratish
- `GET /phone-calls/` - Barcha qo'ng'iroqlarni olish

Qo'ng'iroq yaratish JSON:

```json
{
  "text_id": 1,
  "phone": "998914045340",
  "date": "2025-08-14",
  "status": 0,
  "call_time": 0,
  "last_date": "2025-08-14",
  "company_id": 1
}
```

### Foydalanuvchilar

- `POST /users/` - Yangi foydalanuvchi yaratish
- `GET /users/` - Barcha foydalanuvchilarni olish

## Cron (VDS) bilan ishlatish

Tizim ichki scheduler orqali ham har 5 daqiqada tekshiradi. Agar cron ishlatmoqchi bo'lsangiz, quyidagicha sozlang:

```bash
# scripts/cron_check.py bir martalik tekshiruvni bajaradi
# Crontabga qo'shing (Linux):
*/5 * * * * /usr/bin/bash -lc 'cd /path/to/auto-caller && ./venv/bin/python -m scripts.cron_check >> logs/cron.log 2>&1'
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
│   ├── tts.py           # Text-to-Speech va audio import
│   ├── scheduler.py     # 5 daqiqalik tekshiruvchi
│   └── asterisk_trunk.py# Kompaniya uchun SIP trunk yaratish
├── scripts/
│   └── cron_check.py    # Cron uchun bir martalik tekshiruv
├── agi/
│   └── play_audio.agi   # Asterisk AGI script (ixtiyoriy)
├── audio/               # Audio fayllar
├── logs/                # Log fayllar
├── temp_calls/          # Vaqtinchalik qo'ng'iroq fayllari
├── requirements.txt     # Python dependencies
└── README.md            # Ushbu fayl
```

## API Dokumentatsiya

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
