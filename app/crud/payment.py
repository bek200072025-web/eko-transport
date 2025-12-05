from sqlalchemy.orm import Session
from app.database.models import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate


def create_payment(db: Session, data: PaymentCreate):
    payment = Payment(**data.dict())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payments_by_booking(db: Session, booking_id: int):
    return db.query(Payment).filter(Payment.booking_id == booking_id).all()


def update_payment(db: Session, payment_id: int, data: PaymentUpdate):
    payment = get_payment(db, payment_id)
    if not payment:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(payment, key, value)

    db.commit()
    db.refresh(payment)
    return payment
