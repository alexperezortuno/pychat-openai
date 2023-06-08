from typing import Optional

from pydantic import BaseModel


class UserModel(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None


class UserModelInDB(UserModel):
    password: Optional[str] = None
