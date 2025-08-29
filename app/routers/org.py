from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models import Organization
from app.schemas import OrganizationOut
from database import get_db

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)

@router.get("/", response_model=List[OrganizationOut])
def get_all_organizations(db: Session = Depends(get_db)):
    organizations = db.query(Organization).all()
    return organizations