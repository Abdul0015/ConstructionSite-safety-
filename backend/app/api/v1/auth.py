import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    revoke_refresh_token,
    is_token_revoked
)
from app.core.rate_limiter import limiter
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token, RefreshTokenRequest, LoginRequest

router = APIRouter()

@router.post("/login", response_model=Token, summary="User Login (Rate-Limited: 5 attempts/min)")
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password and issue JWT access and refresh tokens.
    Rate limited to 5 attempts per minute per IP address.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token, summary="Refresh Access Token (Strict Rotation)")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Issue a new access token and refresh token using a valid refresh token.
    Enforces strict refresh token rotation: old refresh token is invalidated on use.
    """
    try:
        payload = decode_token(request.refresh_token)
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")

        if not user_id_str or token_type != "refresh" or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        # Check if refresh token was already used/revoked
        if is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has already been used and revoked. Please log in again."
            )

        user_id = uuid.UUID(user_id_str)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )

    # Immediately invalidate the used refresh token JTI (strict rotation)
    revoke_refresh_token(jti)

    # Generate new pair of tokens with new unique JTIs
    new_access_token = create_access_token(subject=user.id, role=user.role.value)
    new_refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse, summary="Get Current Authenticated User Profile")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get profile information of the currently authenticated user.
    """
    return current_user

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create User Account (Admin Only)")
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Create a new user account (Admin restricted). Workers and Supervisors are added by Admins.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/test-protected", summary="Test Protected Route (Admin Only)")
def test_protected_route(admin_user: User = Depends(require_role(UserRole.ADMIN))):
    """
    Test endpoint verifying role-based access control (Admin required).
    """
    return {
        "message": "Access granted to admin-only protected route",
        "admin_email": admin_user.email,
        "role": admin_user.role.value
    }
