#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

# Auth utils modules providing functions used for authentication
# As in the documentation : https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status

from src.api.db.user_db import UserDB
from src.api.models import TokenData, User, UserIn
from src.api.routers import config, ROUTE_PREFIX

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = UserDB(config['database'])

SECRET_KEY = str(os.urandom(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=ROUTE_PREFIX+"/token")


def verify_password(plain_password, hashed_password):
    """
    Verify a password against a hash using the pwd_context
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Get the hash of a password using the pwd_context
    """
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    """
    Authenticate a user using username and password
    """
    user = db.get_user_by_username(username)
    user = db.get_user_by_email(username) if user is None else user
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create an access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Get the current active user
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Get the current admin user
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not admin user")
    return current_user


def create_user(user: UserIn):
    """
    Create a user
    """
    user.hashed_password = get_password_hash(user.password)
    db.add_user(user)
