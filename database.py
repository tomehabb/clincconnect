from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define the database URL for SQLite
SQLALCHEMY_DATABASE_URL = 'sqlite:///./clinicconnect.db'

# Create an engine instance with the database URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class that our models will inherit
Base = declarative_base()
