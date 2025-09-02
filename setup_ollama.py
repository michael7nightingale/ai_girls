#!/usr/bin/env python3
"""
Скрипт для установки и настройки Ollama для AI Girls
"""

import os
import sys
import subprocess
import platform
import requests
import time
from pathlib import Path


def check_ollama_installed() -> bool:
    """Проверка установки Ollama"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_ollama():
    """Установка Ollama"""
    system = platform.system().lower()
    
    print("🚀 Установка Ollama...")
    
    if system == "linux":
        install_ollama_linux()
    elif system == "darwin":  # macOS
        install_ollama_macos()
    elif system == "windows":
        install_ollama_windows()
    else:
        print(f"❌ Неподдерживаемая операционная система: {system}")
        return False
    
    return True


def install_ollama_linux():
    """Установка Ollama на Linux"""
    try:
        # Установка через curl
        install_script = """
        curl -fsSL https://ollama.ai/install.sh | sh
        """
        
        print("📥 Загрузка и установка Ollama...")
        result = subprocess.run(install_script, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ollama успешно установлен!")
        else:
            print(f"❌ Ошибка установки: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка установки Ollama: {e}")
        return False


def install_ollama_macos():
    """Установка Ollama на macOS"""
    try:
        # Проверяем наличие Homebrew
        result = subprocess.run(['which', 'brew'], capture_output=True)
        if result.returncode != 0:
            print("❌ Homebrew не установлен. Установите Homebrew: https://brew.sh")
            return False
        
        # Установка через Homebrew
        print("📥 Установка Ollama через Homebrew...")
        result = subprocess.run(['brew', 'install', 'ollama'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ollama успешно установлен!")
        else:
            print(f"❌ Ошибка установки: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка установки Ollama: {e}")
        return False


def install_ollama_windows():
    """Установка Ollama на Windows"""
    print("📥 Для Windows скачайте Ollama с https://ollama.ai/download")
    print("После установки запустите этот скрипт снова")
    return False


def start_ollama_service():
    """Запуск сервиса Ollama"""
    try:
        print("🔄 Запуск сервиса Ollama...")
        
        # Проверяем, запущен ли уже сервис
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Сервис Ollama уже запущен")
                return True
        except:
            pass
        
        # Запускаем сервис
        if platform.system().lower() == "windows":
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(['ollama', 'serve'])
        
        # Ждем запуска сервиса
        print("⏳ Ожидание запуска сервиса...")
        for i in range(30):  # Ждем до 30 секунд
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    print("✅ Сервис Ollama успешно запущен!")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("❌ Не удалось запустить сервис Ollama")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка запуска сервиса: {e}")
        return False


def download_models():
    """Загрузка рекомендуемых моделей"""
    recommended_models = [
        "llama2",
        "mistral",
        "neural-chat"
    ]
    
    print("📥 Загрузка рекомендуемых моделей...")
    
    for model in recommended_models:
        print(f"📦 Загрузка модели {model}...")
        try:
            result = subprocess.run(['ollama', 'pull', model], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Модель {model} загружена")
            else:
                print(f"⚠️  Ошибка загрузки модели {model}: {result.stderr}")
        except Exception as e:
            print(f"❌ Ошибка загрузки модели {model}: {e}")


def test_ollama():
    """Тестирование Ollama"""
    print("🧪 Тестирование Ollama...")
    
    try:
        # Проверяем доступность API
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print("❌ API Ollama недоступен")
            return False
        
        # Проверяем наличие моделей
        models = response.json().get("models", [])
        if not models:
            print("⚠️  Модели не найдены. Запустите download_models()")
            return False
        
        print(f"✅ Найдено {len(models)} моделей:")
        for model in models[:5]:  # Показываем первые 5
            print(f"  - {model['name']}")
        
        # Тестируем генерацию
        print("🧪 Тестирование генерации...")
        test_prompt = {
            "model": "llama2",
            "prompt": "Привет! Как дела?",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=test_prompt, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                print("✅ Генерация работает!")
                return True
        
        print("❌ Ошибка тестирования генерации")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False


def setup_ollama_config():
    """Настройка конфигурации Ollama"""
    print("⚙️  Настройка конфигурации...")
    
    # Создаем конфигурационный файл для AI Girls
    config_dir = Path.home() / ".ollama"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "ai_girls_config.json"
    config = {
        "default_model": "llama2",
        "temperature": 0.85,
        "top_p": 0.92,
        "max_tokens": 250,
        "repeat_penalty": 1.15,
        "top_k": 40
    }
    
    try:
        import json
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Конфигурация сохранена")
    except Exception as e:
        print(f"⚠️  Ошибка сохранения конфигурации: {e}")


def main():
    """Главная функция"""
    print("🤖 AI Girls - Настройка Ollama")
    print("=" * 40)
    
    # Проверяем установку
    if not check_ollama_installed():
        print("📥 Ollama не установлен")
        if not install_ollama():
            return
    else:
        print("✅ Ollama уже установлен")
    
    # Запускаем сервис
    if not start_ollama_service():
        print("❌ Не удалось запустить сервис")
        return
    
    # Загружаем модели
    download_models()
    
    # Настраиваем конфигурацию
    setup_ollama_config()
    
    # Тестируем
    if test_ollama():
        print("\n🎉 Ollama успешно настроен для AI Girls!")
        print("\n📋 Следующие шаги:")
        print("1. Убедитесь, что в .env файле установлено: USE_OLLAMA=true")
        print("2. Запустите приложение: python run.py")
        print("3. Наслаждайтесь общением с AI персонажами!")
    else:
        print("\n❌ Настройка не завершена. Проверьте ошибки выше.")


if __name__ == "__main__":
    main()
