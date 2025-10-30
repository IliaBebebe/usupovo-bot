import os
import logging
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 2107059658
QUESTIONS_FILE = "questions.json"

if not BOT_TOKEN:
    raise ValueError("Токен не найден! Проверьте .env")

# Параметры webhook
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8000))
WEBHOOK_SECRET_PATH = os.getenv("WEBHOOK_SECRET_PATH", "a4VlADbUmAGAlucHI4444444reufjrnef444444YBLOgerIZ4VIniteEE44242")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET_PATH}"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://usupovo-bot.onrender.com/").strip()  # ← убран пробел!

def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ошибка загрузки вопросов: {e}")
            return {}
    return {}

def save_questions(data):
    try:
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения вопросов: {e}")

# Загружаем при старте
questions = load_questions()

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
    if "Расписание" in message.text:
        await message.answer("📆 Расписание: https://usupovo-life-hall.onrender.com/")
    else:
        await message.answer("🎟️ Билеты: https://usupovo-life-hall.onrender.com/")

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
                    save_questions(questions)  # ← СОХРАНЯЕМ!
                    await message.answer(f"✅ Ответ отправлен пользователю (ID: {target_id})!")
                    return
                except Exception as e:
                    await message.answer(f"❌ Ошибка: {e}")
                    del questions[target_id]
                    save_questions(questions)  # ← СОХРАНЯЕМ!
                    return
        return

    if text == "📞 Поддержка":
        await message.answer("💬 Напишите ваш вопрос:")
        return

    # Сохраняем новый вопрос
    questions[user.id] = text
    save_questions(questions)  # ← СОХРАНЯЕМ!
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

    # Помечаем, что админ готов ответить
    questions[target_id] = {
        "question": questions[target_id],
        "admin_ready_to_reply": True
    }
    save_questions(questions)  # ← СОХРАНЯЕМ!
    await callback.message.answer(f"✏️ Введите ответ для пользователя (ID: {target_id}):")
    await callback.answer()

async def on_startup(bot: Bot):
    url = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(url)
    logging.info(f"Webhook установлен на {url}")

def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(info_handler, F.text.in_({"📅 Расписание", "🎫 Купить билеты"}))
    dp.message.register(support_handler, F.text == "📞 Поддержка")
    dp.message.register(handle_all_text, F.text)
    dp.callback_query.register(answer_callback, F.data.startswith("ans_"))

    dp.startup.register(on_startup)

    app = web.Application()
    app.router.add_get("/", lambda _: web.Response(text="✅ Usupovo Bot is running!"))  # ← здоровая страница
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
