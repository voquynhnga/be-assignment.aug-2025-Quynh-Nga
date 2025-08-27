from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum, Text
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel

class NotificationType(str, enum.Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_COMMENT_ADDED = "task_comment_added"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"

class Notification(BaseModel):
    __tablename__ = "notifications"
    
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    task = relationship("Task", back_populates="notifications")
    
    def __str__(self):
        return f"<Notification: {self.title}>"