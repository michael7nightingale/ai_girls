from fastapi import APIRouter

from .api import router as api_router
from .web import router as web_router
from .ollama_api import router as ollama_router

api_router = api_router
web_router = web_router
ollama_router = ollama_router
