from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, BLOB
from sqlalchemy.orm import relationship

# Define the Users model, which maps to the 'users' table in the database
class Users(Base):
    __tablename__ = 'users'

    # Define the columns in the 'users' table
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    gender = Column(String)
    profile_picture = relationship("ProfilePictures", back_populates="user")  # Field to store the profile picture URL or path
    hashed_password = Column(String)
    email = Column(String, unique=True)
    mobile_number = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    date_of_birth = Column(String)  # Field to store the user's date of birth
    doctor_speciality = Column(String)  # Field to store the doctor's specialty

    # Establish a relationship with the Clinics model
    clinics = relationship("Clinics", back_populates="owner")

    syndicate_id = relationship("LegalInformation", back_populates="user_id")



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
    reviews = Column(Float, default=0)

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
    
    # Other features
    is_active = Column(Boolean, default=True)
    clinic_sub_speciality = Column(String)
    staff_type = Column(String)

    # Clinic pictures (one-to-many relationship)
    pictures = relationship("ClinicPictures", back_populates="clinic")



class ClinicPictures(Base):
    __tablename__ = 'clinic_pictures'

    id = Column(Integer, primary_key=True, index=True)
    owner_clinic_id = Column(Integer, ForeignKey('clinics.id'))
    image_url = Column(String)  # Or use Base64-encoded string if storing the image data directly

    clinic = relationship("Clinics", back_populates="pictures")


class ProfilePictures(Base):
    __tablename__ = "profile_pictures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_url = Column(String)  # Store the URL or file path to the image
    user = relationship("Users", back_populates="profile_picture")


class LegalInformation(Base):
    __tablename__ = "legal_information"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(Integer, ForeignKey('users.id'))
    arabic_full_name = Column(String)
    syndicate_id = Column(String)
    syndicate_id_url = Column(String)

    user_id = relationship("Users", back_populates="syndicate_id")
