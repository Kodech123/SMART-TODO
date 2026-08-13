import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# passlib's bcrypt wrapper is unmaintained and breaks against bcrypt>=4.1 (its version
# self-detection crashes), so this calls the bcrypt library directly instead.


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int, expires_minutes: int | None = None) -> str:
    expire_delta = timedelta(minutes=expires_minutes or settings.jwt_expire_minutes)
    expire_at = datetime.now(timezone.utc) + expire_delta
    payload = {"sub": str(user_id), "exp": expire_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


class InvalidTokenError(Exception):
    pass


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    subject = payload.get("sub")
    if subject is None:
        raise InvalidTokenError("Token missing subject")
    return int(subject)


def sign_reminder_open_token(reminder_id: int) -> str:
    """A service worker can't carry the user's JWT (no access to localStorage from that
    context), but the "reminder opened" signal is a low-sensitivity analytics timestamp,
    not something worth a full auth round trip. This HMAC just stops arbitrary reminder
    IDs from being marked opened by anyone who guesses one -- it's delivered to the
    client inside the push notification payload itself, alongside the reminder_id.
    """
    digest = hmac.new(settings.jwt_secret_key.encode("utf-8"), str(reminder_id).encode("utf-8"), hashlib.sha256)
    return digest.hexdigest()


def verify_reminder_open_token(reminder_id: int, token: str) -> bool:
    expected = sign_reminder_open_token(reminder_id)
    return hmac.compare_digest(expected, token)
