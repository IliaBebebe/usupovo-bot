"""Обработчики команд администратора."""
from aiogram import types, F
from aiogram.filters import Command
from config import config
from database import db
from utils.keyboards import get_user_menu


async def cmd_stats(message: types.Message) -> None:
    """Обработчик команды /stats и кнопки 'Статистика'."""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ Эта команда доступна только администратору.")
        return
    
    stats = db.get_statistics()
    stats_text = (
        f"📊 **Статистика вопросов:**\n\n"
        f"📝 Всего вопросов: {stats['total']}\n"
        f"⏳ Ожидают ответа: {stats['pending']}\n"
        f"✅ Отвечено: {stats['answered']}"
    )
    
    await message.answer(stats_text, parse_mode="Markdown")


async def cmd_questions(message: types.Message) -> None:
    """Обработчик команды /questions - показывает все неотвеченные вопросы."""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ Эта команда доступна только администратору.")
        return
    
    pending = db.get_pending_questions()
    
    if not pending:
        await message.answer("✅ Нет неотвеченных вопросов!")
        return
    
    questions_text = "📋 **Неотвеченные вопросы:**\n\n"
    
    for user_id_str, data in list(pending.items())[:10]:  # Показываем первые 10
        user_id = int(user_id_str)
        question = data.get("question", "N/A")
        username = data.get("username", f"ID{user_id}")
        created_at = data.get("created_at", "N/A")
        
        questions_text += (
            f"🆔 {user_id} ({username})\n"
            f"❓ {question[:50]}{'...' if len(question) > 50 else ''}\n"
            f"📅 {created_at}\n\n"
        )
    
    if len(pending) > 10:
        questions_text += f"... и еще {len(pending) - 10} вопросов"
    
    await message.answer(questions_text, parse_mode="Markdown")


async def stats_button_handler(message: types.Message) -> None:
    """Обработчик кнопки 'Статистика'."""
    await cmd_stats(message)

