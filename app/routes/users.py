from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas, database
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=schemas.UserResponse)
def create_user(data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.login == data.login).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already exists")
    user = models.User(
        name=data.name,
        login=data.login,
        password=pwd_context.hash(data.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()