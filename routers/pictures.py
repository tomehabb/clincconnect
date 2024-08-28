from typing import Annotated
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
import os
from database import SessionLocal
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from models import Clinics, Users, ProfilePictures, ClinicPictures
import uuid
from typing import List



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

async def save_image(image: UploadFile):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="The uploaded file is not an image")
    
    file_extension = image.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    directory = "images/clinic_pictures"
    if not os.path.exists(directory):
        os.makedirs(directory)

    save_path = os.path.join(directory, unique_filename)
    with open(save_path, "wb") as f:
        f.write(await image.read())

    return unique_filename

router = APIRouter(prefix="/picture", tags=['picture'])

@router.post("/upload_profile_picture")
async def upload_profile_picture(db: db_dependency, user: user_dependency, profile_picture: UploadFile = File(...)):

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Check the file type
    if not profile_picture.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="The uploaded file is not an image")
    
    file_extension = profile_picture.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Define the path to save the image
    directory = "images/profile_pictures"
    if not os.path.exists(directory):
        os.makedirs(directory)

    save_path = os.path.join(directory, unique_filename)
    with open(save_path, "wb") as f:
        f.write(await profile_picture.read())
    
    picture_model = db.query(ProfilePictures).filter(ProfilePictures.user_id == user.get("id")).first()

    if picture_model is None:

        picture_model = ProfilePictures(
            user_id = user_model.id,
            image_url = unique_filename
        )   
        db.add(picture_model)
        db.commit()
    else:
        picture_model.user_id = user_model.id
        picture_model.image_url = unique_filename
        db.add(picture_model)
        db.commit()
    

    return {"message": "Image uploaded successfuly"}

@router.get("/profile_image/{filename}", status_code=200)
async def get_user_image(filename: str):
    directory = "images/profile_pictures"
    file_path = os.path.join(directory, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)

@router.delete("/profile_picture/{id}")
async def delete_profile_picture(user: user_dependency,db: db_dependency, id: int):
    picture_model = db.query(ProfilePictures).filter(ProfilePictures.id == id).first()

    if picture_model is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    db.delete(picture_model)
    db.commit()

    return {"message": "Image deleted successfully"}



@router.post("/add_clinic_pictures")
async def add_clinic_pictures(db: db_dependency, user: user_dependency ,clinic_id: int = Form(...), images: List[UploadFile] = File(...)):

    clinic_model = db.query(Clinics).filter(Clinics.id == clinic_id).first()
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not clinic_model or not user_model:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    if not user_model.id == clinic_model.owner_id:
        raise HTTPException(status_code=401, detail="it's not your clinic bro")
    
    for image in images:
        file_name = await save_image(image)
        picture = ClinicPictures(
            clinic_id = clinic_id,
            image_url = file_name 
        )
        db.add(picture)
    
    db.commit()

    return {"message": "Images uploaded successfully"}

@router.get("/clinic_images/{filename}", status_code=200)
async def display_clinic_image(filename: str):
    directory = "images/clinic_pictures"
    file_path = os.path.join(directory, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)

@router.delete("/clinic_picture/{id}")
async def delete_profile_picture(user: user_dependency,db: db_dependency, id: int):
    picture_model = db.query(ClinicPictures).filter(ClinicPictures.id == id).first()

    if picture_model is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    db.delete(picture_model)
    db.commit()

    return {"message": "Image deleted successfully"}