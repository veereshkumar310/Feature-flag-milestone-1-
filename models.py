from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, index=True)
    flag_name = Column(String, unique=True, nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)