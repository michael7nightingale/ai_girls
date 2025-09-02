#!/usr/bin/env python3
"""
Скрипт для запуска AI Girls приложения
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.telegram.bot import start_bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска"""
    try:
        logger.info("🚀 Запуск AI Girls приложения...")
        
        # Проверяем наличие необходимых переменных окружения
        required_vars = [
            'DATABASE_URL',
            'TELEGRAM_TOKEN',
            'SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(settings, var.lower(), None):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
            logger.error("Создайте файл .env на основе env.example")
            return
        
        # Запускаем Telegram бота в отдельной задаче
        if settings.telegram_token:
            logger.info("🤖 Запуск Telegram бота...")
            # bot_task = asyncio.create_task(start_bot())
        else:
            logger.warning("⚠️ Telegram токен не настроен, бот не запущен")
            bot_task = None
        
        # Запускаем веб-сервер
        logger.info("🌐 Запуск веб-сервера...")
        
        import uvicorn
        config = uvicorn.Config(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        # Запускаем сервер
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки...")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        raise
    finally:
        logger.info("👋 Приложение остановлено")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
