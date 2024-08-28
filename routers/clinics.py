import base64
from fastapi import APIRouter, Depends, Form, Path, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Annotated

from database import SessionLocal
from routers.auth import get_current_user
from models import Clinics, ClinicPictures

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class ClinicRequest(BaseModel):
    title: str
    description: str
    address: str
    city: str
    province: str
    country: str
    owner_contact: str
    operating_hours: str
    no_of_shifts: int
    clinic_speciality: str
    clinic_sub_speciality: str
    staff_type: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Clinic title",
                "description": "Clinic's Description.",
                "address": "Clinic's Address",
                "city": "Clinic's city",
                "province": "Clinic's Province",
                "country": "Clinic's country",
                "owner_contact": "Clinic's contact",
                "operating_hours": "Clinic's operating hours",
                "no_of_shifts": 5,
                "clinic_speciality": "Clinic's speciality",
                "clinic_sub_speciality": "Clinic's sub speciality",
                "staff_type": "Clinic's staff type",
            }
        }
    }


router = APIRouter(prefix="/clinics", tags=['clinics'])

@router.get("/all_clinic_info", status_code=status.HTTP_200_OK)
async def get_clinic_info(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Unauthorized")
    
    clinic_details = {}
    
    clinic_models = db.query(Clinics).all()
    for n, clinic in enumerate(clinic_models, start=1):
        clinic_urls = [f"http://127.0.0.1:8000/picture/clinic_images/{image.image_url}" for image in db.query(ClinicPictures).filter(ClinicPictures.clinic_id == clinic.id).all()]
        clinic_details[f"clinic_{n}"] = {"clinic": clinic, "images": clinic_urls}
    
    return clinic_details



@router.post("/add_clinic", status_code=status.HTTP_200_OK)
async def add_clinic(
    db: db_dependency,
    user: user_dependency,
    clinic_request: ClinicRequest):

    # Create a new clinic entry
    clinic_model = Clinics(
        title=clinic_request.title,
        description=clinic_request.description,
        address=clinic_request.address,
        city=clinic_request.city,
        province=clinic_request.province,
        country=clinic_request.country,
        owner_contact=clinic_request.owner_contact,
        operating_hours=clinic_request.operating_hours,
        no_of_shifts=clinic_request.no_of_shifts,
        clinic_speciality=clinic_request.clinic_speciality,
        clinic_sub_speciality=clinic_request.clinic_sub_speciality,
        staff_type=clinic_request.staff_type,
        owner_id=user.get("id"),
        owner_name=user.get("full_name"),
        registration_date=str(datetime.now())
    )
    db.add(clinic_model)
    db.commit()
    db.refresh(clinic_model)
    
    
    
    db.commit()
    return {"status": "Clinic and pictures added successfully"}


@router.get("/get_clinic_by_id/{clinic_id}", status_code=status.HTTP_200_OK)
async def get_clinic_by_id(user: user_dependency, db: db_dependency, clinic_id: int = Path(gt=0)):
    clinic_model = db.query(Clinics).filter(Clinics.id == clinic_id).first()
    if clinic_model is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    clinic_pictures = db.query(ClinicPictures).filter(ClinicPictures.clinic_id == clinic_model.id).all()
    clinic_urls = [f"http://127.0.0.1:8000/picture/clinic_images/{image.image_url}" for image in clinic_pictures]
    
    return {
        "clinic": clinic_model,
        "images": clinic_urls
    }


@router.put("/update_clinic_information/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_clinic(user: user_dependency, db: db_dependency, clinic_request: ClinicRequest, clinic_id: int = Path(gt=0)):
    clinic_model = db.query(Clinics).filter(Clinics.id == clinic_id).first()
    if clinic_model is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    if clinic_model.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised User")

    clinic_model.title = clinic_request.title
    clinic_model.description = clinic_request.description
    clinic_model.address = clinic_request.address
    clinic_model.city = clinic_request.city
    clinic_model.province = clinic_request.province
    clinic_model.country = clinic_request.country
    clinic_model.owner_contact = clinic_request.owner_contact
    clinic_model.operating_hours = clinic_request.operating_hours
    clinic_model.no_of_shifts = clinic_request.no_of_shifts
    clinic_model.clinic_speciality = clinic_request.clinic_speciality
    clinic_model.clinic_sub_speciality = clinic_request.clinic_sub_speciality
    clinic_model.staff_type = clinic_request.staff_type
    db.add(clinic_model)
    db.commit()

@router.delete("/delete/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clinic(user: user_dependency, db: db_dependency, clinic_id: int = Path(gt=0)):
    clinic_model = db.query(Clinics).filter(Clinics.id == clinic_id).first()
    if clinic_model is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    if clinic_model.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised User")
    
    db.delete(clinic_model)
    db.commit()
