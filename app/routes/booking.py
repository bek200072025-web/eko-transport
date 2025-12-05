from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db

from app.schemas.booking import BookingCreate, BookingResponse, BookingStatus
from app.services.booking_service import (
    service_create_booking,
    service_change_status
)


router = APIRouter(prefix="/booking", tags=["Booking"])


# --- FOYDALANUVCHI BOOKING QILADI ---
@router.post("/", response_model=BookingResponse)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return service_create_booking(db, user.id, data)


# --- ADMIN STATUS O'ZGARTIRADI ---
@router.put("/{booking_id}/status")
def change_status(
    booking_id: int,
    status: BookingStatus,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return service_change_status(db, booking_id, status)


# --- ADMIN BARCHA BOOKINGLARNI KO'RADI ---
@router.get("/")
def get_all_bookings(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    from app.database.models import Booking
    return db.query(Booking).all()
