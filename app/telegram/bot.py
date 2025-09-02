import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.database import User, Character, Chat, Message, UserRole
from app.ai.service import AIService

logger = logging.getLogger(__name__)

ai_service = AIService()
bot = Bot(token=settings.telegram_token)
dp = Dispatcher()


async def start(message: types.Message):
    user = message.from_user
    async with AsyncSessionLocal() as db:
        
        try:
            db_user = db.query(User).filter(User.telegram_id == user.id).first()
            
            if not db_user:
                db_user = User(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                db.add(db_user)
                db.commit()
            
            welcome_text = f"""Привет, {user.first_name}! 👋

    Добро пожаловать в AI Girls - мир эротических AI персонажей! 

    🎭 Выбери персонажа для общения:
    • Бесплатные персонажи доступны всем
    • Премиум персонажи для подписчиков

    💬 Начни чат с любым персонажем
    💳 Получи премиум для большего количества сообщений

    Выбери действие:"""
            
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="👥 Персонажи", callback_data="characters"))
            builder.add(types.InlineKeyboardButton(text="💬 Мои чаты", callback_data="my_chats"))
            builder.add(types.InlineKeyboardButton(text="💳 Премиум", callback_data="premium"))
            builder.add(types.InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"))
            builder.adjust(2)
            
            await message.answer(welcome_text, reply_markup=builder.as_markup())
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")


async def show_characters(callback: types.CallbackQuery):
    await callback.answer()
    
    db = SessionLocal()
    try:
        characters = db.query(Character).filter(Character.is_active == True).all()
        
        if not characters:
            await callback.message.edit_text("Персонажи временно недоступны.")
            return
        
        text = "🎭 Доступные персонажи:\n\n"
        builder = InlineKeyboardBuilder()
        
        for char in characters:
            emoji = "💎" if char.is_premium else "🆓"
            text += f"{emoji} {char.name}\n{char.description[:100]}...\n\n"
            
            builder.add(types.InlineKeyboardButton(
                text=f"{emoji} {char.name}",
                callback_data=f"chat_with_{char.id}"
            ))
        
        builder.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="start"))
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        
    except Exception as e:
        logger.error(f"Error showing characters: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()


async def start_chat(callback: types.CallbackQuery):
    await callback.answer()
    
    character_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    
    db = SessionLocal()
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        user = db.query(User).filter(User.telegram_id == user_id).first()
        
        if not character or not user:
            await callback.message.edit_text("Персонаж не найден.")
            return
        
        if character.is_premium and user.role == UserRole.FREE:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="💳 Получить премиум", callback_data="premium"))
            builder.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="characters"))
            builder.adjust(1)
            
            await callback.message.edit_text(
                f"💎 {character.name} - премиум персонаж!\n\n"
                "Для общения с этим персонажем нужна премиум подписка.",
                reply_markup=builder.as_markup()
            )
            return
        
        chat = Chat(
            user_id=user.id,
            character_id=character.id,
            title=f"Чат с {character.name}"
        )
        db.add(chat)
        db.commit()
        
        welcome_msg = f"""💕 Привет! Я {character.name}!

{character.personality}

Давай познакомимся поближе... 😊

Просто напиши мне что-нибудь!"""
        
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="🔙 К персонажам", callback_data="characters"))
        
        await callback.message.edit_text(welcome_msg, reply_markup=builder.as_markup())
        
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()


