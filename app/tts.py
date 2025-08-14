import os
import requests
import subprocess
import shutil
import base64
from typing import Optional
from app.config import Config
import logging

logger = logging.getLogger(__name__)

def _run_cmd(cmd: list) -> tuple[bool, str, str]:
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}, Error: {e}")
        return False, e.stdout.strip(), e.stderr.strip() or str(e)

def convert_audio(input_path: str, output_path: str, codec: str, sample_rate: str = "8000") -> bool:
    """Umumiy audio konvertatsiya funksiyasi"""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", sample_rate, "-ac", "1",
        "-c:a", codec,
        "-f", "wav" if codec in ["pcm_alaw", "pcm_s16le"] else codec,
        output_path
    ]
    success, _, _ = _run_cmd(cmd)
    return success

def _ensure_asterisk_permissions(file_path: str):
    """Fayl uchun kerakli permissionlarni o'rnatish"""
    try:
        os.chmod(file_path, 0o644)
        import pwd, grp
        uid = pwd.getpwnam("asterisk").pw_uid
        gid = grp.getgrnam("asterisk").gr_gid
        os.chown(file_path, uid, gid)
    except Exception as e:
        logger.warning(f"Could not set permissions for {file_path}: {e}")

def _copy_to_asterisk(src: str, dst_dir: str) -> bool:
    """Faylni Asterisk katalogiga nusxalash"""
    try:
        if not os.path.exists(src):
            logger.error(f"Source file not found: {src}")
            return False

        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, os.path.basename(src))

        # Avval vaqtinchalik faylga nusxa olamiz
        temp_dst = f"{dst}.tmp"
        shutil.copy2(src, temp_dst)
        
        # Keyin asosiy faylga o'tkazamiz
        os.rename(temp_dst, dst)
        
        _ensure_asterisk_permissions(dst)
        return True
    except Exception as e:
        logger.error(f"Failed to copy {src} to {dst_dir}: {e}")
        return False

def text_to_speech(text: str, audio_filename: str, speaker_id: int = 1) -> bool:
    """Matnni audio faylga aylantirish"""
    try:
        # Kataloglarni yaratish
        local_dir = Config.AUDIO_DIR
        asterisk_dir = os.path.join(Config.ASTERISK_SOUNDS_DIR, "project-audio")
        os.makedirs(local_dir, exist_ok=True)
        os.makedirs(asterisk_dir, exist_ok=True)

        # Fayl yo'llari
        mp3_path = os.path.join(local_dir, f"{audio_filename}.mp3")
        wav_path = os.path.join(local_dir, f"{audio_filename}.wav")
        alaw_path = os.path.join(local_dir, f"{audio_filename}.alaw")
        gsm_path = os.path.join(local_dir, f"{audio_filename}.gsm")

        # TTS API so'rovini yuborish
        headers = {
            "Content-Type": "application/json",
            "x-api-key": Config.MUXLISA_API_KEY
        }
        payload = {"text": text, "speaker": speaker_id}

        response = requests.post(
            Config.MUXLISA_TTS_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            logger.error(f"TTS API error: {response.status_code} - {response.text}")
            return False

        # Audio faylni saqlash
        content_type = response.headers.get("Content-Type", "").lower()
        
        if content_type.startswith("audio/"):
            if "wav" in content_type:
                audio_data = response.content
                with open(wav_path, "wb") as f:
                    f.write(audio_data)
            else:
                with open(mp3_path, "wb") as f:
                    f.write(response.content)
                if not convert_audio(mp3_path, wav_path, "pcm_s16le"):
                    return False
        else:
            try:
                audio_data = base64.b64decode(response.json().get("audio"))
                with open(wav_path, "wb") as f:
                    f.write(audio_data)
            except Exception as e:
                logger.error(f"Audio decoding failed: {e}")
                return False

        # Qo'shimcha formatlarga konvertatsiya
        if not convert_audio(wav_path, alaw_path, "pcm_alaw"):
            logger.warning("ALAW conversion failed")
        
        if not convert_audio(wav_path, gsm_path, "gsm"):
            logger.warning("GSM conversion failed")

        # Asterisk katalogiga nusxalash
        formats = [
            (wav_path, f"{audio_filename}.wav"),
            (alaw_path, f"{audio_filename}.alaw"),
            (gsm_path, f"{audio_filename}.gsm")
        ]

        for src, dst_name in formats:
            if os.path.exists(src):
                dst = os.path.join(asterisk_dir, dst_name)
                if not _copy_to_asterisk(src, asterisk_dir):
                    logger.error(f"Failed to copy {src} to Asterisk directory")
                    return False

        logger.info(f"Successfully generated audio files for {audio_filename}")
        return True

    except Exception as e:
        logger.error(f"TTS processing failed: {e}")
        return False

def import_audio_from_link(link: str, audio_filename: str) -> bool:
    """Berilgan linkdan audio yuklab olib, kerakli formatlarga o'tkazib Asteriskga joylaydi"""
    try:
        local_dir = Config.AUDIO_DIR
        asterisk_dir = os.path.join(Config.ASTERISK_SOUNDS_DIR, "project-audio")
        os.makedirs(local_dir, exist_ok=True)
        os.makedirs(asterisk_dir, exist_ok=True)

        # Fayl yo'llari
        src_path = os.path.join(local_dir, f"{audio_filename}.src")
        wav_path = os.path.join(local_dir, f"{audio_filename}.wav")
        alaw_path = os.path.join(local_dir, f"{audio_filename}.alaw")
        gsm_path = os.path.join(local_dir, f"{audio_filename}.gsm")

        # Yuklab olish
        r = requests.get(link, timeout=60, stream=True)
        r.raise_for_status()
        with open(src_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Source formatdan WAV ga o'tkazish
        if not convert_audio(src_path, wav_path, "pcm_s16le"):
            return False

        # Qo'shimcha formatlarga konvertatsiya
        if not convert_audio(wav_path, alaw_path, "pcm_alaw"):
            logger.warning("ALAW conversion failed")
        if not convert_audio(wav_path, gsm_path, "gsm"):
            logger.warning("GSM conversion failed")

        # Asteriskga nusxa
        for src in (wav_path, alaw_path, gsm_path):
            if os.path.exists(src):
                if not _copy_to_asterisk(src, asterisk_dir):
                    logger.error(f"Failed to copy {src} to Asterisk directory")
                    return False

        logger.info(f"Successfully imported audio from link for {audio_filename}")
        return True
    except Exception as e:
        logger.error(f"Audio import failed: {e}")
        return False