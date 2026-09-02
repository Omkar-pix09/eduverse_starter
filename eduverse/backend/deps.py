from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import JWTError

import models
from database import get_db
from auth import decode_access_token


def get_current_user(
    authorization: str = Header(...), db: Session = Depends(get_db)
) -> models.User:
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