async def handle_message(message: types.Message):
    user_id = message.from_user.id
    message_text = message.text
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await message.answer("Пожалуйста, начните с /start")
            return
        
        current_chat = db.query(Chat).filter(
            Chat.user_id == user.id
        ).order_by(Chat.created_at.desc()).first()
        
        if not current_chat:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="👥 Персонажи", callback_data="characters"))
            
            await message.answer(
                "Выберите персонажа для начала чата!",
                reply_markup=builder.as_markup()
            )
            return
        
        if not await check_message_limit(user, db):
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="💳 Получить премиум", callback_data="premium"))
            
            await message.answer(
                f"Достигнут лимит сообщений на сегодня ({settings.free_messages_per_day}).\n"
                "Получите премиум для большего количества сообщений!",
                reply_markup=builder.as_markup()
            )
            return
        
        user_message = Message(
            chat_id=current_chat.id,
            content=message_text,
            is_user_message=True
        )
        db.add(user_message)
        
        character = current_chat.character
        conversation_history = [
            {
                "content": msg.content,
                "is_user_message": msg.is_user_message
            }
            for msg in current_chat.messages[-10:]
        ]
        
        await message.answer("💭 Думаю...")
        
        ai_response = await ai_service.generate_response(
            character.personality,
            character.description,
            conversation_history,
            message_text
        )
        
        ai_message = Message(
            chat_id=current_chat.id,
            content=ai_response,
            is_user_message=False,
            tokens_used=ai_service.count_tokens(ai_response)
        )
        db.add(ai_message)
        
        user.messages_used_today += 1
        user.last_message_date = datetime.utcnow()
        
        db.commit()
        
        await message.answer(ai_response)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
    finally:
        db.close()


async def check_message_limit(user: User, db) -> bool:
    today = datetime.utcnow().date()
    last_message_date = user.last_message_date.date() if user.last_message_date else None
    
    if last_message_date != today:
        user.messages_used_today = 0
        db.commit()
    
    limit = settings.premium_messages_per_day if user.role == UserRole.PREMIUM else settings.free_messages_per_day
    return user.messages_used_today < limit


async def show_premium(callback: types.CallbackQuery):
    await callback.answer()
    
    text = """💎 Премиум подписка

Получите доступ к:
• Неограниченному количеству сообщений
• Эксклюзивным премиум персонажам
• Приоритетной поддержке
• Специальным функциям

Выберите план:"""
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="💳 Месячная подписка - $9.99", callback_data="subscribe_monthly"))
    builder.add(types.InlineKeyboardButton(text="💳 Годовая подписка - $99.99", callback_data="subscribe_yearly"))
    builder.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="start"))
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


async def show_help(callback: types.CallbackQuery):
    await callback.answer()
    
    text = """ℹ️ Помощь

🤖 Как использовать бота:
1. Выберите персонажа из списка
2. Начните общение
3. Получайте ответы от AI

💬 Команды:
/start - Главное меню
/characters - Список персонажей
/premium - Премиум подписка

💳 Лимиты:
• Бесплатные пользователи: {free_limit} сообщений в день
• Премиум пользователи: {premium_limit} сообщений в день

🔙 Назад в главное меню""".format(
        free_limit=settings.free_messages_per_day,
        premium_limit=settings.premium_messages_per_day
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="start"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


async def handle_subscription(callback: types.CallbackQuery):
    await callback.answer()
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="premium"))
    
    await callback.message.edit_text(
        "💳 Для оформления подписки перейдите на наш веб-сайт:\n\n"
        "🌐 https://your-domain.com/premium\n\n"
        "Или свяжитесь с поддержкой: @support",
        reply_markup=builder.as_markup()
    )


async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    
    if data == "start":
        await start(callback.message)
    elif data == "characters":
        await show_characters(callback)
    elif data.startswith("chat_with_"):
        await start_chat(callback)
    elif data == "premium":
        await show_premium(callback)
    elif data == "help":
        await show_help(callback)
    elif data.startswith("subscribe_"):
        await handle_subscription(callback)


def register_handlers():
    dp.message.register(start, Command("start"))
    dp.callback_query.register(handle_callback)
    dp.message.register(handle_message, lambda message: message.text and not message.text.startswith('/'))


async def start_bot():
    if not settings.telegram_token:
        logger.error("Telegram token not set!")
        return
    
    register_handlers()
    
    if settings.telegram_webhook_url:
        await bot.set_webhook(url=settings.telegram_webhook_url)
        await dp.start_polling(bot, webhook_url=settings.telegram_webhook_url)
    else:
        await dp.start_polling(bot)
