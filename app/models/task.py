from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid

from .base import BaseModel

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    __tablename__ = "tasks"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = Column(Date)
    
    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="task")
    
    def __str__(self):
        return f"<Task: {self.title}>"

class TaskComment(BaseModel):
    __tablename__ = "task_comments"
    
    content = Column(Text, nullable=False)
    
    # Foreign Keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")
    
    def __str__(self):
        return f"<Comment on Task {self.task_id}>"

class TaskAttachment(BaseModel):
    __tablename__ = "task_attachments"
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    content_type = Column(String(100))
    
    # Foreign Keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    upload_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploaded_by_user = relationship("User", back_populates="attachments")
    
    def __str__(self):
        return f"<Attachment: {self.original_filename}>"