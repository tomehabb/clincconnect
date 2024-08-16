from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship

# Define the Users model, which maps to the 'users' table in the database
class Users(Base):
    __tablename__ = 'users'

    # Define the columns in the 'users' table
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    # Add user's profile picture later
    hashed_password = Column(String)
    email = Column(String, unique=True)
    mobile_number = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    role = Column(String)

    # Establish a relationship with the Todos model
    clinics = relationship("Clinics", back_populates="owner")


#Define the Clinics model, which maps to the 'maps' table in the database

class Clinics(Base):
    __tablename__ = 'clinics'

    # Define the columns in the 'clinic' table
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    address = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String)
    reviews = Column(Float, default="0")

    # Owner's details
    owner = relationship("Users", back_populates="clinics")
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner_name = Column(String)
    owner_contact = Column(String)

    # Operational Details
    operating_hours = Column(String)
    no_of_shifts = Column(Integer)
    clinic_speciality = Column(String)

    # Regulatory and Compliance
    registration_date = Column(String)
    
    # Other featurs
    is_active = Column(Boolean, default=True)
    clinic_sub_speciality = Column(String)
    staff_type = Column(Integer)

    # Clinic pictures (Add later)


    



