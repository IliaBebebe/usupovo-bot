"""Утилиты для создания клавиатур."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import config


def get_user_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Создает главное меню для пользователя."""
    if is_admin:
        keyboard = [
            [KeyboardButton(text="📅 Расписание")],
            [KeyboardButton(text="🎫 Купить билеты")],
            [KeyboardButton(text="📊 Статистика")]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="📅 Расписание")],
            [KeyboardButton(text="🎫 Купить билеты")],
            [KeyboardButton(text="📞 Поддержка")]
        ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_admin_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Создает inline клавиатуру для ответа на вопрос."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Ответить", callback_data=f"ans_{user_id}")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data=f"close_{user_id}")]
        ]
    )


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой 'Назад'."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )

