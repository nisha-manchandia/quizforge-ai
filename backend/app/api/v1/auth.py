from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.core.security import decode_access_token
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    MessageResponse
)
from app.services.auth_service import (
    register_user,
    login_user,
    get_user_by_id
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Use HTTPBearer — this gives Swagger a simple Value field
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency — extracts and validates JWT token.
    Use this in any route that requires authentication.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return get_user_by_id(db, user_id)


# ─── Routes ───────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user account."""
    return register_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and receive JWT access token."""
    result = login_user(db, credentials.email, credentials.password)
    return {
        "access_token": result["access_token"],
        "token_type": "bearer",
        "user": result["user"]
    }


@router.get(
    "/me",
    response_model=UserResponse
)
async def get_my_profile(
    current_user=Depends(get_current_user)
):
    """Get current authenticated user's profile."""
    return current_user