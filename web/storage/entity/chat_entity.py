from sqlalchemy import Column, Integer, Sequence, String, JSON

from web.storage.connection import Base


class ChatEntity(Base):
    __tablename__ = "chat"

    id = Column(Integer, Sequence("sq_chat_id"), primary_key=True, index=True)
    key_id = Column(String, unique=True, default=None)
    username = Column(String, index=True)
    role = Column(String)
    data = Column(JSON)

    def __repr__(self):
        return f"Chat(id={self.id}, key_id={self.key_id}, username={self.username}, system={self.system}, data={self.data})"
