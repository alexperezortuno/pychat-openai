#!/usr/bin/env python
import os
from typing import Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ai.core.commons import log_lvl, log_str
from ai.core.logger import get_logger
from web.storage.entity.user_entity import UserEntity
from web.storage.model.token import TokenData
from web.storage.model.user_model import UserModelInDB, UserModel
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("SECRET_KEY", b"bae9543379d8475aa52bd5898fa5a737899a7c5bb4a9b09beec45190e615603d")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCES_TOKEN_EXPIRE_MINUTES", 30)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = get_logger(log_lvl, log_str, __name__)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def get_user(db: Session, username: str) -> UserModel or None:
    try:
        user = db.query(UserEntity).filter(UserEntity.username == username).first()
        logger.debug(f"get_user: {user}")
        if not user:
            return None
        return user
    except Exception as ex:
        logger.error(f"get_user: {ex}")
        return None


def authenticate_user(db: Session, username: str, password: str, grant_type: str) -> UserModelInDB or bool:
    if grant_type != "password":
        return False

    try:
        user = get_user(db, username)
        logger.debug(f"authenticate_user: {user}")
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user
    except Exception as ex:
        logger.error(f"authenticate_user: {ex}")
        return False


def create_access_token(data: Dict, expires_delta: timedelta or None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(db: Session, token: str = Depends(oauth2_scheme)) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"payload: {payload}")
        username: str = payload.get("sub")
        logger.debug(f"username: {username}")
        if username is None:
            return False
        token_data = TokenData(username=username)
        user = get_user(db, username=token_data.username)
        if user is None:
            return False
        return True
    except JWTError:
        logger.error(f"JWTError: {JWTError}")
        return False
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return False


async def get_current_user(db: Session, token: str) -> UserModel or None:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"Authorization": "Bearer"})
    try:
        payload = decode_token(token)
        logger.debug(f"payload: {payload}")
        username: str = payload.get("sub")
        logger.debug(f"username: {username}")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = get_user(db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        logger.error(f"JWTError: {JWTError}")
        raise credentials_exception
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        raise credentials_exception


def decode_token(token: str) -> dict or None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"payload: {payload}")
        return payload
    except JWTError:
        logger.error(f"JWTError: {JWTError}")
        return None
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return None


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel or None:
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def create_user(db: Session, user: UserModel) -> UserEntity:
    db_user = UserEntity(username=user.username,
                         email=user.email,
                         password=get_password_hash(user.password),
                         full_name=user.full_name,
                         disabled=user.disabled)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def exists_user(db: Session, username: str) -> bool:
    return db.query(UserEntity).filter(UserEntity.username == username).first() is not None
