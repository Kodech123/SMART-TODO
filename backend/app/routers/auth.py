from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    try:
        user, token = register_user(db, payload.email, payload.password, payload.display_name)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc

    return RegisterResponse(
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        access_token=token,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        _user, token = authenticate_user(db, payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password") from exc

    return TokenResponse(access_token=token, expires_in=settings.jwt_expire_minutes * 60)


@router.post("/logout")
def logout(_current_user: User = Depends(get_current_user)) -> dict[str, str]:
    # Stateless JWT: logout is a client-side token discard, nothing to invalidate server-side.
    return {"message": "Logged out successfully"}
