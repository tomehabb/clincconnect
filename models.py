from database import Base
from sqlalchemy import Column, Integer, String, Boolean

# Define the Users model, which maps to the 'users' table in the database
class Users(Base):
    __tablename__ = 'users'

    # Define the columns in the 'users' table
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    email = Column(String, unique=True)
    mobile_number = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    role = Column(String)
