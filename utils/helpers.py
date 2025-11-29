"""Вспомогательные функции."""
from typing import Optional
from aiogram.types import User


def format_user_info(user: User) -> tuple[str, str]:
    """Форматирует информацию о пользователе."""
    username = f"@{user.username}" if user.username else f"ID{user.id}"
    full_name = user.full_name or "—"
    return username, full_name


def format_question_message(user_id: int, question: str, username: str, 
                           full_name: str) -> str:
    """Форматирует сообщение с вопросом для админа."""
    return (
        f"📩 Новый вопрос!\n"
        f"👤 {username} ({full_name})\n"
        f"🆔 {user_id}\n\n"
        f"{question}"
    )


def format_answer_message(answer: str) -> str:
    """Форматирует сообщение с ответом для пользователя."""
    return f"📬 **Ответ от поддержки Usupovo Life Hall:**\n\n{answer}"

