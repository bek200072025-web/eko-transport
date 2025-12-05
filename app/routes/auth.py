from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session
from app.database.db import get_db
from app.database.models import User
from app.schemas.token import TokenData, Token

session = Session()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRY_DAYS = 180
ACCESS_TOKEN_EXPIRY_DAYS = 10

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
login_router = APIRouter(tags=['Login and Refresh token'])


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(data: dict, secret_key: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta \
        if expires_delta else datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRY_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, ALGORITHM)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Hisob maʼlumotlarini tekshirib boʻlmadi",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).where(User.email == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    return current_user


def verify_token(token_data: str, secret_key: str):
    try:
        payload = jwt.decode(token_data, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def is_token_expired(token_data: str, secret_key: str) -> bool:
    payload = verify_token(token_data, secret_key)
    if not payload:
        return True
    return datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0))


@login_router.post("/login", summary="Token yaratish, login")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.email == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Foydalanuvchi topilmadi")

    if not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=400, detail="Parol xato")

    access_token = create_token(
        data={"sub": user.email, "type": "access"},
        secret_key=SECRET_KEY,
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRY_DAYS),
    )

    refresh_token = create_token(
        data={"sub": user.email, "type": "refresh"},
        secret_key=SECRET_KEY,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS),
    )

    db.query(User).filter(User.id == user.id).update({
        User.token: access_token,
        User.refresh_token: refresh_token,
    })
    db.commit()

    return {
        "id": user.id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@login_router.post("/refresh_token", summary="Tokenni yangilash refresh token orqali",
                   response_model=Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.refresh_token == refresh_token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Refresh token yaroqsiz")

    if is_token_expired(refresh_token, SECRET_KEY):
        raise HTTPException(status_code=400, detail="Refresh token muddati tugagan")

    access_token = create_token(
        data={"sub": user.email, "type": "access"},
        secret_key=SECRET_KEY,
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRY_DAYS),
    )

    db.query(User).filter(User.id == user.id).update({
        User.token: access_token,
    })
    db.commit()

    return {
        "id": user.id,
        "access_token": access_token,
        "token_type": "bearer"
    }
