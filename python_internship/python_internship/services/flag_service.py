from sqlalchemy.orm import Session
from fastapi import HTTPException

from models import FeatureFlag


def create_flag(db: Session, flag_name: str):
    existing_flag = (
        db.query(FeatureFlag)
        .filter(FeatureFlag.flag_name == flag_name)
        .first()
    )

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

    return new_flag


def get_all_flags(db: Session):
    return db.query(FeatureFlag).all()


def update_flag(db: Session, flag_id: int, enabled: bool):
    flag = (
        db.query(FeatureFlag)
        .filter(FeatureFlag.id == flag_id)
        .first()
    )

    if not flag:
        raise HTTPException(
            status_code=404,
            detail="Feature flag not found"
        )

    flag.enabled = enabled
    db.commit()
    db.refresh(flag)

    return flag