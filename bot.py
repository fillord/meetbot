import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import Config
from database import Database
from handlers import register_all_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_bot_commands(bot: Bot):
    """Настройка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Начать знакомство"),
        BotCommand(command="profile", description="👤 Моя анкета"),
        BotCommand(command="search", description="👀 Смотреть анкеты"),
        BotCommand(command="settings", description="⚙️ Настройки"),
        BotCommand(command="help", description="❓ Помощь"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Команды бота настроены")

async def on_startup(bot: Bot, db: Database):
    """Действия при запуске бота"""
    await db.init_db()
    await setup_bot_commands(bot)
    logger.info("Бот запущен и готов к работе!")

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Бот остановлен")

async def main():
    """Главная функция запуска бота"""
    # Проверяем наличие токена
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создаем экземпляры бота и диспетчера
    bot = Bot(token=Config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Создаем экземпляр базы данных
    db = Database(Config.DATABASE_URL)
    
    # Регистрируем middleware для передачи db в хендлеры
    from aiogram import BaseMiddleware
    from typing import Callable, Dict, Any, Awaitable
    from aiogram.types import TelegramObject
    
    class DatabaseMiddleware(BaseMiddleware):
        def __init__(self, db: Database):
            self.db = db
        
        async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
        ) -> Any:
            data['db'] = self.db
            return await handler(event, data)
    
    # Регистрируем middleware
    db_middleware = DatabaseMiddleware(db)
    dp.message.middleware(db_middleware)
    dp.callback_query.middleware(db_middleware)
    
    # Регистрируем обработчики
    register_all_handlers(dp)
    
    # Добавляем обработчики команд
    from aiogram import Router
    from aiogram.types import Message
    from aiogram.filters import Command
    from utils.keyboards import get_main_menu_keyboard
    
    commands_router = Router()
    
    @commands_router.message(Command("profile"))
    async def profile_command(message: Message, db: Database):
        """Команда /profile"""
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if user and user.name and user.age and user.gender:
            from handlers.profile import show_user_profile
            await show_user_profile(message, db, user_id, is_own=True)
        else:
            await message.answer(
                "❌ У тебя еще нет анкеты!\n\nСоздай ее с помощью /start",
                reply_markup=get_main_menu_keyboard(has_profile=False)
            )
    
    @commands_router.message(Command("search"))
    async def search_command(message: Message, db: Database):
        """Команда /search"""
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if user and user.name and user.age and user.gender:
            from handlers.swipe import show_next_profile
            await message.answer("🔍 Ищу интересных людей для тебя...")
            await show_next_profile(message, db, user_id)
        else:
            await message.answer(
                "❌ Сначала создай анкету с помощью /start",
                reply_markup=get_main_menu_keyboard(has_profile=False)
            )
    
    @commands_router.message(Command("settings"))
    async def settings_command(message: Message, db: Database):
        """Команда /settings"""
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if not user or not user.name:
            await message.answer(
                "❌ Сначала создай анкету с помощью /start",
                reply_markup=get_main_menu_keyboard(has_profile=False)
            )
            return
        
        settings_text = (
            "⚙️ <b>Настройки</b>\n\n"
            "Настрой параметры поиска под себя:\n\n"
            "🎯 <b>Возрастной диапазон</b> - выбери подходящий возраст\n"
            "📍 <b>Радиус поиска</b> - расстояние для поиска людей\n"
            "🔔 <b>Уведомления</b> - управляй оповещениями\n\n"
            "Выбери что хочешь настроить:"
        )
        
        from utils.keyboards import get_settings_keyboard
        await message.answer(
            settings_text,
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )
    
    @commands_router.message(Command("help"))
    async def help_command(message: Message):
        """Команда /help"""
        help_text = (
            "❓ <b>Помощь по боту Meet Bot</b>\n\n"
            "<b>Команды:</b>\n"
            "/start - Начать знакомство\n"
            "/profile - Моя анкета\n"
            "/search - Смотреть анкеты\n"
            "/settings - Настройки\n"
            "/help - Эта справка\n\n"
            "<b>Как пользоваться:</b>\n"
            "1. Создай анкету с фото и описанием\n"
            "2. Смотри анкеты других пользователей\n"
            "3. Ставь лайки понравившимся людям\n"
            "4. При взаимной симпатии открывается чат!\n\n"
            "<b>Возможности:</b>\n"
            "• 📸 До 5 фотографий в анкете\n"
            "• 🤖 AI-помощник для улучшения описания\n"
            "• 🔍 Фильтры по возрасту и расстоянию\n"
            "• 📊 Статистика просмотров и лайков\n\n"
            "По вопросам: @support_username"
        )
        
        await message.answer(
            help_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(has_profile=True)
        )
    
    dp.include_router(commands_router)
    
    # Запускаем бота
    try:
        await on_startup(bot, db)
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await on_shutdown()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
