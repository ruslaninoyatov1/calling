from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, database

router = APIRouter(prefix="/texts", tags=["Texts"])

get_db = database.get_db

@router.post("/", response_model=schemas.TextResponse)
def create_text(text: schemas.TextCreate, db: Session = Depends(get_db)):
    return crud.create_text(db, text)

@router.get("/", response_model=List[schemas.TextResponse])
def read_texts(db: Session = Depends(get_db)):
    return crud.get_texts(db)

@router.get("/company/{company_id}", response_model=List[schemas.TextResponse])
def read_texts_by_company(company_id: int, db: Session = Depends(get_db)):
    texts = crud.get_texts_by_company(db, company_id)
    if not texts:
        raise HTTPException(status_code=404, detail="No texts found for this company")
    return texts