from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from pydantic import EmailStr, constr


#Authentication
class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern="^[A-Za-z0-9@#$%^&+=]*$")
    full_name: constr(min_length=5, max_length=255)
    gender: Optional[str] =  'male'

    # if join existing org
    organization_id: Optional[UUID] = None  

    # if create new org
    organization_name: Optional[str] = None
    organization_desc: Optional[str] = None


class TokenOut(BaseModel):
    message: Optional[str] = "Success"
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class RefreshIn(BaseModel):
    refresh_token: str

#User
class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    class Config:
        orm_mode = True

#organization
class OrganizationOut(BaseModel):
    id: UUID
    name: str
    description: str
    class Config:
        orm_mode = True

class OrganizationUpdate(BaseModel):
    name: str
    description: str
    class Config:
        orm_mode = True

class UserCreateByAdmin(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern="^[A-Za-z0-9@#$%^&+=]*$")
    full_name: constr(min_length=5, max_length=255)
    gender: Optional[str] = 'male'
    role: Optional[str] = "member"  


#project
class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: str
    members: List[UserOut]

    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None 

class ProjectMemberIn(BaseModel):
    user_id: int

class ProjectMemberOut(BaseModel):
    id: int
    user_id: int
    project_id: int

    class Config:
        orm_mode = True

  
