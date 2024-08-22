import base64
from fastapi import APIRouter, Depends, Form, Path, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import List, Annotated

from database import SessionLocal, Base
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

def add_clinic_form(
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    province: str = Form(...),
    country: str = Form(...),
    owner_contact: str = Form(...),
    operating_hours: str = Form(...),
    no_of_shifts: int = Form(...),
    clinic_speciality: str = Form(...),
    clinic_sub_speciality: str = Form(...),
    staff_type: str = Form(...)
) -> ClinicRequest:
    return ClinicRequest(
        title=title, 
        description=description,
        address=address,
        city=city,
        province=province,
        country=country,
        owner_contact=owner_contact,
        operating_hours=operating_hours,
        no_of_shifts=no_of_shifts,
        clinic_speciality=clinic_speciality,
        clinic_sub_speciality=clinic_sub_speciality,
        staff_type=staff_type
    )

router = APIRouter(prefix="/clinics", tags=['clinics'])

@router.get("/all_clinic_info", status_code=status.HTTP_200_OK)
async def get_clinic_info(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Unauthorised")
    
    clinics_details = db.query(Clinics).filter(Clinics.owner_id == user.get("id")).all()
    for clinic in clinics_details:
        clinic.pictures  # Load related pictures if needed
    return clinics_details

@router.post("/add_clinic", status_code=status.HTTP_200_OK)
async def add_clinic(
    db: db_dependency,
    user: user_dependency,
    clinic_request: ClinicRequest = Depends(add_clinic_form),
    clinics_pictures: list[UploadFile] = File(...)
):
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
    
    # Add pictures to the clinic
    for image in clinics_pictures:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="The uploaded file is not an image")
        
        image_data = await image.read()
        base64_encoded_data = base64.b64encode(image_data)
        base64_string = base64_encoded_data.decode('utf-8')
        
        picture = ClinicPictures(
            image_url=base64_string,  # Storing base64 string in image_url field
            clinic_id=clinic_model.id
        )
        db.add(picture)
    
    db.commit()
    return {"status": "Clinic and pictures added successfully"}


@router.get("/get_clinic_by_id/{clinic_id}", status_code=status.HTTP_200_OK)
async def get_clinic_by_id(user: user_dependency, db: db_dependency, clinic_id: int = Path(gt=0)):
    clinic_model = db.query(Clinics).filter(Clinics.id == clinic_id).first()
    if clinic_model is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic_model

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
