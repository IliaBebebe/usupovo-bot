"""Главный файл Telegram бота Usupovo Life Hall."""
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import config
from handlers import common, support, admin


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Выполняется при запуске бота."""
    url = config.webhook_url
    await bot.set_webhook(url)
    logger.info(f"✅ Webhook установлен на {url}")


async def on_shutdown(bot: Bot) -> None:
    """Выполняется при остановке бота."""
    await bot.delete_webhook()
    logger.info("🛑 Webhook удален, бот остановлен")


def setup_handlers(dp: Dispatcher) -> None:
    """Регистрирует все обработчики."""
    # Общие команды
    dp.message.register(common.cmd_start, Command("start"))
    dp.message.register(common.cmd_help, Command("help"))
    
    # Обработчики кнопок меню
    dp.message.register(common.info_handler, F.text.in_({"📅 Расписание", "🎫 Купить билеты"}))
    dp.message.register(support.support_handler, F.text == "📞 Поддержка")
    dp.message.register(admin.stats_button_handler, F.text == "📊 Статистика")
    
    # Админские команды
    dp.message.register(admin.cmd_stats, Command("stats"))
    dp.message.register(admin.cmd_questions, Command("questions"))
    
    # Обработка вопросов и ответов
    # Сначала проверяем, не админ ли это (для ответов на вопросы)
    dp.message.register(
        support.handle_admin_reply,
        F.from_user.id == config.ADMIN_ID,
        F.text
    )
    # Затем обрабатываем вопросы от обычных пользователей (не админов)
    dp.message.register(
        support.handle_user_question,
        F.from_user.id != config.ADMIN_ID,
        F.text
    )
    
    # Callback обработчики
    dp.callback_query.register(
        support.answer_callback,
        F.data.startswith("ans_") | F.data.startswith("close_")
    )


def main() -> None:
    """Главная функция запуска бота."""
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрируем обработчики
    setup_handlers(dp)
    
    # Регистрируем startup и shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Настройка webhook сервера
    app = web.Application()
    
    # Health check endpoint
    app.router.add_get(
        "/",
        lambda _: web.Response(text="✅ Usupovo Bot is running!")
    )
    
    # Webhook endpoint
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path=config.webhook_path)
    setup_application(app, dp, bot=bot)
    
    logger.info(f"🚀 Бот запускается на {config.WEB_SERVER_HOST}:{config.WEB_SERVER_PORT}")
    
    # Запуск сервера
    web.run_app(
        app,
        host=config.WEB_SERVER_HOST,
        port=config.WEB_SERVER_PORT
    )


if __name__ == "__main__":
    main()
