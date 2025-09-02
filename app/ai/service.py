import json
import logging
from typing import List, Optional

import openai
import anthropic
from app.core.config import settings
from app.ai.ollama_service import OllamaService

logger = logging.getLogger(__name__)

openai.api_key = settings.openai_api_key
anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.anthropic_client = anthropic_client
        self.ollama_service = OllamaService(
            base_url=settings.ollama_base_url
        )
    
    async def generate_response(
        self,
        character_personality: str,
        character_description: str,
        conversation_history: List[dict],
        user_message: str,
        use_anthropic: bool = False,
        use_ollama: bool = None
    ) -> str:
        # Определяем какой сервис использовать
        if use_ollama is None:
            use_ollama = settings.use_ollama
        
        try:
            if use_ollama:
                return await self._generate_ollama_response(
                    character_personality,
                    character_description,
                    conversation_history,
                    user_message
                )
            elif use_anthropic:
                return await self._generate_anthropic_response(
                    character_personality,
                    character_description,
                    conversation_history,
                    user_message
                )
            else:
                return await self._generate_openai_response(
                    character_personality,
                    character_description,
                    conversation_history,
                    user_message
                )
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "Извините, произошла ошибка. Попробуйте еще раз."
    
    async def _generate_openai_response(
        self,
        character_personality: str,
        character_description: str,
        conversation_history: List[dict],
        user_message: str
    ) -> str:
        system_prompt = f"""Ты {character_description}

Твоя личность: {character_personality}

Ты должна отвечать от первого лица, как будто ты действительно этот персонаж. 
Будь естественной, игривой и немного кокетливой. Отвечай на русском языке.
Не используй формальный тон, будь дружелюбной и интимной.
Максимальная длина ответа - 200 слов."""

        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in conversation_history[-10:]:  # Последние 10 сообщений
            role = "user" if msg["is_user_message"] else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            max_tokens=300,
            temperature=0.8,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_anthropic_response(
        self,
        character_personality: str,
        character_description: str,
        conversation_history: List[dict],
        user_message: str
    ) -> str:
        system_prompt = f"""Ты {character_description}

Твоя личность: {character_personality}

Ты должна отвечать от первого лица, как будто ты действительно этот персонаж. 
Будь естественной, игривой и немного кокетливой. Отвечай на русском языке.
Не используй формальный тон, будь дружелюбной и интимной.
Максимальная длина ответа - 200 слов."""

        conversation_text = ""
        for msg in conversation_history[-10:]:
            speaker = "Пользователь" if msg["is_user_message"] else "Ты"
            conversation_text += f"{speaker}: {msg['content']}\n"
        
        conversation_text += f"Пользователь: {user_message}\nТы:"
        
        response = self.anthropic_client.messages.create(
            model=settings.anthropic_model,
            max_tokens=300,
            temperature=0.8,
            system=system_prompt,
            messages=[{"role": "user", "content": conversation_text}]
        )
        
        return response.content[0].text.strip()
    
    async def _generate_ollama_response(
        self,
        character_personality: str,
        character_description: str,
        conversation_history: List[dict],
        user_message: str
    ) -> str:
        """Генерация ответа через Ollama"""
        return await self.ollama_service.generate_character_response(
            character_name="AI Girl",
            character_personality=character_personality,
            character_description=character_description,
            conversation_history=conversation_history,
            user_message=user_message,
            model_name=settings.ollama_default_model
        )
    
    def count_tokens(self, text: str) -> int:
        return len(text.split())  # Простая оценка токенов
