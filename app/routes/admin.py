from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.routes.auth import get_current_active_user
from app.schemas.user import UserCreate, UserUpdate
from app.utils import role_verification
from app.routes.auth import get_password_hash

router = APIRouter(prefix='/admin', tags=['admin and boss role operations'])

@router.post('/', status_code=status.HTTP_201_CREATED)
def register_admin(data: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    role_verification(current_user, "register_admin")
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bu email bilan foydalanuvchi allaqachon mavjud."
        )

    hashed_password = get_password_hash(data.password)

    new_user = User(
        fullname=data.fullname,
        email=data.email,
        password=hashed_password,
        phone=data.phone,
        role="admin",               # ADMIN ROLE
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "data": {
            "id": new_user.id,
            "fullname": new_user.fullname,
            "email": new_user.email,
            "phone": new_user.phone,
            "role": new_user.role
        }
    }

@router.get('/', status_code=status.HTTP_200_OK)
def get_me(current_user=Depends(get_current_active_user)):
    return {"data": current_user}

@router.get('/all', summary="faqat bosh uchun", status_code=status.HTTP_200_OK)
def get_all(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    if current_user.role == "boss":
        return {"data": db.query(User).all()}
    raise HTTPException(400, "Sizga ruxsat berilmagan")
    
@router.put('/', status_code=status.HTTP_200_OK)
def update_user(data: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    db.query(User).filter(User.id == current_user.id).update({
        User.fullname: data.fullname,
        User.phone: data.phone,
        User.email: data.email,
        User.password: get_password_hash(data.password)
    })
    db.commit()
    db.refresh(current_user)
    return {"data": current_user}

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    db.delete(current_user)
    db.commit()
    return {"data": None}