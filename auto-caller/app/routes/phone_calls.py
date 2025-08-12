from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, database

router = APIRouter(prefix="/phone-calls", tags=["Phone Calls"])

get_db = database.get_db

@router.post("/", response_model=schemas.PhoneCallResponse)
def create_phone_call(phone_call: schemas.PhoneCallCreate, db: Session = Depends(get_db)):
    return crud.create_phone_call(db, phone_call)

@router.get("/", response_model=List[schemas.PhoneCallResponse])
def read_phone_calls(db: Session = Depends(get_db)):
    return crud.get_phone_calls(db)

@router.get("/company/{company_id}", response_model=List[schemas.PhoneCallResponse])
def read_calls_by_company(company_id: int, db: Session = Depends(get_db)):
    calls = crud.get_calls_by_company(db, company_id)
    if not calls:
        raise HTTPException(status_code=404, detail="No calls found for this company")
    return calls