from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional, Literal
from pydantic import EmailStr, constr
from datetime import datetime



#Authentication
class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern=r"^[A-Za-z0-9@#$%^&+=*]{6,32}$")
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
    password: constr(min_length=6, max_length=32, pattern=r"^[A-Za-z0-9@#$%^&+=*]{6,32}$")

class RefreshIn(BaseModel):
    refresh_token: str



#User
class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: Literal['member','manager','admin']  
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[Literal['male','female']] = None
    password: Optional[constr(min_length=6, max_length=32, pattern=r"^[A-Za-z0-9@#$%^&+=*]{6,32}$")]=None
    organization_id: Optional[UUID] = None 

class UserCreateByAdmin(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern=r"^[A-Za-z0-9@#$%^&+=*]{6,32}$")
    full_name: constr(min_length=5, max_length=255)
    gender: Literal['male','female']
    role: Literal['member','manager','admin']  

#organization
class OrganizationOut(BaseModel):
    name: str
    description: Optional[str] = None
    class Config:
        orm_mode = True

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None  
    description: Optional[str] = None


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

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
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
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["todo", "in_progress", "done"]] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[UUID] = None

class TaskOut(TaskBase):
    status: Literal["todo", "in_progress", "done"]
    assignee_id: UUID
    class Config:
        orm_mode = True


#notification
class NotificationOut(BaseModel):
    id: UUID
    type: Literal['task_assigned','task_status_changed','task_comment_added','task_due_soon','task_overdue']
    title: str
    message: str
    is_read: Literal[False, True]
    user_id:  UUID
    task_id:  UUID
    created_at: datetime
    
    class Config:
        orm_mode = True


  
