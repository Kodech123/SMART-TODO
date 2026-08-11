from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserSettingsResponse, UserSettingsUpdate

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.get("/settings", response_model=UserSettingsResponse)
def get_settings(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/settings", response_model=UserSettingsResponse)
def update_settings(
    payload: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user
