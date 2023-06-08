from sqlalchemy import Column, Integer, String, Boolean, Sequence

from web.storage.connection import Base


class UserEntity(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("sq_user_id"), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    disabled = Column(Boolean)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, full_name={self.full_name}, disabled={self.disabled})"
