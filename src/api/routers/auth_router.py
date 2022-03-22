#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.api import auth_utils
from src.api.auth_utils import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    get_current_active_user, get_current_admin_user
from src.api.db.user_db import UserDB
from src.api.models import Token, User, UserIn
from src.api.routers import ROUTE_PREFIX, config

router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["Users"],
                   # dependencies=[Depends(get_current_user)],
                   responses={404: {"description": "Not found"}}
                   )


@router.get('/users/')
async def get_users(current_user: User = Depends(get_current_admin_user)):
    users = auth_utils.get_all_users()
    json_users = []
    for user in users:
        json_users.append(User.from_db_item(user))

    return json_users


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/users/register/")
async def create_user(form_data: UserIn):
    user = auth_utils.create_user(form_data)
    return user


@router.put("/users/{user_id}/admin/{admin}")
async def change_admin_status(user_id: int, admin: bool, current_user: User = Depends(get_current_admin_user)):
    user = auth_utils.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.admin != admin:
        user.admin = admin
        auth_utils.update_user(user)
    return user


@router.delete('/users/{username}')
async def delete_user(username: str, current_user: User = Depends(get_current_admin_user)):
    user = auth_utils.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    auth_utils.delete_user(user)
    return user
