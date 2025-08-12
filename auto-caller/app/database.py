import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Config

# .env fayldan ma'lumotlarni yuklaymiz
load_dotenv()

# Use database URL from config
SQLALCHEMY_DATABASE_URL = Config.get_database_url()

# Configure engine based on database type
if Config.USE_SQLITE:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency — FastAPI uchun
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()