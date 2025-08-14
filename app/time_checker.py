import datetime
import pytz
from typing import Tuple
from app.config import Config

def _parse_hhmm(value: str) -> tuple[int, int]:
    parts = value.split(":", 1)
    return int(parts[0]), int(parts[1])

def is_within_call_time() -> Tuple[bool, str]:
    """
    Toshkent vaqtida Config.CALL_START dan Config.CALL_END gacha bo'lgan vaqtni tekshiradi.
    
    Returns:
        Tuple[bool, str]: (vaqt mos keladimi, hozirgi vaqt)
    """
    # Toshkent vaqt mintaqasini olish
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    
    # Hozirgi vaqtni matn sifatida qaytarish
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # Vaqtni tekshirish (CALL_START dan CALL_END gacha)
    start_h, start_m = _parse_hhmm(Config.CALL_START)
    end_h, end_m = _parse_hhmm(Config.CALL_END)
    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m
    curr_minutes = now.hour * 60 + now.minute
    
    return (start_minutes <= curr_minutes <= end_minutes), current_time_str

def get_next_call_time() -> datetime.datetime:
    """
    Keyingi qo'ng'iroq vaqtini hisoblaydi, 5 daqiqali bo'lib, ish vaqti oralig'ida bo'ladi.
    """
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    
    start_h, start_m = _parse_hhmm(Config.CALL_START)
    end_h, end_m = _parse_hhmm(Config.CALL_END)
    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m
    
    # 5 daqiqalik interval
    minutes = now.minute
    next_minutes = ((minutes // 5) + 1) * 5
    candidate = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=next_minutes)
    
    curr_minutes = now.hour * 60 + now.minute
    
    if curr_minutes < start_minutes:
        return now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    if curr_minutes > end_minutes:
        return (now + datetime.timedelta(days=1)).replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    
    # Agar ish vaqtida bo'lsa, keyingi 5 daqiqani qaytaradi, lekin end_minutes dan oshmaydi
    cand_minutes = candidate.hour * 60 + candidate.minute
    if cand_minutes > end_minutes:
        return (now + datetime.timedelta(days=1)).replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    return candidate