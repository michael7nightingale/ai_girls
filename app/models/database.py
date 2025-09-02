from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserRole(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"


class SubscriptionType(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    role = Column(String(50), default=UserRole.FREE)
    subscription_type = Column(String(50), nullable=True)
    subscription_expires = Column(DateTime, nullable=True)
    messages_used_today = Column(Integer, default=0)
    last_message_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chats = relationship("Chat", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Character(Base):
    __tablename__ = "character"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    personality = Column(Text, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chats = relationship("Chat", back_populates="character")


class Chat(Base):
    __tablename__ = "chat"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    character_id = Column(Integer, ForeignKey("character.id"))
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="chats")
    character = relationship("Character", back_populates="chats")
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "message"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chat.id"))
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, default=True)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chat = relationship("Chat", back_populates="messages")


class Payment(Base):
    __tablename__ = "payment"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    stripe_payment_intent_id = Column(String(255), unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    subscription_type = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="payments")


class UserSession(Base):
    __tablename__ = "user_session"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    session_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
