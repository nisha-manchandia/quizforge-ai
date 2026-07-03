from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

# ─── Request Schemas (what client sends) ──────────────────────

class UserRegister(BaseModel):
    """Schema for registration request."""
    email: EmailStr
    password: str
    full_name: str
    role: str = "participant"

class UserLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str

# ─── Response Schemas (what server returns) ───────────────────

class UserResponse(BaseModel):
    """Safe user data to return — never includes password."""
    id: UUID
    email: Optional[str]
    full_name: str
    role: str
    is_active: bool
    is_guest: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows converting SQLAlchemy model to schema

class TokenResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str