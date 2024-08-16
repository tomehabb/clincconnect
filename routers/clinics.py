from fastapi import APIRouter, Depends, Path, status, HTTPException
from database import SessionLocal
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from models import Clinics
from pydantic import BaseModel, Field
from datetime import datetime

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
    no_of_shifts: str
    clinic_speciality: str
    clinic_sub_speciality: str
    staff_type: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Clinic title",
                "description": "Clinic's Description.",
                "address": "Clinc's Address",
                "city": "Clinics city",
                "province": "Clinic's Province",
                "country": "Clinic's country",
                "owner_contact": "Clinic's contact",
                "operating_hours": "Clinic's operating hours",
                "no_of_shifts": "Clinic's no of shifts",
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Unauthorised")
    
    clinics_details = db.query(Clinics).filter(Clinics.owner_id == user.get("id")).all()
    return clinics_details

@router.post("/add_clinic", status_code=status.HTTP_200_OK)
async def add_clinic(db: db_dependency, user:user_dependency, clinic_request: ClinicRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Unauthorised")
    
    clinic_model = Clinics(**clinic_request.model_dump(), owner_id = user.get("id"), owner_name = user.get("full_name"), registration_date = str(datetime.now()))
    db.add(clinic_model)
    db.commit()
    db.refresh(clinic_model)
    return clinic_model

@router.get("/get_clinic_by_id/{clinic_id}", status_code=status.HTTP_200_OK)
async def get_clinic_by_id(user: user_dependency, db: db_dependency, clinic_id: int = Path(gt = 0)):
    
    clinic_model = db.query(Clinics).filter(Clinics.id == clinic_id).first()

    return clinic_model

@router.put("/update_cilinc_informaiton/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_clinic(user: user_dependency, db: db_dependency, clinic_request: ClinicRequest, clinic_id: int = Path(gt=0)):

    clinic_model = db.query(Clinics).filter(Clinics.id == clinic_id).first()
    if clinic_model.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised User")
    
    if clinic_model is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
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
    if clinic_model.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised User")
    
    if clinic_model is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    db.delete(clinic_model)
    db.commit()