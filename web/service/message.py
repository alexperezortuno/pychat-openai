# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session

from ai.core.commons import log_lvl, log_str
from ai.core.logger import get_logger
from ai.core.utils import random_str
from web.storage.entity.chat_entity import ChatEntity
from web.storage.model.chat_model import ChatModel
from web.storage.model.message_model import MessageModel

logger = get_logger(log_lvl, log_str, __name__)


def get_user_messages(db: Session, username: str, data: MessageModel) -> ChatEntity or None:
    try:
        messages: ChatEntity = db.query(ChatEntity).filter(ChatEntity.username == username, ChatEntity.role == data.role).first()
        logger.debug(messages)
    except Exception as ex:
        logger.error(f"get_user_messages: {ex}")
        return None


def get_chats(db: Session, username: str) -> [ChatEntity] or None:
    try:
        chats: [ChatEntity] = db.query(ChatEntity).filter(ChatEntity.username == username).all()
        logger.debug(chats)
        return chats
    except Exception as ex:
        logger.error(f"get_chats: {ex}")
        return None


def get_by_key(db: Session, key: str) -> ChatEntity or None:
    try:
        chat: ChatEntity = db.query(ChatEntity).filter(ChatEntity.key == key).first()
        logger.debug(chat)
        return chat
    except Exception as ex:
        logger.error(f"get_by_key: {ex}")
        return None


def get_by_role_and_username(db: Session, role: str, username: str) -> ChatEntity or None:
    try:
        chat: ChatEntity = db.query(ChatEntity).filter(ChatEntity.role == role, ChatEntity.username == username).first()
        logger.debug(chat)
        return chat
    except Exception as ex:
        logger.error(f"get_by_role: {ex}")
        return None


def set_chat(db: Session, chat_model: ChatModel) -> ChatEntity:
    key_id: str = random_str(25, 4)

    db_chat = ChatEntity(
        key_id=key_id,
        username=chat_model.username,
        role=chat_model.role,
        data=chat_model.data,
    )

    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat
