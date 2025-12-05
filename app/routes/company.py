from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.routes.auth import get_current_active_user
from app.utils import role_verification
from app.utils.db_operations import get_in_db

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # 1. Kompaniya nomi bo'yicha tekshirish (ixtiyoriy, lekin foydali)
    existing = db.query(Company).filter(Company.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bu nom bilan kompaniya allaqachon mavjud."
        )

    new_company = Company(
        name=data.name,
        phone=data.phone,
        region=data.region,
        address=data.address,
        description=data.description,
        owner_id=current_user.id
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company



@router.get("/", status_code=status.HTTP_200_OK,
            summary="List Companies, admin panel uchun",
            description="Retrieve a list of companies. Boss users can see all companies, while regular users")
def list_companies(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    if current_user.role == 'boss':
        return {"data": db.query(Company).all()}
    return {"data": db.query(Company).filter(Company.owner_id == current_user.id).all()}


@router.get("/{company_id}", status_code=status.HTTP_200_OK)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = get_in_db(db, Company, company_id)
    return {"data": company}


@router.put("/{company_id}", response_model=CompanyResponse, status_code=status.HTTP_200_OK)
def update_company(company_id: int, data: CompanyUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    company = get_in_db(db, Company, company_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return {"data": company}


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    role_verification(current_user, "delete_company")
    company = get_in_db(db, Company, company_id)
    db.delete(company)
    db.commit()
    return {"data": None}
