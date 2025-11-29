"""Конфигурация бота."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Класс для хранения конфигурации бота."""
    
    # Токен бота
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # ID администратора (можно указать через переменную окружения)
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "2107059658"))
    
    # Файл с вопросами
    QUESTIONS_FILE: str = "questions.json"
    
    # Параметры webhook
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = int(os.getenv("PORT", "8000"))
    WEBHOOK_SECRET_PATH: str = os.getenv(
        "WEBHOOK_SECRET_PATH", 
        "a4VlADbUmAGAlucHI4444444reufjrnef444444YBLOgerIZ4VIniteEE44242"
    )
    BASE_WEBHOOK_URL: str = os.getenv(
        "WEBHOOK_URL", 
        "https://usupovo-bot.onrender.com"
    ).strip()
    
    # URL сайта
    WEBSITE_URL: str = "https://usupovo-life-hall.onrender.com/"
    
    @property
    def webhook_path(self) -> str:
        """Возвращает путь webhook."""
        return f"/webhook/{self.WEBHOOK_SECRET_PATH}"
    
    @property
    def webhook_url(self) -> str:
        """Возвращает полный URL webhook."""
        return f"{self.BASE_WEBHOOK_URL}{self.webhook_path}"
    
    def validate(self) -> None:
        """Проверяет корректность конфигурации."""
        if not self.BOT_TOKEN:
            raise ValueError("Токен бота не найден! Проверьте переменную окружения BOT_TOKEN")


# Создаем глобальный экземпляр конфигурации
config = Config()
config.validate()

