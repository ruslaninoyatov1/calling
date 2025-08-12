from sqlalchemy.orm import Session
from app import models, schemas
import uuid
from typing import List, Optional
import os

# ===== CONFIG =====
AUDIO_DIR = "app/static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ===== COMPANIES =====

def create_company(db: Session, company: schemas.CompanyCreate) -> models.Company:
    db_company = models.Company(
        name=company.name,
        link=company.link,
        login=company.login,
        password=company.password,
        token=str(uuid.uuid4())
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_companies(db: Session) -> List[models.Company]:
    return db.query(models.Company).all()

def get_company(db: Session, company_id: int) -> Optional[models.Company]:
    return db.query(models.Company).filter(models.Company.id == company_id).first()

# ===== USERS =====

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        name=user.name,
        login=user.login,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()

def get_user_by_login(db: Session, login: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.login == login).first()

# ===== TEXTS =====
def create_text(db: Session, text: schemas.TextCreate) -> models.Text:
    db_text = models.Text(
        company_id=text.company_id,
        text=text.text,
    )
    db.add(db_text)
    db.commit()
    db.refresh(db_text)

    if text.text:
        try:
            from app import tts
            filename_prefix = f"audio-{db_text.id}"
            success = tts.text_to_speech(text.text, filename_prefix)
            
            if success:
                db_text.audio_filename = filename_prefix
                db.commit()
                db.refresh(db_text)
            else:
                raise ValueError("Audio generation failed")
        except Exception as e:
            raise ValueError(f"TTS generation failed: {e}")

    return db_text

def get_texts(db: Session) -> List[models.Text]:
    return db.query(models.Text).all()

def get_texts_by_company(db: Session, company_id: int) -> List[models.Text]:
    return db.query(models.Text).filter(models.Text.company_id == company_id).all()

# ===== PHONE CALLS =====

def create_phone_call(db: Session, call: schemas.PhoneCallCreate) -> models.PhoneCall:
    db_call = models.PhoneCall(
        phone=call.phone,
        status=call.status,
        date=call.date,
        call_time=call.call_time,
        last_date=call.last_date,
        company_id=call.company_id,
        text_id=call.text_id
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call

def get_phone_calls(db: Session) -> List[models.PhoneCall]:
    return db.query(models.PhoneCall).all()

def get_calls_by_company(db: Session, company_id: int) -> List[models.PhoneCall]:
    return db.query(models.PhoneCall).filter(models.PhoneCall.company_id == company_id).all()