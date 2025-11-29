"""Обработчики системы поддержки."""
import logging
from aiogram import types, F
from aiogram.filters import Command
from config import config
from database import db
from utils.keyboards import get_admin_inline_keyboard
from utils.helpers import format_user_info, format_question_message, format_answer_message


async def support_handler(message: types.Message) -> None:
    """Обработчик кнопки 'Поддержка'."""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("💬 Напишите ваш вопрос, и мы обязательно ответим!")


async def handle_user_question(message: types.Message) -> None:
    """Обработчик вопроса от пользователя."""
    user = message.from_user
    
    # Пропускаем команды и кнопки меню
    if message.text in ["📅 Расписание", "🎫 Купить билеты", "📞 Поддержка", "📊 Статистика"]:
        return
    
    # Сохраняем вопрос
    username, full_name = format_user_info(user)
    db.add_question(
        user_id=user.id,
        question=message.text,
        username=username,
        full_name=full_name
    )
    
    await message.answer("✅ Ваш вопрос принят! Ожидайте ответа от нашей поддержки.")
    
    # Отправляем уведомление админу
    question_msg = format_question_message(
        user_id=user.id,
        question=message.text,
        username=username,
        full_name=full_name
    )
    
    await message.bot.send_message(
        config.ADMIN_ID,
        question_msg,
        reply_markup=get_admin_inline_keyboard(user.id)
    )


async def handle_admin_reply(message: types.Message) -> None:
    """Обработчик ответа админа на вопрос."""
    # Пропускаем команды и кнопки меню
    if message.text in ["📅 Расписание", "🎫 Купить билеты", "📞 Поддержка", "📊 Статистика"]:
        return
    
    # Проверяем, есть ли вопрос, на который админ готов ответить
    ready = db.get_ready_to_reply()
    
    if not ready:
        # Если админ пишет что-то, но нет готового вопроса, игнорируем
        return
    
    target_id, question_data = ready
    
    try:
        # Отправляем ответ пользователю
        answer_text = format_answer_message(message.text)
        await message.bot.send_message(
            target_id,
            answer_text,
            parse_mode="Markdown"
        )
        
        # Помечаем как отвеченный и удаляем
        db.mark_answered(target_id)
        db.delete_question(target_id)
        
        await message.answer(f"✅ Ответ отправлен пользователю (ID: {target_id})!")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка отправки ответа: {e}", exc_info=True)
        await message.answer(f"❌ Ошибка отправки: {e}")
        db.delete_question(target_id)


async def answer_callback(callback: types.CallbackQuery) -> None:
    """Обработчик callback для ответа на вопрос."""
    if callback.from_user.id != config.ADMIN_ID:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    try:
        action, user_id_str = callback.data.split("_", 1)
        target_id = int(user_id_str)
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка обработки", show_alert=True)
        return
    
    question_data = db.get_question(target_id)
    
    if not question_data:
        await callback.message.edit_text("❌ Вопрос не найден или уже удален.")
        await callback.answer()
        return
    
    if action == "ans":
        # Помечаем, что админ готов ответить
        db.set_admin_ready(target_id)
        await callback.message.answer(
            f"✏️ Введите ответ для пользователя (ID: {target_id}):\n\n"
            f"Вопрос: {question_data.get('question', 'N/A')}"
        )
        await callback.answer("Готов к ответу")
    
    elif action == "close":
        # Закрываем вопрос без ответа
        db.delete_question(target_id)
        await callback.message.edit_text("❌ Вопрос закрыт без ответа.")
        await callback.answer("Вопрос закрыт")

