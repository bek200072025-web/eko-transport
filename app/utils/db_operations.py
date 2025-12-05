from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def get_in_db(db, model, ident: int):
    obj = db.query(model).filter(model.id == ident).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bazada bunday {model.__name__} yo'q")
    return obj


def save_in_db(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj