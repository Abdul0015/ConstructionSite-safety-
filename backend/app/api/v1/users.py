import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.get("", response_model=List[UserResponse], summary="List All Users (Admin Only)")
def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Retrieve list of registered users (Admin only).
    """
    return db.query(User).order_by(User.created_at.desc()).all()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create User Account (Admin Only)")
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Create a new user account (Admin only).
    Returns 409 Conflict if email already exists.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_in.email}' already exists"
        )

    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        created_at=datetime.utcnow()
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{id}/deactivate", response_model=UserResponse, summary="Deactivate User Account (Admin Only)")
def deactivate_user(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Deactivate a user account (Admin only).
    Returns 400 Bad Request if Admin attempts to deactivate their own account.
    """
    if id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot deactivate their own account"
        )

    target_user = db.query(User).filter(User.id == id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{id}' not found"
        )

    # Delete or mark inactive (soft-delete preserves audit trail)
    db.delete(target_user)
    db.commit()

    return target_user
