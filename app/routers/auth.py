from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
import re

from app.dependencies import get_db
from app.models import User, RefreshToken, Organization
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.security import REFRESH_TOKEN_EXPIRE_DAYS
from uuid import UUID


router = APIRouter(prefix="/auth", tags=["auth"])

class OrganizationOut(BaseModel):
    id: UUID
    name: str



class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=32, pattern="^[A-Za-z0-9@#$%^&+=]*$")
    full_name: constr(min_length=5, max_length=255)
    gender: Optional[str] = 'male' 
    organization_id: Optional[UUID]



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

@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    # check if email already exists
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    #check organization exists
    organization = db.query(Organization).filter(Organization.id == payload.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id: {payload.organization_id} not found."
        )
    user = User(
        email=payload.email,
        hash_password=hash_password(payload.password),
        full_name=payload.full_name,
        gender=payload.gender,
        role='member',
        is_active=True,
        organization_id=payload.organization_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # create tokens to not require login after register
    access = create_access_token(subject=str(user.id), data={"role": user.role})
    refresh = create_refresh_token(subject=str(user.id))
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at)
    db.add(db_token)
    db.commit()


    return TokenOut(
        message="Register successfully",
        access_token=access, 
        refresh_token=refresh,
        token_type="bearer")

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(subject=str(user.id), data={"role": user.role})
    refresh = create_refresh_token(subject=str(user.id))

    # store refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at)
    db.add(db_token)
    db.commit()

    return TokenOut(
        message="Login successfully",
        access_token=access, 
        refresh_token=refresh,
        token_type="bearer")



@router.post("/refresh", response_model=TokenOut)
def refresh_token(payload: RefreshIn, db: Session = Depends(get_db)):
    from app.core.security import decode_token
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token")

    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # check refresh token exists and not expired
    db_token = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Optionally: revoke current refresh token and issue new one (rotate)
    db.delete(db_token)
    db.commit()

    new_refresh = create_refresh_token(subject=str(user.id))
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(token=new_refresh, user_id=user.id, expires_at=expires_at))
    db.commit()

    access = create_access_token(subject=str(user.id), data={"role": user.role})
    return TokenOut(access_token=access, refresh_token=new_refresh)

@router.post("/logout", response_model=dict)
def logout(payload: RefreshIn, db: Session = Depends(get_db)):
    # revoke refresh token
    db_token = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if db_token:
        db.delete(db_token)
        db.commit()
    return {"ok": True}

