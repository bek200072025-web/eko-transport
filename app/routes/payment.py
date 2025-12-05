from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.services.payment_service import (
    create_payment_service,
    update_payment_service,
    get_payments_by_booking_service
)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment_service(db, data)


@router.get("/booking/{booking_id}", response_model=list[PaymentResponse])
def get_booking_payments(booking_id: int, db: Session = Depends(get_db)):
    return get_payments_by_booking_service(db, booking_id)


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    return update_payment_service(db, payment_id, data)
