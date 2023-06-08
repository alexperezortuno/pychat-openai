from typing import Any, Optional

from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: int
    message: str
    data: Optional[Any] = None

    class Config:
        orm_mode = True
