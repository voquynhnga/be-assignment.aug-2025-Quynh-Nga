from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import User, RefreshToken, Organization
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.schemas import TokenOut, RegisterIn, LoginIn, RefreshIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    #Ensure email is unique
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    #Join existing organization or create a new one
    if payload.organization_id:
        organization = (
            db.query(Organization)
            .filter(Organization.id == payload.organization_id)
            .first()
        )
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        role = "member"
    else:
        if not payload.organization_name:
            raise HTTPException(
                status_code=400,
                detail="organization_name is required when organization_id is not provided",
            )
        new_org = Organization(
            name=payload.organization_name, description=payload.organization_desc
        )
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        organization = new_org
        role = "admin"

    #Create user
    user = User(
        email=payload.email,
        hash_password=hash_password(payload.password),
        full_name=payload.full_name,
        gender=payload.gender,
        role=role,
        is_active=True,
        organization_id=organization.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    #Issue tokens and persist refresh token
    now_utc = datetime.now(timezone.utc)
    access = create_access_token(subject=str(user.id), data={"role": user.role})
    refresh = create_refresh_token(subject=str(user.id))
    expires_at = now_utc + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at)
    db.add(db_token)
    db.commit()

    return TokenOut(
        message="Register successfully",
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
    )


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is deactivated"
        )

    # Enforce single-session: revoke all previous refresh tokens for this user
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db.commit()

    # Issue tokens
    now_utc = datetime.now(timezone.utc)
    access = create_access_token(subject=str(user.id), data={"role": user.role})
    refresh = create_refresh_token(subject=str(user.id))
    expires_at = now_utc + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(token=refresh, user_id=user.id, expires_at=expires_at)
    db.add(db_token)
    db.commit()

    return TokenOut(
        message="Login successfully",
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenOut)
def refresh_token(payload: RefreshIn, db: Session = Depends(get_db)):
    from app.core.security import decode_token

    # Decode token and validate type
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token"
        )

    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    #Check refresh token existence and expiration
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == payload.refresh_token)
        .first()
    )
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked"
        )

    now_utc = datetime.now(timezone.utc)
    if db_token.expires_at is None or db_token.expires_at < now_utc:
        db.delete(db_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    #Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.delete(db_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    if not user.is_active:
        db.delete(db_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is deactivated"
        )

    #Rotate refresh token
    db.delete(db_token)
    db.commit()

    new_refresh = create_refresh_token(subject=str(user.id))
    new_expires_at = now_utc + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(token=new_refresh, user_id=user.id, expires_at=new_expires_at))
    db.commit()

    #Issue new access token
    access = create_access_token(subject=str(user.id), data={"role": user.role})

    return TokenOut(
        message="Token refreshed successfully",
        access_token=access,
        refresh_token=new_refresh,
        token_type="bearer",
    )


@router.post("/logout", response_model=dict)
def logout(payload: RefreshIn, db: Session = Depends(get_db)):
    # Revoke given refresh token (idempotent)
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == payload.refresh_token)
        .first()
    )
    if db_token:
        db.delete(db_token)
        db.commit()
    return {"ok": True, "message": "Logged out successfully"}
