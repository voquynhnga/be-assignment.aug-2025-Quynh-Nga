from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
import enum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    hash_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    gender = Column(
    Enum(Gender, name="gender", values_callable=lambda obj: [e.value for e in obj]),
    default=Gender.MALE.value,
    nullable=False,
    )
    role = Column(
    Enum(UserRole, name="userrole", values_callable=lambda obj: [e.value for e in obj]),
    default=UserRole.MEMBER.value,
    nullable=False,
    )

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

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    token = Column(Text, nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    
    def __str__(self):
        return f"<User: {self.email}>"