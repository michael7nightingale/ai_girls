from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Основные настройки
    app_name: str = "AI Girls"
    debug: bool = False
    
    # База данных
    database_url: str = "postgresql+asyncpg://user:password@localhost/ai_girls"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Telegram
    telegram_token: str = ""
    telegram_webhook_url: Optional[str] = None
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "llama2"
    use_ollama: bool = True
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    
    # JWT
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Лимиты
    free_messages_per_day: int = 10
    premium_messages_per_day: int = 100
    
    class Config:
        env_file = ".env"


settings = Settings()
