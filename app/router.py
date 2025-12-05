from fastapi import APIRouter
from app.routes.auth import login_router
from app.routes.admin import router as user_router
from app.routes.transport import router as tr_router
# from app.routes.booking import router as bookings_router
# from app.routes.payment import router as payments_router
from app.routes.company import router as companies_router

from app.database.db import Base, engine

api = APIRouter()
Base.metadata.create_all(bind=engine)

api.include_router(login_router)
api.include_router(user_router)
api.include_router(companies_router)
# api.include_router(payments_router)
api.include_router(tr_router)
# api.include_router(bookings_router)
