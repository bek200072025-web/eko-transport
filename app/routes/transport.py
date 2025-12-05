from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
import uuid
import os
import shutil
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.database.db import get_db
from app.database.db_operations import get_in_db
from app.database.models import Transport, TransportImage, Company
from app.schemas.transport import TransportCreate, TransportUpdate
from app.routes.auth import get_current_active_user
from app.utils.role_verification import role_verification

router = APIRouter(prefix="/transports", tags=["Transports"])

UPLOAD_DIR = "files"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transport(data: TransportCreate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    role_verification(current_user, "create_transport")
    get_in_db(db, Company, data.company_id)
    transport = Transport(**data.dict())
    db.add(transport)
    db.commit()
    db.refresh(transport)
    return {"data": transport}

@router.post("/{transport_id}/upload-image")
def upload_transport_image(transport_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

    transport = db.query(Transport).filter(Transport.id == transport_id).first()
    if not transport:
        raise HTTPException(404, "Transport topilmadi")

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = TransportImage(transport_id=transport_id, image_url=file_path)
    db.add(image)
    db.commit()

    return {"message": "Rasm yuklandi", "image_url": file_path}

@router.get("/", status_code=status.HTTP_200_OK)
def list_transports(
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    # year_min: Optional[int] = Query(None),
    # year_max: Optional[int] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Transport)

    # Category bo‘yicha filter
    if category:
        query = query.filter(Transport.category.ilike(f"%{category}%"))

    # Brand bo‘yicha filter
    if brand:
        query = query.filter(Transport.brand.ilike(f"%{brand}%"))

    # Yil diapazoni
    # if year_min is not None:
    #     query = query.filter(Transport.year >= year_min)

    # if year_max is not None:
    #     query = query.filter(Transport.year <= year_max)

    # Narx diapazoni
    if price_min is not None:
        query = query.filter(Transport.price_per_day >= price_min)

    if price_max is not None:
        query = query.filter(Transport.price_per_day <= price_max)

    total = query.count()  # umumiy natija
    transports = query.options(joinedload(Transport.images)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "count": len(transports),
        "limit": limit,
        "offset": offset,
        "data": transports
    }

@router.get("/{transport_id}")
def get_transport(transport_id: int, db: Session = Depends(get_db)):
    get_in_db(db, Transport, transport_id)
    transport = db.query(Transport).filter(Transport.id == transport_id).options(joinedload(Transport.images)).first()
    return {"data": transport}

@router.put("/{transport_id}")
def update_transport(transport_id: int, data: TransportUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    role_verification(current_user, "update_transport")
    transport = get_in_db(db, Transport, transport_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(transport, key, value)
    db.commit()
    db.refresh(transport)
    return {"data": transport}

@router.delete("/{transport_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transport(transport_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    role_verification(current_user, "delete_transport")
    transport = get_in_db(db, Transport, transport_id)
    db.delete(transport)
    db.commit()
    return {"data": None}