from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.ai.ollama_service import OllamaService
from app.core.config import settings

router = APIRouter()
ollama_service = OllamaService(base_url=settings.ollama_base_url)


@router.get("/models", response_model=List[Dict[str, Any]])
async def get_models():
    """Получение списка доступных моделей"""
    try:
        models = ollama_service.list_models()
        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения списка моделей: {str(e)}"
        )


@router.post("/models/{model_name}/pull")
async def pull_model(model_name: str):
    """Загрузка модели"""
    try:
        success = ollama_service.pull_model(model_name)
        if success:
            return {"message": f"Модель {model_name} успешно загружена"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Не удалось загрузить модель {model_name}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка загрузки модели: {str(e)}"
        )


@router.get("/models/{model_name}/info")
async def get_model_info(model_name: str):
    """Получение информации о модели"""
    try:
        info = ollama_service.get_model_info(model_name)
        if info:
            return info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Модель {model_name} не найдена"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения информации о модели: {str(e)}"
        )


@router.get("/models/recommended")
async def get_recommended_models():
    """Получение списка рекомендуемых моделей"""
    try:
        models = ollama_service.get_recommended_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения рекомендуемых моделей: {str(e)}"
        )


@router.get("/status")
async def get_ollama_status():
    """Получение статуса Ollama"""
    try:
        models = ollama_service.list_models()
        return {
            "status": "running",
            "models_count": len(models),
            "default_model": settings.ollama_default_model,
            "base_url": settings.ollama_base_url
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "default_model": settings.ollama_default_model,
            "base_url": settings.ollama_base_url
        }
