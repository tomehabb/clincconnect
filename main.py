from fastapi import FastAPI
from routers import auth
from database import engine, Base

# Create an instance of FastAPI
app = FastAPI()

# Ensure all tables are created
Base.metadata.create_all(bind=engine)

# Include the authentication router
app.include_router(auth.router)
