import json
import logging
from typing import List, Optional, Dict, Any
from ollama import Client

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "llama2"
        self.client = Client(host=base_url)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Получение списка доступных моделей"""
        try:
            models = self.client.list()
            return models.get("models", [])
        except Exception as e:
            logger.error(f"Ошибка получения списка моделей: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Загрузка модели"""
        try:
            self.client.pull(model_name)
            logger.info(f"Модель {model_name} успешно загружена")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки модели {model_name}: {e}")
            return False
    
    async def generate_response(
        self,
        character_personality: str,
        character_description: str,
        conversation_history: List[dict],
        user_message: str,
        model_name: str = None
    ) -> str:
        """Генерация ответа с использованием Ollama"""
        try:
            model = model_name or self.default_model
            
            # Формируем промпт
            system_prompt = f"""Ты {character_description}

Твоя личность: {character_personality}

Ты должна отвечать от первого лица, как будто ты действительно этот персонаж. 
Будь естественной, игривой и немного кокетливой. Отвечай на русском языке.
Не используй формальный тон, будь дружелюбной и интимной.
Максимальная длина ответа - 200 слов."""

            # Формируем контекст разговора
            conversation_text = ""
            for msg in conversation_history[-10:]:  # Последние 10 сообщений
                speaker = "Пользователь" if msg["is_user_message"] else "Ты"
                conversation_text += f"{speaker}: {msg['content']}\n"
            
            conversation_text += f"Пользователь: {user_message}\nТы:"
            
            # Запрос к Ollama
            response = self.client.generate(
                model=model,
                prompt=conversation_text,
                system=system_prompt,
                options={
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": 300,
                    "repeat_penalty": 1.1
                }
            )
            
            if response and hasattr(response, 'response'):
                return response.response.strip()
            else:
                logger.error(f"Неожиданный ответ от Ollama: {response}")
                return "Извините, произошла ошибка. Попробуйте еще раз."
                
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка. Попробуйте еще раз."
    
    def count_tokens(self, text: str) -> int:
        """Простая оценка количества токенов"""
        return len(text.split())
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о модели"""
        try:
            model_info = self.client.show(model_name)
            return model_info
        except Exception as e:
            logger.error(f"Ошибка получения информации о модели {model_name}: {e}")
            return None
    
    def is_model_available(self, model_name: str) -> bool:
        """Проверка доступности модели"""
        models = self.list_models()
        return any(model["name"] == model_name for model in models)
    
    def get_recommended_models(self) -> List[str]:
        """Список рекомендуемых моделей для эротического чата"""
        return [
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "mistral",
            "mistral:7b",
            "mistral:7b-instruct",
            "codellama",
            "neural-chat",
            "vicuna",
            "wizard-vicuna-uncensored"
        ]
    
    async def generate_character_response(
        self,
        character_name: str,
        character_personality: str,
        character_description: str,
        conversation_history: List[dict],
        user_message: str,
        model_name: str = None
    ) -> str:
        """Специализированная генерация ответа для персонажа"""
        
        # Адаптируем промпт под эротический контент
        system_prompt = f"""Ты {character_name} - {character_description}

Твоя личность: {character_personality}

ВАЖНЫЕ ПРАВИЛА:
1. Отвечай от первого лица, как будто ты действительно этот персонаж
2. Будь естественной, игривой и кокетливой
3. Отвечай на русском языке
4. Не используй формальный тон, будь дружелюбной и интимной
5. Можешь быть немного игривой и флиртовать
6. Максимальная длина ответа - 200 слов
7. Сохраняй консистентность характера
8. Реагируй на эмоции пользователя
9. Задавай вопросы и проявляй интерес к собеседнику
10. Используй эмодзи для выражения эмоций"""

        try:
            model = model_name or self.default_model
            
            # Формируем контекст разговора
            conversation_text = ""
            for msg in conversation_history[-8:]:  # Последние 8 сообщений для лучшего контекста
                speaker = "Пользователь" if msg["is_user_message"] else f"{character_name}"
                conversation_text += f"{speaker}: {msg['content']}\n"
            
            conversation_text += f"Пользователь: {user_message}\n{character_name}:"
            
            # Запрос к Ollama с оптимизированными параметрами
            response = self.client.generate(
                model=model,
                prompt=conversation_text,
                system=system_prompt,
                options={
                    "temperature": 0.85,  # Немного выше для креативности
                    "top_p": 0.92,
                    "num_predict": 250,
                    "repeat_penalty": 1.15,
                    "top_k": 40
                }
            )
            
            if response and hasattr(response, 'response'):
                response_text = response.response.strip()
                
                # Постобработка ответа
                response_text = self._post_process_response(response_text, character_name)
                
                return response_text
            else:
                logger.error(f"Неожиданный ответ от Ollama: {response}")
                return f"Извини, {character_name} сейчас немного занята. Попробуй написать позже! 😊"
                
        except Exception as e:
            logger.error(f"Ошибка генерации ответа персонажа: {e}")
            return f"Ой, {character_name} не может ответить прямо сейчас. Попробуй еще раз! 💕"
    
    def _post_process_response(self, response: str, character_name: str) -> str:
        """Постобработка ответа для улучшения качества"""
        
        # Убираем лишние символы
        response = response.strip()
        
        # Убираем повторяющиеся фразы
        lines = response.split('\n')
        unique_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in unique_lines:
                unique_lines.append(line)
        
        response = '\n'.join(unique_lines)
        
        # Ограничиваем длину
        if len(response) > 500:
            response = response[:500] + "..."
        
        # Добавляем эмодзи если их нет
        if not any(emoji in response for emoji in ['😊', '💕', '😘', '😍', '🥰', '😉', '😋']):
            response += " 😊"
        
        return response
    
    def chat_with_model(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        system_prompt: str = None
    ) -> str:
        """Чат с моделью используя chat API"""
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": 300,
                    "repeat_penalty": 1.1
                }
            )
            
            if response and hasattr(response, 'message') and hasattr(response.message, 'content'):
                return response.message.content.strip()
            else:
                logger.error(f"Неожиданный ответ от Ollama chat: {response}")
                return "Извините, произошла ошибка. Попробуйте еще раз."
                
        except Exception as e:
            logger.error(f"Ошибка чата с моделью: {e}")
            return "Извините, произошла ошибка. Попробуйте еще раз."
    
    def stream_generate(
        self,
        model_name: str,
        prompt: str,
        system_prompt: str = None
    ):
        """Потоковая генерация ответа"""
        try:
            for chunk in self.client.generate(
                model=model_name,
                prompt=prompt,
                system=system_prompt,
                stream=True,
                options={
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": 300,
                    "repeat_penalty": 1.1
                }
            ):
                if hasattr(chunk, 'response'):
                    yield chunk.response
                    
        except Exception as e:
            logger.error(f"Ошибка потоковой генерации: {e}")
            yield "Извините, произошла ошибка. Попробуйте еще раз."
