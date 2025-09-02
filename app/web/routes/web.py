from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/characters", response_class=HTMLResponse)
async def characters_page(request: Request):
    return templates.TemplateResponse("characters.html", {"request": request})


@router.get("/premium", response_class=HTMLResponse)
async def premium_page(request: Request):
    return templates.TemplateResponse("premium.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/ollama", response_class=HTMLResponse)
async def ollama_page(request: Request):
    return templates.TemplateResponse("ollama.html", {"request": request})
