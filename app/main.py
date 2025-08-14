from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, tts, call
from app.config import Config
import uuid
import os
import time
from datetime import datetime

app = FastAPI(title="AutoCaller API")

# Create tables on startup
try:
    models.Base.metadata.create_all(bind=database.engine)
except Exception as e:
    print(f"⚠️ Database table creation warning: {e}")

Config.ensure_directories()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/companies/", response_model=schemas.CompanyResponse)
def create_company(data: schemas.CompanyCreate, db: Session = Depends(get_db)):
    try:
        from app import crud
        company = crud.create_company(db, data)
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company creation failed: {str(e)}")

@app.get("/companies/", response_model=list[schemas.CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).all()

@app.post("/texts/", response_model=schemas.TextResponse)
def create_text(data: schemas.TextCreate, db: Session = Depends(get_db)):
    try:
        # Kompaniyani tekshirish
        company = db.query(models.Company).filter_by(id=data.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        from app import crud
        return crud.create_text(db, data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text creation failed: {str(e)}"
        )
    
@app.get("/texts/", response_model=list[schemas.TextResponse])
def list_texts(db: Session = Depends(get_db)):
    return db.query(models.Text).all()

@app.post("/phone-calls/", response_model=schemas.PhoneCallResponse)
def create_phone_call(data: schemas.PhoneCallCreate, db: Session = Depends(get_db)):
    try:
        text_obj = db.query(models.Text).filter_by(id=data.text_id).first()
        if not text_obj:
            raise HTTPException(status_code=404, detail="Text topilmadi")

        audio_filename = text_obj.audio_filename
        if not audio_filename:
            raise HTTPException(status_code=400, detail="Audio fayl nomi mavjud emas")

        audio_path = os.path.join(Config.ASTERISK_SOUNDS_DIR, "project-audio", f"{audio_filename}.wav")
        if not os.path.isfile(audio_path):
            raise HTTPException(status_code=400, detail="Audio fayl topilmadi")

        company = text_obj.company
        trunk_name = getattr(company, "trunk_name", None) or None
        call.place_call(data.phone, audio_filename, trunk_name=trunk_name)

        phone_call_instance = models.PhoneCall(
            company_id=text_obj.company_id,
            text_id=data.text_id,
            phone=data.phone,
            date=data.date,
            status=0,
            call_time=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(phone_call_instance)
        db.commit()
        db.refresh(phone_call_instance)

        log_entry = models.CallLog(
            phone_call_id=phone_call_instance.id,
            message=f"Qo'ng'iroq yaratildi: {data.phone}",
            level="INFO"
        )
        db.add(log_entry)
        db.commit()

        return phone_call_instance
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Phone call creation failed: {str(e)}")

@app.get("/phone-calls/", response_model=list[schemas.PhoneCallResponse])
def list_phone_calls(db: Session = Depends(get_db)):
    return db.query(models.PhoneCall).all()

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = models.User(
            name=data.name,
            login=data.login,
            password=data.password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

@app.get("/users/", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Scheduler uchun import
from app.scheduler import run_scheduler
import threading

# Scheduler threadini ishga tushirish
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()