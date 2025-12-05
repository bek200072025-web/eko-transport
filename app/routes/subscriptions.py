from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database.db import get_db
from app.database.models import SubscriptionPlan, CompanySubscription, Company

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

# --- ADMIN uchun: yangi obuna turi yaratish ---
@router.post("/plans/create")
def create_subscription_plan(name: str, price: float, duration_days: int = 30, description: str = "", db: Session = Depends(get_db)):
    plan = SubscriptionPlan(
        name=name,
        price=price,
        duration_days=duration_days,
        description=description
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return {"message": "Subscription plan created successfully", "plan": plan}


# --- ADMIN uchun: barcha obuna turlarini ko‘rish ---
@router.get("/plans")
def get_subscription_plans(db: Session = Depends(get_db)):
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return plans


# --- KOMPANIYA uchun: obunaga yozilish ---
@router.post("/company/subscribe/{company_id}/{plan_id}")
def subscribe_company(company_id: int, plan_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    end_date = datetime.utcnow() + timedelta(days=plan.duration_days)

    sub = CompanySubscription(
        company_id=company_id,
        plan_id=plan_id,
        start_date=datetime.utcnow(),
        end_date=end_date,
        is_active=True
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"message": f"{company.name} subscribed to {plan.name} plan", "subscription": sub}


# --- Obunani bekor qilish ---
@router.post("/company/unsubscribe/{company_id}")
def unsubscribe_company(company_id: int, db: Session = Depends(get_db)):
    sub = db.query(CompanySubscription).filter(CompanySubscription.company_id == company_id, CompanySubscription.is_active == True).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Active subscription not found")

    sub.is_active = False
    db.commit()
    return {"message": "Subscription cancelled successfully"}
