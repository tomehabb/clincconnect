from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from routers.auth import get_current_user
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import Users, ProfilePictures
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

class ChangePasswordRequest(BaseModel):
    old_password: str 
    new_password: str
    repeated_password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "",
                "new_password": "",
                "repeated_password": ""
            }
        }
    }

class UpdateUserRequest(BaseModel):
    full_name: str
    email: str
    mobile_number: str


    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "John Doe",
                "email": "example@example.com",
                "mobile_number": "01015164678",
            }
        }
    }


# API endpoint to return the current user information
@router.get("/get_user_information", status_code=status.HTTP_200_OK)
async def get_user_information(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    picture_model = db.query(ProfilePictures).filter(ProfilePictures.user_id == user.get("id")).first()

    profile_picture = ""
    if picture_model is not None:
        profile_picture = f"http://127.0.0.1:8000/picture/profile_image/{picture_model.image_url}"

    return_message = {
        "id": user_model.id,
        "full_name": user_model.full_name,
        "email": user_model.email,
        "mobile_number": user_model.mobile_number,
        "date_of_birth": user_model.date_of_birth,
        "doctor_speciality": user_model.doctor_speciality,
        "profile_picture": profile_picture,

    }

    return return_message

# API endpoint to change user's password
@router.put("/change/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, change_password_request: ChangePasswordRequest):

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model.id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised User")
    
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    
    if change_password_request.new_password != change_password_request.repeated_password:
        raise HTTPException(status_code=400, detail="Password Doesn't match")
    

    if bcrypt_context.verify(change_password_request.old_password, user_model.hashed_password):
        user_model.hashed_password = bcrypt_context.hash(change_password_request.new_password)
        db.add(user_model)
        db.commit()
    else:
        raise HTTPException(status_code=400, detail="Old password doesn't match the password in database")
    
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(db: db_dependency, user:user_dependency, user_id: int):

    user_model = db.query(Users).filter(Users.id == user_id).first()
    picture_model = db.query(ProfilePictures).filter(ProfilePictures.user_id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_picture = ""
    if picture_model is not None:
        profile_picture = f"http://127.0.0.1:8000/picture/profile_image/{picture_model.image_url}"
    
    user_details = {
        "full_name": user_model.full_name,
        "date_of_birth": user_model.date_of_birth,
        "profile_picture": user_model.profile_picture,
        "mobile_number": user_model.mobile_number,
        "doctor_speciality": user_model.doctor_speciality,
        "profile_picture": profile_picture
    }
    return user_details

# @router.post("/update_user_information")
# async def update_user(db: db_dependency, user: user_dependency, update_request: UpdateUserRequest):
#     user_model = db.query(Users).filter(Users.id == user.get("id")).first()

#     user_model.full_name = update_request.full_name
#     user_model.email = update_request.email
#     user_model.mobile_number = update_request.mobile_number


#     db.add(user_model)
#     db.commit

#     return {"message": "User data updated successfully."}


@router.delete("/user_delete")
async def delete_user(db: db_dependency, user: user_dependency):
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User's data doesn't exist")
    db.delete(user_model)
    db.commit()
    return {"message": "user deleted succefully"}