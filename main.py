from fastapi import FastAPI
from routers import auth, users, admin
from database import engine, Base

# Create an instance of FastAPI
app = FastAPI()

# Ensure all tables are created
Base.metadata.create_all(bind=engine)

# Include the authentication router
app.include_router(auth.router)

#Include the Users router
app.include_router(users.router)

#Include the admin's router
app.include_router(admin.router)