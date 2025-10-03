# bot.py
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 2107059658

if not BOT_TOKEN:
    raise ValueError("Токен не найден! Проверьте .env")

# Параметры webhook
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8000))  # Render даёт PORT
WEBHOOK_SECRET_PATH = os.getenv("WEBHOOK_SECRET_PATH", "a4VlADbUmAGAlucHI4444444reufjrnef444444YBLOgerIZ4VIniteEE44242")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET_PATH}"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://usupovo-bot.onrender.com")

# Хранилище вопросов (в памяти)
questions = {}

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

async def cmd_start(message: types.Message):
    await message.answer(
        "🎭 Админка" if message.from_user.id == ADMIN_ID else "🎭 Добро пожаловать!",
        reply_markup=get_menu(message.from_user.id)
    )

async def info_handler(message: types.Message):
    txt = "📆 Расписание: https://usupovo-life-hall.onrender.com/" if "Расписание" in message.text else "🎟️ Билеты: https://usupovo-life-hall.onrender.com/"
    await message.answer(txt)

async def support_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("💬 Напишите ваш вопрос:")

async def handle_all_text(message: types.Message):
    user = message.from_user
    text = message.text

    if user.id == ADMIN_ID:
        for target_id, data in questions.items():
            if isinstance(data, dict) and data.get("admin_ready_to_reply"):
                try:
                    await message.bot.send_message(
                        target_id,
                        f"📬 **Ответ от поддержки Usupovo Life Hall:**\n\n{text}",
                        parse_mode="Markdown"
                    )
                    del questions[target_id]
                    await message.answer(f"✅ Ответ отправлен пользователю (ID: {target_id})!")
                    return
                except Exception as e:
                    await message.answer(f"❌ Ошибка: {e}")
                    del questions[target_id]
                    return
        return

    if text == "📞 Поддержка":
        await message.answer("💬 Напишите ваш вопрос:")
        return

    questions[user.id] = text
    await message.answer("✅ Вопрос принят! Ожидайте ответа.")

    username = f"@{user.username}" if user.username else f"ID{user.id}"
    full_name = user.full_name or "—"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"ans_{user.id}")]
    ])
    await message.bot.send_message(
        ADMIN_ID,
        f"📩 Новый вопрос!\n👤 {username} ({full_name})\n🆔 {user.id}\n\n{text}",
        reply_markup=kb
    )

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

    questions[target_id] = {
        "question": questions[target_id],
        "admin_ready_to_reply": True
    }
    await callback.message.answer(f"✏️ Введите ответ для пользователя (ID: {target_id}):")
    await callback.answer()

# Настройка webhook при запуске
async def on_startup(bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")
    logging.info(f"Webhook установлен на {BASE_WEBHOOK_URL}{WEBHOOK_PATH}")

# Запуск веб-сервера
def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация хэндлеров
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(info_handler, F.text.in_({"📅 Расписание", "🎫 Купить билеты"}))
    dp.message.register(support_handler, F.text == "📞 Поддержка")
    dp.message.register(handle_all_text, F.text)
    dp.callback_query.register(answer_callback, F.data.startswith("ans_"))

    dp.startup.register(on_startup)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()