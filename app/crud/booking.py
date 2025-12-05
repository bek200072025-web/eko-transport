from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database.models import Booking, Car
from app.schemas.booking import BookingCreate, BookingStatus


def check_car_availability(db: Session, car_id: int, start, end):
    overlap = db.query(Booking).filter(
        Booking.car_id == car_id,
        Booking.status != BookingStatus.cancelled, 
        and_(
            Booking.start_date <= end,
            Booking.end_date >= start
        )
    ).first()
    return overlap is None


def create_booking(db: Session, data: BookingCreate, user_id: int):
    car = db.query(Car).filter(Car.id == data.car_id).first()
    if not car:
        return None

    days = (data.end_date - data.start_date).days + 1
    total_price = car.price_per_day * days
    booking = Booking(
        company_id=data.company_id,
        car_id=data.car_id,
        user_id=user_id,
        start_date=data.start_date,
        end_date=data.end_date,
        total_price=total_price
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def update_booking_status(db: Session, booking_id: int, status: BookingStatus):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return None
    booking.status = status
    db.commit()
    db.refresh(booking)
    return booking
