# bot.py
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 2107059658

if not BOT_TOKEN:
    raise ValueError("Токен не найден! Проверьте .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище вопросов
questions = {}  # {user_id: str или {question: str, admin_ready: True}}

# --- Меню ---
def get_menu(user_id: int):
    if user_id == ADMIN_ID:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📅 Расписание")], [KeyboardButton(text="🎫 Купить билеты")]],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📅 Расписание")],
                [KeyboardButton(text="🎫 Купить билеты")],
                [KeyboardButton(text="📞 Поддержка")]
            ],
            resize_keyboard=True
        )

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎭 Админка" if message.from_user.id == ADMIN_ID else "🎭 Добро пожаловать!",
        reply_markup=get_menu(message.from_user.id)
    )

@dp.message(F.text.in_({"📅 Расписание", "🎫 Купить билеты"}))
async def info(message: types.Message):
    txt = "📆 Расписание: https://usupovo-life-hall.onrender.com/" if "Расписание" in message.text else "🎟️ Билеты: https://usupovo-life-hall.onrender.com/"
    await message.answer(txt)

@dp.message(F.text == "📞 Поддержка")
async def support(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("💬 Напишите ваш вопрос:")

# --- ЕДИНЫЙ ОБРАБОТЧИК ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ ---
@dp.message(F.text)
async def handle_all_text(message: types.Message):
    user = message.from_user
    text = message.text

    # === Случай 1: это админ, и он отвечает на вопрос ===
    if user.id == ADMIN_ID:
        # Ищем, есть ли пользователь, ожидающий ответа
        for target_id, data in questions.items():
            if isinstance(data, dict) and data.get("admin_ready_to_reply"):
                # Отправляем ответ
                try:
                    await bot.send_message(
                        target_id,
                        f"📬 **Ответ от поддержки Usupovo Life Hall:**\n\n{text}",
                        parse_mode="Markdown"
                    )
                    del questions[target_id]
                    await message.answer(f"✅ Ответ отправлен пользователю (ID: {target_id})!")
                    logging.info(f"✅ Ответ доставлен: {target_id} <- '{text}'")
                    return
                except Exception as e:
                    logging.error(f"❌ Ошибка отправки: {e}")
                    await message.answer(f"❌ Не удалось отправить: {e}")
                    del questions[target_id]
                    return

        # Если нет активного ответа — просто логируем
        logging.info(f"Админ написал (не ответ): {text}")
        return

    # === Случай 2: обычный пользователь ===
    if text == "📞 Поддержка":
        await message.answer("💬 Напишите ваш вопрос:")
        return

    # Сохраняем вопрос
    questions[user.id] = text
    await message.answer("✅ Вопрос принят! Ожидайте ответа.")

    # Уведомление админу
    username = f"@{user.username}" if user.username else f"ID{user.id}"
    full_name = user.full_name or "—"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"ans_{user.id}")]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новый вопрос!\n👤 {username} ({full_name})\n🆔 {user.id}\n\n{text}",
        reply_markup=kb
    )

# --- Обработка кнопки "Ответить" ---
@dp.callback_query(F.data.startswith("ans_"))
async def answer_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    try:
        target_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("Ошибка", show_alert=True)
        return

    if target_id not in questions:
        await callback.message.edit_text("❌ Вопрос уже отвечен.")
        return

    # Помечаем, что админ готов ответить
    questions[target_id] = {
        "question": questions[target_id],
        "admin_ready_to_reply": True
    }
    await callback.message.answer(f"✏️ Введите ответ для пользователя (ID: {target_id}):")
    await callback.answer()

WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8000))  # Render даёт PORT
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
BASE_WEBHOOK_URL = "https://ваш-рендер-адрес.onrender.com"  # ← замените позже

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")

def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # ... зарегистрируйте все ваши хэндлеры (как раньше) ...
    dp.message.register(start, Command("start"))
    dp.message.register(handle_all_text, F.text)
    dp.callback_query.register(answer_callback, F.data.startswith("ans_"))
    # ... и т.д.

    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    main()