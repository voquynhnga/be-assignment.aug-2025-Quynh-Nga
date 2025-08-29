from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

# ... các schema khác của bạn như RegisterIn, TokenOut, LoginIn ...

# Dưới đây là schema bạn đang hỏi đến
class OrganizationOut(BaseModel):
    id: UUID
    name: str

  

class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: str



class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None 

  
