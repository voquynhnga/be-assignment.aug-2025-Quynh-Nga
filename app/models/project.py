from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from .base import BaseModel

# Association table for many-to-many relationship
project_members = Table(
    'project_members',
    BaseModel.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class Project(BaseModel):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Foreign Keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    members = relationship("User", secondary=project_members, backref="projects")
    
    def __str__(self):
        return f"<Project: {self.name}>"