from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
import enum

from sqlalchemy.orm import relationship

from .base import BaseModel

class Organization(BaseModel):
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")