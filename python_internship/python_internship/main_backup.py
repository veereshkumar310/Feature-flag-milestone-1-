from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash

from database import engine, Base, SessionLocal
from models import FeatureFlag, User

app = FastAPI(title="Feature Flag Management System")

password_hash = PasswordHash.recommended()

# Request models
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Create database tables
Base.metadata.create_all(bind=engine)


# Home page
@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "index.html")


# Dashboard page
@app.get("/dashboard")
def dashboard():
    return FileResponse(Path(__file__).parent / "dashboard.html")


# Health check
@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }


# Register user
@app.post("/register")
def register_user(user_data: UserCreate):
    db: Session = SessionLocal()

    try:
        existing_user = db.query(User).filter(
            User.email == str(user_data.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Email is already registered"
            )

        new_user = User(
            email=str(user_data.email),
            hashed_password=password_hash.hash(user_data.password)
        )

        db.add(new_user)
        db.commit()

        return {
            "message": "Account created successfully"
        }

    finally:
        db.close()


# Login user
@app.post("/login")
def login_user(user_data: UserLogin):
    db: Session = SessionLocal()

    try:
        user = db.query(User).filter(
            User.email == str(user_data.email)
        ).first()

        if not user or not password_hash.verify(
            user_data.password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        return {
            "message": "Login successful",
            "redirect": "/dashboard"
        }

    finally:
        db.close()


# Create feature flag
@app.post("/flags")
def create_flag(flag_name: str):
    db: Session = SessionLocal()

    try:
        existing_flag = db.query(FeatureFlag).filter(
            FeatureFlag.flag_name == flag_name
        ).first()

        if existing_flag:
            raise HTTPException(
                status_code=409,
                detail="Feature flag already exists"
            )

        new_flag = FeatureFlag(
            flag_name=flag_name,
            enabled=True
        )

        db.add(new_flag)
        db.commit()
        db.refresh(new_flag)

        return {
            "id": new_flag.id,
            "flag_name": new_flag.flag_name,
            "enabled": new_flag.enabled
        }

    finally:
        db.close()


# Get all feature flags
@app.get("/flags")
def get_flags():
    db: Session = SessionLocal()

    try:
        flags = db.query(FeatureFlag).all()

        return [
            {
                "id": flag.id,
                "flag_name": flag.flag_name,
                "enabled": flag.enabled
            }
            for flag in flags
        ]

    finally:
        db.close()


# Enable or disable a feature flag
@app.put("/flags/{flag_id}")
def update_flag(flag_id: int, enabled: bool):
    db: Session = SessionLocal()

    try:
        flag = db.query(FeatureFlag).filter(
            FeatureFlag.id == flag_id
        ).first()

        if not flag:
            raise HTTPException(
                status_code=404,
                detail="Feature flag not found"
            )

        flag.enabled = enabled
        db.commit()
        db.refresh(flag)

        return {
            "id": flag.id,
            "flag_name": flag.flag_name,
            "enabled": flag.enabled
        }

    finally:
        db.close()