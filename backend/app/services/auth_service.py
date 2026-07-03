from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import UserRegister
from app.core.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from app.config import settings


def register_user(db: Session, user_data: UserRegister) -> User:
    """
    Register a new user.
    Raises 409 if email already exists.
    """
    # Check if email already taken
    existing = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_guest=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(db: Session, email: str, password: str) -> dict:
    """
    Authenticate user and return JWT token.
    Raises 401 if credentials are invalid.
    """
    # Find user by email
    user = db.query(User).filter(User.email == email).first()

    # Generic error — don't reveal whether email exists
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        },
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    return {"access_token": access_token, "user": user}


def get_user_by_id(db: Session, user_id: str) -> User:
    """Fetch a user by their ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user