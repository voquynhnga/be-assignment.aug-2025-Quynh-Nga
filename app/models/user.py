from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import BaseModel

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

class Organization(BaseModel):
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    hash_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    gender = Column(Boolean, default=True, nullable=False)  # True for male
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign Keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    comments = relationship("TaskComment", back_populates="user")
    attachments = relationship("TaskAttachment", back_populates="uploaded_by_user")
    notifications = relationship("Notification", back_populates="user")
    
    def __str__(self):
        return f"<User: {self.email}>"