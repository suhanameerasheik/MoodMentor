import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "60")
)

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET is not configured. "
        "Create a .env file before starting the backend."
    )


DEMO_USERS = {
    "user_001": {
        "username": "user_001",
        "password": os.getenv("USER_001_PASSWORD"),
    },
    "user_002": {
        "username": "user_002",
        "password": os.getenv("USER_002_PASSWORD"),
    },
    "user_003": {
        "username": "user_003",
        "password": os.getenv("USER_003_PASSWORD"),
    },
}


def authenticate_user(
    username: str,
    password: str
):
    user = DEMO_USERS.get(username)

    if not user:
        return None

    if not user["password"]:
        return None

    if user["password"] != password:
        return None

    return {
        "user_id": user["username"]
    }


def create_access_token(user_id: str):
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=JWT_EXPIRE_MINUTES)
    )

    payload = {
        "sub": user_id,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            return None

        if user_id not in DEMO_USERS:
            return None

        return {
            "user_id": user_id
        }

    except jwt.PyJWTError:
        return None
