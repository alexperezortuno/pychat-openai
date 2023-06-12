# -*- coding: utf-8 -*-
import os
from typing import Annotated

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import timedelta

from sqlalchemy.orm import Session
from starlette.middleware.gzip import GZipMiddleware

from ai.core.commons import log_lvl, log_str
from ai.core.logger import get_logger
from web.common.response_code import ResponseCode
from web.service.auth import SECRET_KEY, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    get_current_user, create_user, exists_user, verify_token, decode_token
from web.service.message import get_chats, get_by_role_and_username, set_chat
from web.storage import connection
from web.storage.connection import SessionLocal, engine
from web.storage.entity.user_entity import UserEntity
from web.storage.model.chat_model import ChatModel
from web.storage.model.message_model import MessageModel
from web.storage.model.response_model import ResponseModel
from web.storage.model.token import Token
from web.storage.model.user_model import UserModel
from dotenv import load_dotenv

load_dotenv()

connection.Base.metadata.schema = "openai"
connection.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*lo"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)
app.secret_key = SECRET_KEY
app.mount("/static", StaticFiles(directory="web/static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory="web/templates")
logger = get_logger(log_lvl, log_str, __name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def authenticate(request: Request,
                       token: Annotated[str, Depends(oauth2_scheme)],
                       db: Session = Depends(get_db)):
    c: bool = await verify_token(db, token)
    return c


@app.get("/health/")
async def test():
    return {"message": "ok"}


@app.get("/auth/verify", response_model=ResponseModel)
async def check_token(token: Annotated[str, Depends(oauth2_scheme)],
                      db: Session = Depends(get_db)):
    logger.debug(f"verify_token: {token}")
    c: bool = await verify_token(db, token)

    if not c:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return ResponseModel(
        status=ResponseCode.VALID_CREDENTIALS.value,
        message="Token is valid",
        data={
            "valid": c
        }
    )


@app.post("/oauth/token", response_model=Token)
async def login_for_access_token(data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    logger.debug(f"form_data: {data}")
    user = authenticate_user(db,
                             data.username,
                             data.password,
                             data.grant_type)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"Authorization": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=ResponseModel)
async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)],
                        db: Session = Depends(get_db)):
    current_user: UserModel = await get_current_user(db, token)
    if current_user:
        return ResponseModel(
            status=ResponseCode.SUCCESS.value,
            message="User data retrieved successfully",
            data={
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "disabled": current_user.disabled
            }
        )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")


@app.get("/", response_class=RedirectResponse)
async def home():
    return '/auth/login'


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse('dashboard.html', {"request": request})


@app.get('/auth/login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('auth_login.html', {"request": request})


@app.get('/message')
async def request_message(message: str,
                          role: str,
                          token: Annotated[str, Depends(oauth2_scheme)],
                          db: Session = Depends(get_db),
                          token_valid: bool = Depends(authenticate)):
    if not token_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credential")

    payload: dict = decode_token(token)
    username = payload.get("sub")

    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credential")

    logger.debug(f"message: {message}")
    logger.debug(f"token_valid: {token_valid}")

    chat = get_by_role_and_username(db, role, username)

    if not chat:
        set_chat(db, ChatModel(
            username=username,
            role=role,
            data=[
                {
                    "role": "system",
                    "content": role,
                },
                {
                    "role": "user",
                    "content": message,
                }]
        ))

    return ResponseModel(
        status=ResponseCode.SUCCESS.value,
        message="successfull"
    )


@app.get('/chat/all', response_model=ResponseModel)
async def chats(token: Annotated[str, Depends(oauth2_scheme)],
                db: Session = Depends(get_db),
                token_valid: bool = Depends(authenticate)):
    if not token_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credential")

    payload: dict = decode_token(token)
    username = payload.get("sub")

    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credential")

    chats: [MessageModel] = get_chats(db, username)
    return ResponseModel(
        status=ResponseCode.SUCCESS.value,
        message="successfull",
        data=chats
    )


@app.get('/auth/register', response_model=ResponseModel)
async def register(user: UserModel, db: Session = Depends(get_db)):
    if not user.username or not user.password or not user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username, password and email are required")

    if exists_user(db, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    try:
        response: UserEntity = create_user(db, user)
        return ResponseModel(
            status=ResponseCode.USER_CREATED.value,
            message="User created successfully" if response.id else "User already exists",
            data={
                "id": response.id,
                "username": response.username,
                "email": response.email,
            }
        )
    except Exception as exc:
        logger.error(f"error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app,
                host=os.getenv('APP_HOST', "0.0.0.0"),
                port=int(os.getenv('APP_PORT', 8000)),
                log_level=str(os.getenv('LOG_LEVEL', 'info')).lower())
