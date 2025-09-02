# AI Girls - Эротический AI Чат

Полноценное приложение для общения с AI персонажами, включающее Telegram бота, веб-сайт и систему биллинга.

## 🌟 Особенности

### 🤖 AI Персонажи
- **Эротические AI персонажи** с уникальными личностями
- **Бесплатные и премиум персонажи**
- **Продвинутые LLM модели** (OpenAI, Anthropic, Ollama)
- **Запоминание контекста** разговора
- **Персонализированные ответы**

### 💬 Telegram Бот
- **Полнофункциональный бот** на aiogram 3.x
- **Инлайн кнопки** для навигации
- **Система персонажей** с фильтрацией
- **Интеграция с веб-платформой**
- **Поддержка webhook и polling**

### 🌐 Веб-сайт
- **Современный дизайн** с Tailwind CSS
- **Адаптивный интерфейс** для всех устройств
- **Система авторизации** и профилей
- **Интерактивный чат** в реальном времени
- **Управление подписками**

### 💳 Система Биллинга
- **Множественные платежные системы** (Stripe, PayPal, Crypto)
- **Гибкие планы подписки** (месячные, годовые, пожизненные)
- **Автоматическое управление** подписками
- **История платежей** и статистика
- **Webhook интеграции**

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.13+
- PostgreSQL 12+
- Ollama (опционально)
- Telegram Bot Token
- API ключи (OpenAI, Anthropic, Stripe, PayPal)

### Установка

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd aig
```

2. **Установите зависимости**
```bash
uv sync
```

3. **Настройте переменные окружения**
```bash
cp env.example .env
# Отредактируйте .env файл
```

4. **Настройте базу данных**
```bash
# Создайте базу данных PostgreSQL
createdb aig_db

# Запустите миграции
alembic upgrade head
```

5. **Инициализируйте данные**
```bash
python -m app.core.init_data
```

6. **Запустите приложение**
```bash
# Разработка
uvicorn main:app --reload

# Продакшн
uvicorn main:app --host 0.0.0.0 --port 8000
```

## ⚙️ Конфигурация

### Переменные окружения

```env
# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost/aig_db

# Telegram
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# AI Сервисы
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2

# Платежные системы
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret

# Приложение
SECRET_KEY=your_secret_key
BASE_URL=https://your-domain.com
DEBUG=false
```

### Настройка Ollama

1. **Установите Ollama**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

2. **Запустите Ollama**
```bash
ollama serve
```

3. **Загрузите модели**
```bash
ollama pull llama2
ollama pull mistral
```

## 📱 Использование

### Telegram Бот

1. Создайте бота через @BotFather
2. Получите токен и добавьте в .env
3. Запустите бота:
```bash
python -m app.telegram.bot
```

### Веб-сайт

1. Откройте http://localhost:8000
2. Зарегистрируйтесь или войдите
3. Выберите персонажа для общения
4. Начните чат!

### API Endpoints

- `GET /api/characters` - Список персонажей
- `POST /api/chat/{character_id}/message` - Отправить сообщение
- `GET /api/billing/plans` - Планы подписки
- `POST /api/billing/create-payment` - Создать платеж

## 🏗️ Архитектура

```
aig/
├── app/
│   ├── ai/                 # AI сервисы
│   │   ├── service.py      # Основной AI сервис
│   │   └── ollama_service.py # Ollama интеграция
│   ├── billing/            # Система биллинга
│   │   └── service.py      # Платежные сервисы
│   ├── core/               # Основные компоненты
│   │   ├── config.py       # Конфигурация
│   │   ├── database.py     # База данных
│   │   └── auth.py         # Аутентификация
│   ├── models/             # Модели данных
│   │   └── database.py     # SQLAlchemy модели
│   ├── telegram/           # Telegram бот
│   │   └── bot.py          # Основной бот
│   └── web/                # Веб-приложение
│       ├── routes/         # API маршруты
│       ├── templates/      # HTML шаблоны
│       └── static/         # Статические файлы
├── alembic/                # Миграции БД
├── main.py                 # Точка входа
└── pyproject.toml          # Зависимости
```

## 💰 Монетизация

### Планы подписки

- **Бесплатный**: 10 сообщений/день, базовые персонажи
- **Месячный ($9.99)**: Безлимитные сообщения, премиум персонажи
- **Годовой ($59.99)**: Все преимущества + эксклюзивные функции
- **Пожизненный ($199)**: Все навсегда + VIP статус

### Платежные системы

- **Stripe** - Кредитные карты
- **PayPal** - Электронные платежи
- **Криптовалюты** - Bitcoin, Ethereum

## 🔧 Разработка

### Структура базы данных

```sql
-- Пользователи
users (id, telegram_id, username, email, role, subscription_type, subscription_expires)

-- Персонажи
characters (id, name, description, personality, is_premium, is_active)

-- Чаты
chats (id, user_id, character_id, title, created_at, updated_at)

-- Сообщения
messages (id, chat_id, content, is_user_message, tokens_used, created_at)

-- Платежи
payments (id, user_id, amount, currency, subscription_type, status, payment_method)
```

### Добавление нового персонажа

```python
from app.core.database import SessionLocal
from app.models.database import Character

db = SessionLocal()
character = Character(
    name="Анна",
    description="Сексуальная брюнетка 25 лет",
    personality="Игривая и кокетливая девушка, любит флиртовать",
    is_premium=True,
    is_active=True
)
db.add(character)
db.commit()
```

### Настройка новых AI моделей

```python
# В app/ai/service.py
async def _generate_custom_response(self, ...):
    # Ваша логика генерации
    pass
```

## 🚀 Деплой

### Docker

```bash
# Сборка образа
docker build -t aig .

# Запуск
docker-compose up -d
```

### VPS/Сервер

1. **Настройте сервер**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 postgresql nginx

# Установите Python зависимости
pip install -r requirements.txt
```

2. **Настройте Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Настройте systemd**
```ini
[Unit]
Description=AI Girls App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/aig
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 Мониторинг

### Логи

```bash
# Просмотр логов
tail -f /var/log/aig/app.log

# Логи Telegram бота
tail -f /var/log/aig/telegram.log
```

### Метрики

- Количество активных пользователей
- Объем сообщений
- Конверсия в премиум
- Доходы по планам

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. LICENSE файл

## 🆘 Поддержка

- **Email**: support@aigirl.one
- **Telegram**: @aigirl_support
- **Документация**: https://docs.aigirl.one

## 🔮 Планы развития

- [ ] Мобильное приложение
- [ ] Голосовые сообщения
- [ ] Видео чат
- [ ] Социальные функции
- [ ] AI генерация изображений
- [ ] Мультиязычность

---

**AI Girls** - Ваш идеальный спутник для интимного общения с AI персонажами! 💕
