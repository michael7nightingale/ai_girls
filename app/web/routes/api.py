from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.models.database import User, Character, Chat, Message, UserRole
from app.ai.service import AIService
from app.billing.service import BillingService

router = APIRouter()
security = HTTPBearer()
ai_service = AIService()
billing_service = BillingService()


class MessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    content: str
    is_user_message: bool
    created_at: datetime


class CharacterResponse(BaseModel):
    id: int
    name: str
    description: str
    personality: str
    avatar_url: Optional[str]
    is_premium: bool


class ChatResponse(BaseModel):
    id: int
    title: str
    character: CharacterResponse
    created_at: datetime
    updated_at: datetime


class SubscriptionRequest(BaseModel):
    subscription_type: str


async def get_current_user(
    token: str = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Для демонстрации используем простую проверку
    # В реальном приложении здесь должна быть проверка JWT токена
    try:
        # Пока что ищем первого пользователя в базе
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            # Если пользователей нет, создаем тестового
            user = User(
                telegram_id=123456789,
                username="test_user",
                first_name="Тест",
                last_name="Пользователь",
                role=UserRole.FREE
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user
    except Exception as e:
        raise e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.get("/characters", response_model=List[CharacterResponse])
async def get_characters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Character).where(Character.is_active == True))
    characters = result.scalars().all()
    return [
        CharacterResponse(
            id=char.id,
            name=char.name,
            description=char.description,
            personality=char.personality,
            avatar_url=char.avatar_url,
            is_premium=char.is_premium
        )
        for char in characters
    ]


@router.get("/characters/public", response_model=List[CharacterResponse])
async def get_characters_public(
    db: AsyncSession = Depends(get_db)
):
    """Получить список персонажей без аутентификации"""
    result = await db.execute(select(Character).where(Character.is_active == True))
    characters = result.scalars().all()
    return [
        CharacterResponse(
            id=char.id,
            name=char.name,
            description=char.description,
            personality=char.personality,
            avatar_url=char.avatar_url,
            is_premium=char.is_premium
        )
        for char in characters
    ]


@router.get("/chats", response_model=List[ChatResponse])
async def get_user_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Chat).where(Chat.user_id == current_user.id))
    chats = result.scalars().all()
    return [
        ChatResponse(
            id=chat.id,
            title=chat.title,
            character=CharacterResponse(
                id=chat.character.id,
                name=chat.character.name,
                description=chat.character.description,
                personality=chat.character.personality,
                avatar_url=chat.character.avatar_url,
                is_premium=chat.character.is_premium
            ),
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )
        for chat in chats
    ]


@router.post("/chats")
async def create_chat(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    if character.is_premium and current_user.role == UserRole.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium character requires premium subscription"
        )
    
    chat = Chat(
        user_id=current_user.id,
        character_id=character.id,
        title=f"Чат с {character.name}"
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    
    return {"chat_id": chat.id, "title": chat.title}


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    result = await db.execute(select(Message).where(Message.chat_id == chat_id))
    messages = result.scalars().all()
    return [
        MessageResponse(
            id=msg.id,
            content=msg.content,
            is_user_message=msg.is_user_message,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.post("/chats/{chat_id}/messages")
async def send_message(
    chat_id: int,
    message_request: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id).options(joinedload(Chat.character))
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if not await check_message_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Message limit exceeded"
        )
    
    user_message = Message(
        chat_id=chat.id,
        content=message_request.content,
        is_user_message=True
    )
    db.add(user_message)
    
    # Получаем историю сообщений
    result = await db.execute(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.desc()).limit(10))
    recent_messages = result.scalars().all()
    
    conversation_history = [
        {
            "content": msg.content,
            "is_user_message": msg.is_user_message
        }
        for msg in reversed(recent_messages)
    ]
    
    ai_response = await ai_service.generate_response(
        chat.character.personality,
        chat.character.description,
        conversation_history,
        message_request.content
    )
    
    ai_message = Message(
        chat_id=chat.id,
        content=ai_response,
        is_user_message=False,
        tokens_used=ai_service.count_tokens(ai_response)
    )
    db.add(ai_message)
    
    current_user.messages_used_today += 1
    current_user.last_message_date = datetime.utcnow()
    
    await db.commit()
    
    return {
        "user_message": MessageResponse(
            id=user_message.id,
            content=user_message.content,
            is_user_message=True,
            created_at=user_message.created_at
        ),
        "ai_message": MessageResponse(
            id=ai_message.id,
            content=ai_message.content,
            is_user_message=False,
            created_at=ai_message.created_at
        )
    }


async def check_message_limit(user: User, db: AsyncSession) -> bool:
    today = datetime.utcnow().date()
    last_message_date = user.last_message_date.date() if user.last_message_date else None
    
    if last_message_date != today:
        user.messages_used_today = 0
        await db.commit()
    
    from app.core.config import settings
    limit = settings.premium_messages_per_day if user.role == UserRole.PREMIUM else settings.free_messages_per_day
    return user.messages_used_today < limit


@router.post("/subscription")
async def create_subscription(
    subscription_request: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await billing_service.create_subscription(
            current_user,
            subscription_request.subscription_type,
            db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    return await billing_service.check_subscription_status(current_user)


@router.get("/user/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "subscription_type": current_user.subscription_type,
        "subscription_expires": current_user.subscription_expires,
        "messages_used_today": current_user.messages_used_today,
        "created_at": current_user.created_at
    }


@router.get("/auth/test")
async def test_auth():
    """Тестовый эндпоинт для проверки аутентификации"""
    return {"message": "Authentication test endpoint", "token_required": True}
