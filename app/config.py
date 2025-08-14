import os
from typing import Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """AutoCaller konfiguratsiya klassi"""
    
    # Static raqam
    STATIC_NUMBER = "998771137767"
    
    # Asterisk konfiguratsiya
    CALL_DIR = "/var/spool/asterisk/outgoing"
    ASTERISK_SOUNDS_DIR = "/var/lib/asterisk/sounds"
    
    # Asterisk SIP config snippets directory (must be included from sip.conf)
    # Example: add this line to /etc/asterisk/sip.conf -> #include sip_autocaller.d/*.conf
    SIP_AUTOCALLER_DIR = os.getenv("SIP_AUTOCALLER_DIR", "/etc/asterisk/sip_autocaller.d")
    
    # Audio va temp kataloglar
    AUDIO_DIR = "audio"
    TEMP_CALL_DIR = "temp_calls"
    LOG_DIR = "logs"
    
    # TTS API
    MUXLISA_TTS_URL = os.getenv("MUXLISA_TTS_URL", "https://service.muxlisa.uz/api/v2/tts")
    MUXLISA_API_KEY = os.getenv("MUXLISA_API_KEY")
    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "46.202.143.229")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "auto_caller")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # Use SQLite as fallback for immediate functionality
    USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"
    
    # MySQL Database URL - handle empty password
    @classmethod
    def get_database_url(cls) -> str:
        if cls.USE_SQLITE:
            return "sqlite:///./auto_caller.db"
        
        if cls.DB_PASSWORD:
            return f"mysql+pymysql://{cls.DB_USER}:{quote_plus(cls.DB_PASSWORD)}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            return f"mysql+pymysql://{cls.DB_USER}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    # SIP konfiguratsiya (default trunk values kept for backward compatibility)
    SIP_HOST = "pbx.skyline.uz"
    SIP_USERNAME = "781137767"
    SIP_SECRET = "VUi0vaqS15M8yXkNK"
    SIP_CONTEXT = "outgoing"
    
    # Bulk qo'ng'iroqlar chegarasi
    MAX_BULK_CALLS = 100000000
    
    # Call time window (Asia/Tashkent)
    CALL_START = os.getenv("CALL_START", "07:15")  # HH:MM
    CALL_END = os.getenv("CALL_END", "21:59")      # HH:MM
    
    @classmethod
    def get_static_number(cls) -> str:
        """Static raqamni qaytaradi"""
        return cls.STATIC_NUMBER
    
    @classmethod
    def is_static_number(cls, phone_number: str) -> bool:
        """Raqam static raqam ekanligini tekshiradi"""
        return phone_number == cls.STATIC_NUMBER
    
    @classmethod
    def get_audio_filename(cls, phone_number: str, text_id: Optional[int] = None) -> str:
        """Audio fayl nomini qaytaradi"""
        if cls.is_static_number(phone_number):
            return f"{cls.STATIC_NUMBER}"
        else:
            return f"audio-{text_id}" if text_id else "default"
    
    @classmethod
    def get_call_context(cls, phone_number: str) -> str:
        """Qo'ng'iroq kontekstini qaytaradi"""
        return cls.SIP_CONTEXT
    
    @classmethod
    def get_call_extension(cls, phone_number: str) -> str:
        """Qo'ng'iroq extensionini qaytaradi"""
        if cls.is_static_number(phone_number):
            return cls.STATIC_NUMBER
        else:
            return "s"
    
    @classmethod
    def ensure_directories(cls):
        """Kerakli kataloglarni yaratadi"""
        for directory in [cls.AUDIO_DIR, cls.TEMP_CALL_DIR, cls.LOG_DIR]:
            os.makedirs(directory, exist_ok=True)
        os.makedirs(os.path.join(cls.ASTERISK_SOUNDS_DIR, "project-audio"), exist_ok=True)
    
    @classmethod
    def validate_phone_number(cls, phone: str) -> bool:
        """Telefon raqamini tekshiradi"""
        # O'zbekiston raqamlari uchun
        if phone.startswith('998') and len(phone) == 12:
            return True
        if phone.startswith('+998') and len(phone) == 13:
            phone = phone[1:]  # + ni olib tashlash
            return True
        return False