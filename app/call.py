import os
import shutil
import uuid
import logging
from typing import List, Optional
from app.config import Config

logger = logging.getLogger(__name__)

def setup_logging():
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(Config.LOG_DIR, "call.log")),
            logging.StreamHandler()
        ]
    )

setup_logging()

def verify_audio_file(audio_filename: str) -> bool:
    """Audio fayl mavjudligini tekshiradi"""
    sounds_dir = os.path.join(Config.ASTERISK_SOUNDS_DIR, "project-audio")
    supported_formats = [".wav", ".alaw", ".gsm"]
    
    for ext in supported_formats:
        file_path = os.path.join(sounds_dir, f"{audio_filename}{ext}")
        if os.path.isfile(file_path):
            logger.info(f"Found audio file: {file_path}")
            return True
    
    logger.error(f"No audio file found for {audio_filename} in {sounds_dir}")
    return False

def generate_call_content(phone_number: str, audio_filename: str, trunk_name: Optional[str] = None) -> str:
    """Call fayli uchun kontent yaratish"""
    context = Config.get_call_context(phone_number)
    extension = Config.get_call_extension(phone_number)
    channel_trunk = trunk_name or "skyline"
    
    return (
        f"Channel: SIP/{channel_trunk}/{phone_number}\n"
        f"CallerID: \"AutoCaller\" <{phone_number}>\n"
        f"MaxRetries: 0\n"
        f"RetryTime: 60\n"
        f"WaitTime: 30\n"
        f"Context: {context}\n"
        f"Extension: {extension}\n"
        f"Priority: 1\n"
        f"Set: AUDIOFILE={audio_filename}\n"
    )

def place_call(phone_number: str, audio_filename: str, trunk_name: Optional[str] = None) -> str:
    """Bitta raqamga qo'ng'iroq qilish"""
    try:
        # Audio faylni tekshirish
        if not verify_audio_file(audio_filename):
            raise FileNotFoundError(f"Audio file {audio_filename} not found in Asterisk directory")

        # Call faylini yaratish
        unique_id = uuid.uuid4().hex[:8]
        call_filename = f"{phone_number}-{unique_id}.call"
        temp_call_path = os.path.join(Config.TEMP_CALL_DIR, call_filename)
        final_call_path = os.path.join(Config.CALL_DIR, call_filename)

        # Kataloglarni yaratish
        os.makedirs(Config.TEMP_CALL_DIR, exist_ok=True)
        os.makedirs(Config.CALL_DIR, exist_ok=True)

        # Fayl kontentini yozish
        content = generate_call_content(phone_number, audio_filename, trunk_name)
        with open(temp_call_path, "w") as f:
            f.write(content)

        # Faylni asosiy katalogga ko'chirish
        shutil.move(temp_call_path, final_call_path)
        
        # Permissionlarni o'rnatish
        os.chmod(final_call_path, 0o644)
        
        logger.info(f"Call file created: {final_call_path}")
        return call_filename

    except Exception as e:
        logger.error(f"Failed to place call to {phone_number}: {e}")
        raise