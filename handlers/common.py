"""Обработчики общих команд."""
from aiogram import types, F
from aiogram.filters import Command
from config import config
from utils.keyboards import get_user_menu
from utils.helpers import format_user_info


async def cmd_start(message: types.Message) -> None:
    """Обработчик команды /start."""
    is_admin = message.from_user.id == config.ADMIN_ID
    greeting = "🎭 Админка" if is_admin else "🎭 Добро пожаловать в Usupovo Life Hall!"
    
    await message.answer(
        greeting,
        reply_markup=get_user_menu(is_admin=is_admin)
    )


async def cmd_help(message: types.Message) -> None:
    """Обработчик команды /help."""
    help_text = (
        "📖 **Доступные команды:**\n\n"
        "• /start - Главное меню\n"
        "• /help - Справка\n"
        "• 📅 Расписание - Посмотреть расписание мероприятий\n"
        "• 🎫 Купить билеты - Перейти к покупке билетов\n"
        "• 📞 Поддержка - Задать вопрос\n\n"
        "💡 Используйте кнопки меню для навигации."
    )
    
    await message.answer(help_text, parse_mode="Markdown")


async def info_handler(message: types.Message) -> None:
    """Обработчик кнопок 'Расписание' и 'Купить билеты'."""
    if "Расписание" in message.text:
        text = f"📆 Расписание мероприятий:\n{config.WEBSITE_URL}"
    else:
        text = f"🎟️ Купить билеты:\n{config.WEBSITE_URL}"
    
    await message.answer(text)

