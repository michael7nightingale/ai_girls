# 🚀 Быстрый старт AI Girls

## 📋 Что у вас есть

Полноценное приложение для эротического AI чата с:

- 🤖 **Telegram бот** на aiogram 3.x
- 🌐 **Веб-сайт** с современным дизайном
- 💳 **Система биллинга** (Stripe, PayPal, Crypto)
- 🧠 **AI модели** (OpenAI, Anthropic, Ollama)
- 💾 **База данных** PostgreSQL
- 🔐 **Аутентификация** и профили

## ⚡ Быстрый запуск

### 1. Установка зависимостей
```bash
uv sync
```

### 2. Настройка окружения
```bash
cp env.example .env
# Отредактируйте .env файл
```

### 3. Запуск
```bash
python run.py
```

## 🔧 Минимальная настройка

В файле `.env` обязательно настройте:

```env
# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost/aig_db

# Telegram бот
TELEGRAM_TOKEN=your_bot_token_from_botfather

# Секретный ключ
SECRET_KEY=your_long_random_secret_key

# AI сервис (хотя бы один)
OPENAI_API_KEY=your_openai_key
# или
ANTHROPIC_API_KEY=your_anthropic_key
# или
USE_OLLAMA=true
```

## 🌟 Основные функции

### Telegram бот
- `/start` - Главное меню
- Выбор персонажей
- Чат с AI
- Управление подпиской

### Веб-сайт
- http://localhost:8000 - Главная страница
- http://localhost:8000/characters - Персонажи
- http://localhost:8000/premium - Подписка
- http://localhost:8000/profile - Профиль

### API
- `GET /api/characters` - Список персонажей
- `POST /api/chat/{id}/message` - Отправить сообщение
- `GET /api/billing/plans` - Планы подписки

## 💰 Монетизация

### Планы подписки
- **Бесплатный**: 10 сообщений/день
- **Месячный**: $9.99 - безлимит
- **Годовой**: $59.99 - все функции
- **Пожизненный**: $199 - навсегда

### Платежные системы
- 💳 Stripe (карты)
- 💰 PayPal
- ₿ Криптовалюты

## 🎭 Персонажи

Приложение поставляется с готовыми персонажами:
- **Бесплатные**: Анна, Елена, Виктория
- **Премиум**: Мария, Алиса, София

## 🔧 Разработка

### Добавление персонажа
```python
from app.models.database import Character
character = Character(
    name="Новый персонаж",
    description="Описание",
    personality="Личность",
    is_premium=False
)
```

### Настройка AI
```python
# В app/ai/service.py
# Измените промпты для персонажей
```

## 🚀 Продакшн

### Docker
```bash
docker-compose up -d
```

### VPS
```bash
# Установите зависимости
sudo apt install python3.13 postgresql nginx

# Настройте systemd
sudo systemctl enable aig
sudo systemctl start aig
```

## 📞 Поддержка

- 📧 Email: support@aigirl.one
- 💬 Telegram: @aigirl_support
- 📖 Документация: https://docs.aigirl.one

---

**AI Girls** - Ваш идеальный спутник для интимного общения! 💕
