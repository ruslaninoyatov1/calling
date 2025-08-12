from sqlalchemy import Column, Integer, String, Text, DateTime, Date, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import sqlalchemy as sa

# Use Integer for SQLite compatibility
ID_TYPE = Integer

class Cache(Base):
    __tablename__ = "cache"
    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)
    expiration = Column(Integer, nullable=False)

class CacheLock(Base):
    __tablename__ = "cache_locks"
    key = Column(String(255), primary_key=True)
    owner = Column(String(255), nullable=False)
    expiration = Column(Integer, nullable=False)

class Company(Base):
    __tablename__ = "companies"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    link = Column(String(255), nullable=False)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    texts = relationship("Text", back_populates="company", cascade="all, delete-orphan")
    phone_calls = relationship("PhoneCall", back_populates="company", cascade="all, delete-orphan")

class FailedJob(Base):
    __tablename__ = "failed_jobs"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    uuid = Column(String(255), nullable=False, unique=True)
    connection = Column(Text, nullable=False)
    queue = Column(Text, nullable=False)
    payload = Column(Text, nullable=False)
    exception = Column(Text, nullable=False)
    failed_at = Column(DateTime, nullable=False, server_default=func.now())

class JobBatch(Base):
    __tablename__ = "job_batches"
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    total_jobs = Column(Integer, nullable=False)
    pending_jobs = Column(Integer, nullable=False)
    failed_jobs = Column(Integer, nullable=False)
    failed_job_ids = Column(Text, nullable=False)
    options = Column(Text, nullable=True)
    cancelled_at = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False)
    finished_at = Column(Integer, nullable=True)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    queue = Column(String(255), nullable=False)
    payload = Column(Text, nullable=False)
    attempts = Column(SmallInteger, nullable=False)
    reserved_at = Column(Integer, nullable=True)
    available_at = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False)

class Migration(Base):
    __tablename__ = "migrations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    migration = Column(String(255), nullable=False)
    batch = Column(Integer, nullable=False)

class PersonalAccessToken(Base):
    __tablename__ = "personal_access_tokens"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    tokenable_type = Column(String(255), nullable=False)
    tokenable_id = Column(ID_TYPE, nullable=False)
    name = Column(Text, nullable=False)
    token = Column(String(64), nullable=False, unique=True)
    abilities = Column(Text, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String(255), primary_key=True)
    user_id = Column(ID_TYPE, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    payload = Column(Text, nullable=False)
    last_activity = Column(Integer, nullable=False)

class Text(Base):
    __tablename__ = "texts"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    company_id = Column(ID_TYPE, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(255), nullable=False)
    link = Column(String(255), nullable=True)
    audio_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    company = relationship("Company", back_populates="texts")
    phone_calls = relationship("PhoneCall", back_populates="text", cascade="all, delete-orphan")

class PhoneCall(Base):
    __tablename__ = "phone_calls"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    company_id = Column(ID_TYPE, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    text_id = Column(ID_TYPE, ForeignKey("texts.id", ondelete="CASCADE"), nullable=False)
    phone = Column(String(255), nullable=False)
    status = Column(SmallInteger, nullable=False, default=0)  # 0: pending, 1: completed, 2: failed
    date = Column(Date, nullable=False)
    call_time = Column(SmallInteger, nullable=False, default=0)
    last_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    company = relationship("Company", back_populates="phone_calls")
    text = relationship("Text", back_populates="phone_calls")
    logs = relationship("CallLog", back_populates="phone_call", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    login = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

class CallLog(Base):
    __tablename__ = "call_logs"
    id = Column(ID_TYPE, primary_key=True, autoincrement=True)
    phone_call_id = Column(ID_TYPE, ForeignKey("phone_calls.id", ondelete="CASCADE"), nullable=False)
    message = Column(sa.Text, nullable=False)
    level = Column(String(50), nullable=False)  # INFO, ERROR, WARNING
    created_at = Column(DateTime, nullable=False, default=func.now())
    phone_call = relationship("PhoneCall", back_populates="logs")