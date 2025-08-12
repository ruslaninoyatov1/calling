from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, database

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)

get_db = database.get_db

@router.post("/", response_model=schemas.CompanyResponse)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    return crud.create_company(db, company)

@router.get("/", response_model=List[schemas.CompanyResponse])
def read_companies(db: Session = Depends(get_db)):
    return crud.get_companies(db)

@router.get("/{company_id}", response_model=schemas.CompanyResponse)
def read_company(company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company