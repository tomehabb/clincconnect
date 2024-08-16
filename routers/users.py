from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from routers.auth import get_current_user
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import Users
from starlette import status

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


router = APIRouter(prefix="/user", tags=['user'])


# API endpoint to return the current user information
@router.get("/get_user_information", status_code=status.HTTP_200_OK)
async def get_user_information(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    return user_model