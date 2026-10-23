from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import text
from pydantic import BaseModel
from pwdlib import PasswordHash
from database import (
    engine,
    Base,
    SessionLocal,
)
import models 

app = FastAPI(title="Feature Flag Management System")
password_hash = PasswordHash.recommended()


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/", include_in_schema=False)
def home():
    file_path = Path(__file__).parent / "index.html"
    return FileResponse(file_path)

Base.metadata.create_all(bind=engine)

# Temporary in-memory storage for feature flags
# We will connect flag storage to PostgreSQL next.
flags = {} 
@app.post("/register")
def register_user(user: RegisterRequest):
    username = user.username.strip()

    if not username or not user.password:
        raise HTTPException(
            status_code=400,
            detail="Username and password are required"
        )

    if len(user.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )

    db = SessionLocal()
    try:
        existing_user = db.query(models.User).filter(
            models.User.username == username
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            )

        new_user = models.User(
            username=username,
            password_hash=password_hash.hash(user.password)
        )

        db.add(new_user)
        db.commit()

        return {"message": "Account created successfully"}
    finally:
        db.close()
@app.post("/login")
def login_user(user: LoginRequest):
    username = user.username.strip()

    db = SessionLocal()
    try:
        existing_user = db.query(models.User).filter(
            models.User.username == username
        ).first()

        if existing_user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        if not password_hash.verify(
            user.password,
            existing_user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        return {
            "message": "Login successful",
            "username": existing_user.username
        }
    finally:
        db.close()




@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

@app.post("/flags/{flag_name}")
def create_feature_flag(flag_name: str, enabled: bool = True):
    db = SessionLocal()
    try:
        existing_flag = db.query(models.FeatureFlag).filter(
            models.FeatureFlag.flag_name == flag_name
        ).first()

        if existing_flag:
            raise HTTPException(
                status_code=409,
                detail="Feature flag already exists"
            )

        new_flag = models.FeatureFlag(
            flag_name=flag_name,
            enabled=enabled
        )

        db.add(new_flag)
        db.commit()
        db.refresh(new_flag)

        return {
            "message": "Feature flag created successfully",
            "flag_name": new_flag.flag_name,
            "enabled": new_flag.enabled
        }
    finally:
        db.close()


@app.get("/flags/{flag_name}")
def get_feature_flag(flag_name: str):
    db = SessionLocal()
    try:
        flag = db.query(models.FeatureFlag).filter(
            models.FeatureFlag.flag_name == flag_name
        ).first()

        if flag is None:
            raise HTTPException(
                status_code=404,
                detail="Feature flag not found"
            )

        return {
            "flag_name": flag.flag_name,
            "enabled": flag.enabled
        }
    finally:
        db.close()

@app.put("/flags/{flag_name}")
def update_feature_flag(flag_name: str, enabled: bool):
    db = SessionLocal()
    try:
        flag = db.query(models.FeatureFlag).filter(
            models.FeatureFlag.flag_name == flag_name
        ).first()

        if flag is None:
            raise HTTPException(
                status_code=404,
                detail="Feature flag not found"
            )

        flag.enabled = enabled
        db.commit()
        db.refresh(flag)

        return {
            "message": "Feature flag updated successfully",
            "flag_name": flag.flag_name,
            "enabled": flag.enabled
        }
    finally:
        db.close()
@app.get("/flags")
def list_feature_flags():
    db = SessionLocal()
    try:
        flags = db.query(models.FeatureFlag).all()

        return {
            "flags": [
                {
                    "flag_name": flag.flag_name,
                    "enabled": flag.enabled
                }
                for flag in flags
            ]
        }
    finally:
        db.close()
