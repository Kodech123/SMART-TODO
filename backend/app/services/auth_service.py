from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.category import DEFAULT_CATEGORIES, Category
from app.models.user import User


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(db: Session, email: str, password: str, display_name: str) -> tuple[User, str]:
    existing = db.query(User).filter(User.email == email).first()
    if existing is not None:
        raise EmailAlreadyRegisteredError(email)

    user = User(email=email, password_hash=hash_password(password), display_name=display_name)
    db.add(user)
    db.flush()  # assign user.user_id before creating dependent rows

    for defaults in DEFAULT_CATEGORIES:
        db.add(Category(user_id=user.user_id, is_default=True, **defaults))

    db.commit()
    db.refresh(user)

    token = create_access_token(user.user_id)
    return user, token


def authenticate_user(db: Session, email: str, password: str) -> tuple[User, str]:
    user = db.query(User).filter(User.email == email, User.is_deleted.is_(False)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()

    token = create_access_token(user.user_id)
    return user, token
