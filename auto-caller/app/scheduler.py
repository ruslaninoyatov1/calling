import time
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app import database, crud, call, time_checker
from app.models import PhoneCall

# Logger yaratish
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler qo'shish
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def check_and_make_calls():
    """
    Ma'lumotlar bazasini tekshirib, kerakli qo'ng'iroqlarni amalga oshiradi.
    Faqat ertalab 7:00 dan 14:00 gacha bo'lgan vaqtda ishlaydi.
    """
    # Vaqtni tekshirish
    is_within_time, current_time_str = time_checker.is_within_call_time()
    
    if not is_within_time:
        logger.info(f"Vaqt chegarasidan tashqari: {current_time_str}. Qo'ng'iroq qilinmaydi.")
        return
    
    logger.info(f"Vaqt mos keladi: {current_time_str}. Ma'lumotlar bazasini tekshirish boshlanmoqda...")
    
    # Database session yaratish
    db = database.SessionLocal()
    
    try:
        # Barcha qo'ng'iroqlarni olish
        phone_calls = crud.get_phone_calls(db)
        
        # Bugungi sana
        today = datetime.now().date()
        
        # Har bir qo'ng'iroqni tekshirish
        for phone_call in phone_calls:
            # Agar qo'ng'iroq hali amalga oshirilmagan bo'lsa va bugun amalga oshirilishi kerak bo'lsa
            if phone_call.status == 0 and phone_call.date == today:
                try:
                    logger.info(f"Qo'ng'iroq amalga oshirilmoqda: {phone_call.phone}")
                    
                    # Text obyektini olish
                    text_obj = phone_call.text
                    
                    # Audio fayl nomini olish
                    audio_filename = text_obj.audio_filename
                    
                    if not audio_filename:
                        logger.error(f"Audio fayl nomi mavjud emas: {phone_call.phone}")
                        continue
                    
                    # Qo'ng'iroqni amalga oshirish
                    call.place_call(phone_call.phone, audio_filename)
                    
                    # Qo'ng'iroq holatini yangilash
                    phone_call.status = 1  # Completed
                    phone_call.last_date = today
                    
                    db.commit()
                    logger.info(f"Qo'ng'iroq muvaffaqiyatli amalga oshirildi: {phone_call.phone}")
                    
                except Exception as e:
                    logger.error(f"Qo'ng'iroqda xatolik yuz berdi: {phone_call.phone}, xato: {str(e)}")
                    # Qo'ng'iroq holatini xato sifatida belgilash
                    phone_call.status = 2  # Failed
                    db.commit()
                    
    except Exception as e:
        logger.error(f"Ma'lumotlar bazasini tekshirishda xatolik yuz berdi: {str(e)}")
    finally:
        db.close()

def run_scheduler():
    """
    Har 5 daqiqada bir marta ma'lumotlar bazasini tekshirish uchun scheduler.
    """
    logger.info("Scheduler ishga tushdi...")
    
    while True:
        try:
            check_and_make_calls()
            
            # Keyingi 5 daqiqagacha kutish
            time.sleep(300)  # 300 soniya = 5 daqiqa
        except KeyboardInterrupt:
            logger.info("Scheduler to'xtatildi.")
            break
        except Exception as e:
            logger.error(f"Schedulerda xatolik yuz berdi: {str(e)}")
            time.sleep(60)  # Xatolik yuz berganda 1 daqiqa kutish

if __name__ == "__main__":
    run_scheduler()