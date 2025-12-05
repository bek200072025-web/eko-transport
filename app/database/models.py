from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Date
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.db import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    boss = "boss"


class BookingStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    cancelled = "cancelled"
    completed = "completed"


class PaymentStatus(str, enum.Enum):
    tolangan = "to‘langan"
    tolanmagan = "to‘lanmagan"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.admin)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)

    companies = relationship("Company", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="users", cascade="all, delete")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(String)
    address = Column(String)
    phone = Column(String)
    region = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="companies")
    transports = relationship("Transport", back_populates="companies", cascade="all, delete")
    bookings = relationship("Booking", back_populates="companies", cascade="all, delete")


class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    model = Column(String, nullable=False)
    category = Column(String)
    brand = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price_per_day = Column(Float, nullable=False)
    transmission = Column(String)
    fuel_type = Column(String)
    seats = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    companies = relationship("Company", back_populates="transports")
    images = relationship("TransportImage", back_populates="transports", cascade="all, delete")
    bookings = relationship("Booking", back_populates="transports", cascade="all, delete")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    transport_id = Column(Integer, ForeignKey("transports.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    companies = relationship("Company", back_populates="bookings")
    transports = relationship("Transport", back_populates="bookings")
    users = relationship("User", back_populates="bookings")
    payments = relationship("Payment", back_populates="bookings", cascade="all, delete")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"))
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.tolanmagan)
    payment_date = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="payments")


class TransportImage(Base):
    __tablename__ = 'transport_images'

    id = Column(Integer, primary_key=True, index=True)
    transport_id = Column(Integer, ForeignKey("transports.id", ondelete="CASCADE"))
    image_url = Column(String)

    transports = relationship("Transport", back_populates="images")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    