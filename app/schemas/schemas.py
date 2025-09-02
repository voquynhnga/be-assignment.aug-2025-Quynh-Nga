from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional, Literal
from pydantic import EmailStr, constr
from datetime import datetime



#Authentication
class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern="^[A-Z][a-z][0-9]@#$%^&+=*$")
    full_name: constr(min_length=5, max_length=255)
    gender: Literal['male','female']  
    # if join existing org
    organization_id: Optional[UUID] = None  

    # if create new org
    organization_name: Optional[str] = None
    organization_desc: Optional[str] = None


class TokenOut(BaseModel):
    message: str = "Success"
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class LoginIn(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern="^[A-Z][a-z][0-9]@#$%^&+=*$")

class RefreshIn(BaseModel):
    refresh_token: str

#User
class UserOut(BaseModel):
    email: EmailStr
    full_name: str
    role: Literal['member','manager','admin']  
    class Config:
        orm_mode = True

#organization
class OrganizationOut(BaseModel):
    name: str
    description: Optional[str] = None
    class Config:
        orm_mode = True

class UserCreateByAdmin(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern="^[A-Z][a-z][0-9]@#$%^&+=*$")
    full_name: constr(min_length=5, max_length=255)
    gender: Literal['male','female']
    role: Literal['member','manager','admin']  


#project
class ProjectOut(BaseModel):
    name: str
    description: Optional[str] = None
    members: List[UserOut]

    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectMemberIn(BaseModel):
    user_id: UUID

class ProjectMemberOut(BaseModel):
    user_id:  UUID
    project_id:  UUID

    class Config:
        orm_mode = True

#task
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"]
    due_date: datetime

class TaskCreate(TaskBase):
    assignee_id: UUID

class TaskUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Literal["todo", "in-progress", "done"]
    priority: Literal["low", "medium", "high"]
    due_date: datetime
    assignee_id: UUID

class TaskOut(TaskBase):
    status: Literal["todo", "in-progress", "done"]
    assignee_id: UUID


    class Config:
        orm_mode = True


#notification
class NotificationOut(BaseModel):
    type: Literal['task_assigned','task_status_changed','task_comment_added','task_due_soon','task_overdue']
    title: str
    message: str
    is_read: Literal[False, True]
    user_id:  UUID
    task_id:  UUID


  
