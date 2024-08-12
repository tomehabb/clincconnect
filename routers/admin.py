from typing import Annotated
from database import SessionLocal
from models import Users
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from routers.auth import get_current_user


router = APIRouter(prefix="/admin", tags=['admin'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/get_all_users", status_code=status.HTTP_200_OK)
async def get_all_users(user: user_dependency, db: db_dependency):
    if not user.get('user_role') == 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

    all_users = db.query(Users).all()

    return all_users