from typing import Optional, Any
from pydantic import BaseModel


class ChatModel(BaseModel):
    id:  Optional[int]
    key: Optional[str]
    username: str
    role: str
    data: Optional[Any]
