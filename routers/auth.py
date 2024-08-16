from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

# Create a new router for authentication-related routes
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

# Secret key for JWT encoding/decoding
SECRET_KEY = '6f8f57715090da2632453988d2c487635d354cecf16816386b641456c30f8e47'
ALGORITHM = 'HS256'

# Password hashing context
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Function to authenticate a user
def authenticate_user(email: str, password: str, db: Session):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
    
# Function to create a JWT access token
def create_access_token(email: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get the current user from the JWT token
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {'email': email, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

# Pydantic model for user creation request
class CreateUserRequest(BaseModel):
    full_name: str
    password: str
    email: str
    mobile_number: str
    role: str

    # Example schema for the user creation request
    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "Thomas Ehab",
                "password": "xyz1234",
                "email": "example@example.com",
                "mobile_number": "01012345678",
                "role": "user",
            }
        }
    }

# Pydantic model for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Route to create a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # Check if user exists inside the database

    user_exists = db.query(Users).filter(
    (Users.email == create_user_request.email) | 
    (Users.mobile_number == create_user_request.mobile_number)).first()

    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email address or mobile number is already registered")


    # Create a new user model with hashed password
    create_user_model = Users(
        email=create_user_request.email,
        mobile_number = create_user_request.mobile_number,
        full_name=create_user_request.full_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )

    # Add the user to the database and commit the transaction
    db.add(create_user_model)
    db.commit()

    # Optionally return the created user or a success message
    return {"message": "User created successfully"}

# Route to generate a JWT token for a user
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Authenticate the user
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    # Create an access token with a 20-minute expiration
    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=20))
    
    # Return the token
    return {'access_token': token, 'token_type': 'bearer'}
