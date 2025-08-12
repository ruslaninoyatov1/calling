import datetime
import pytz
from typing import Tuple

def is_within_call_time() -> Tuple[bool, str]:
    """
    Toshkent vaqtida ertalab 8:00 dan 18:00 gacha bo'lgan vaqtni tekshiradi.
    
    Returns:
        Tuple[bool, str]: (vaqt mos keladimi, hozirgi vaqt)
    """
    # Toshkent vaqt mintaqasini olish
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    
    # Hozirgi vaqtni matn sifatida qaytarish
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # Vaqtni tekshirish (8:00 dan 18:00 gacha)
    current_hour = now.hour
    
    if 8 <= current_hour < 18:
        return True, current_time_str
    else:
        return False, current_time_str

def get_next_call_time() -> datetime.datetime:
    """
    Keyingi qo'ng'iroq vaqtini hisoblaydi.
    Agar hozirgi vaqt 8:00 dan oldin bo'lsa, bugun soat 8:00 ni qaytaradi.
    Agar hozirgi vaqt 18:00 dan keyin bo'lsa, ertaga soat 8:00 ni qaytaradi.
    Agar hozirgi vaqt 8:00-18:00 orasida bo'lsa, keyingi 5 daqiqani qaytaradi.
    
    Returns:
        datetime.datetime: Keyingi qo'ng'iroq vaqti
    """
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.datetime.now(tz)
    
    # 5 daqiqalik interval
    minutes = now.minute
    next_minutes = ((minutes // 5) + 1) * 5
    
    if next_minutes >= 60:
        # Keyingi soatga o'tish
        next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    else:
        next_time = now.replace(minute=next_minutes, second=0, microsecond=0)
    
    # Agar hozirgi vaqt 8:00 dan oldin bo'lsa, bugun soat 8:00
    if now.hour < 8:
        return now.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Agar hozirgi vaqt 18:00 dan keyin bo'lsa, ertaga soat 8:00
    if now.hour >= 18:
        return (now + datetime.timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Agar hozirgi vaqt 8:00-18:00 orasida bo'lsa, keyingi 5 daqiqani qaytaramiz
    return next_time