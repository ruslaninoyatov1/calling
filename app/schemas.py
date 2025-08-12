from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

# ===== USERS =====
class UserBase(BaseModel):
    name: str
    login: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ===== COMPANIES =====
class CompanyBase(BaseModel):
    name: str
    link: str
    login: str
    password: str

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    token: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ===== TEXTS =====
class TextBase(BaseModel):
    text: str
    link: Optional[str] = None

class TextCreate(TextBase):
    company_id: int

class TextResponse(TextBase):
    id: int
    company_id: int
    audio_filename: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ===== PHONE CALLS =====
class PhoneCallBase(BaseModel):
    text_id: int
    phone: str
    date: date
    status: int = 0
    call_time: int = 0
    last_date: Optional[date] = None
    company_id: int

class PhoneCallCreate(PhoneCallBase):
    pass

class PhoneCallResponse(PhoneCallBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True