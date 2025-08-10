from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import aiosqlite
from database import Database
from utils.keyboards import (
    get_main_menu_keyboard, 
    get_main_menu_keyboard_with_likes, 
    get_gender_keyboard,
    get_main_menu_reply_keyboard,
    get_main_menu_reply_keyboard_with_likes
)
from utils.profile_utils import is_profile_complete
from utils.message_utils import safe_edit_message, safe_answer_message
from config import Config

router = Router()

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext, db: Database):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    # Обновляем данные пользователя
    await db.create_or_update_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Проверяем, есть ли анкета у пользователя
    user = await db.get_user(user_id)
    
    if not user or not user.name or not user.age or not user.gender:
        # Если анкеты нет, предлагаем создать
        await message.answer(
            "🌟 <b>Добро пожаловать в Meet Bot!</b>\n\n"
            "Я помогу тебе найти интересных людей для знакомства!\n\n"
            "Для начала давай создадим твою анкету. "
            "Это займет всего пару минут ✨",
            parse_mode="HTML",
            reply_markup=get_main_menu_reply_keyboard(has_profile=False)
        )
    else:
        # Если анкета уже есть
        keyboard = await get_main_menu_reply_keyboard_with_likes(db, user_id, has_profile=True)
        await message.answer(
            f"🎉 С возвращением, {user.name}!\n\n"
            "Что будем делать?",
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.callback_query(F.data == "create_profile")
async def start_profile_creation(callback: CallbackQuery, state: FSMContext):
    """Начало создания анкеты"""
    await callback.answer()
    
    # Очищаем состояние перед началом создания профиля
    await state.clear()
    
    await safe_edit_message(
        callback.message,
        text="🎭 <b>Создание анкеты</b>\n\n"
             "Сначала выбери свой пол:",
        reply_markup=get_gender_keyboard()
    )

@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext, db: Database):
    """Показать главное меню"""
    await callback.answer()
    
    # Очищаем состояние FSM при возврате в главное меню
    await state.clear()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    has_profile = is_profile_complete(user)
    
    if has_profile:
        text = f"🏠 <b>Главное меню</b>\n\nПривет, {user.name}! Что будем делать?"
        keyboard = await get_main_menu_reply_keyboard_with_likes(db, user_id, has_profile=True)
    else:
        text = "🏠 <b>Главное меню</b>\n\nДля начала создай свою анкету!"
        keyboard = get_main_menu_reply_keyboard(has_profile=False)
    
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML"
        )
        # Отправляем reply клавиатуру отдельным сообщением
        await callback.message.answer(
            "Выбери действие из меню ниже:",
            reply_markup=keyboard
        )
    except:
        # Если не удалось редактировать (например, сообщение с фото), удаляем и отправляем новое
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.callback_query(F.data == "statistics")
async def show_statistics(callback: CallbackQuery, db: Database):
    """Показать статистику пользователя"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await safe_edit_message(
            callback.message,
            text="❌ Сначала создайте анкету!",
            reply_markup=get_main_menu_keyboard(has_profile=False)
        )
        return
    
    # Получаем расширенную статистику
    stats = await db.get_user_statistics(user_id)
    
    if not stats:
        await safe_edit_message(
            callback.message,
            text="❌ Ошибка получения статистики",
            reply_markup=get_main_menu_keyboard(has_profile=True)
        )
        return
    
    # Форматируем даты
    from datetime import datetime
    
    created_at = stats['created_at']
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except:
            created_at = datetime.now()
    
    last_active = stats['last_active']
    if isinstance(last_active, str):
        try:
            last_active = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
        except:
            last_active = datetime.now()
    
    # Определяем статус активности
    activity_emoji = "🟢" if (datetime.now() - last_active).days < 1 else "🟡" if (datetime.now() - last_active).days < 7 else "🔴"
    
    stats_text = (
        f"📊 <b>Твоя статистика</b>\n\n"
        
        f"<b>👀 Просмотры и популярность:</b>\n"
        f"• Просмотры анкеты: {stats['profile_views']} 👁️\n"
        f"• Фотографий в анкете: {stats['photo_count']}/5 📸\n\n"
        
        f"<b>💌 Активность в лайках:</b>\n"
        f"• Всего отправлено: {stats['likes_sent']} ➡️\n"
        f"• Сегодня отправлено: {stats['today_likes']} 🔥\n"
        f"• Получено лайков: {stats['likes_received']} ⬅️\n"
        f"• За последнюю неделю: {stats['week_incoming']} 📈\n\n"
        
        f"<b>� Успешность знакомств:</b>\n"
        f"• Взаимных симпатий: {stats['matches_count']} 💝\n"
        f"• Активных чатов: {stats['active_matches']} 💬\n"
        f"• Успешность лайков: {stats['success_rate']}% 🎯\n\n"
        
        f"<b>📅 Информация об аккаунте:</b>\n"
        f"• Дата регистрации: {created_at.strftime('%d.%m.%Y')} 📅\n"
        f"• Последняя активность: {last_active.strftime('%d.%m.%Y %H:%M')} {activity_emoji}\n\n"
        
        f"<i>Совет: Обновляй фото и описание для большей популярности! ✨</i>"
    )
    
    from utils.keyboards import get_statistics_keyboard
    await safe_edit_message(
        callback.message,
        text=stats_text,
        reply_markup=get_statistics_keyboard()
    )

@router.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    """Показать информацию о боте"""
    await callback.answer()
    
    about_text = (
        "ℹ️ <b>О боте Meet Bot</b>\n\n"
        "🤖 Современный бот для знакомств с AI-возможностями\n\n"
        "<b>Возможности:</b>\n"
        "• 📝 Создание детальных анкет\n"
        "• 👀 Просмотр анкет других пользователей\n"
        "• 💌 Система лайков и матчей\n"
        "• � Просмотр входящих лайков\n"
        "• 🤖 AI-помощник для анкет\n"
        "• 📍 Поиск по геолокации\n"
        "• 🎨 До 5 фото в анкете\n\n"
        "Сделано с ❤️ для новых знакомств!"
    )
    
    from utils.keyboards import get_back_to_menu_keyboard
    await safe_edit_message(
        callback.message,
        text=about_text,
        reply_markup=get_back_to_menu_keyboard()
    )

@router.callback_query(F.data == "top_users")
async def show_top_users(callback: CallbackQuery, db: Database):
    """Показать топ пользователей"""
    await callback.answer()
    
    top_data = await db.get_top_users(limit=5)
    
    text = "🏆 <b>Топ пользователей</b>\n\n"
    
    # Топ по популярности
    if top_data['popular']:
        text += "<b>👑 Самые популярные:</b>\n"
        for i, user in enumerate(top_data['popular'], 1):
            text += f"{i}. {user['name']} - {user['likes_received']} ❤️\n"
        text += "\n"
    
    # Топ по активности
    if top_data['active']:
        text += "<b>🔥 Самые активные:</b>\n"
        for i, user in enumerate(top_data['active'], 1):
            text += f"{i}. {user['name']} - {user['likes_sent']} лайков\n"
        text += "\n"
    
    # Топ по успешности
    if top_data['successful']:
        text += "<b>🎯 Самые успешные:</b>\n"
        for i, user in enumerate(top_data['successful'], 1):
            text += f"{i}. {user['name']} - {user['success_rate']}% успеха\n"
    
    if not any(top_data.values()):
        text += "Пока недостаточно данных для составления рейтинга 📊"
    
    from utils.keyboards import get_back_to_menu_keyboard
    await safe_edit_message(
        callback.message,
        text=text,
        reply_markup=get_back_to_menu_keyboard()
    )

@router.callback_query(F.data == "global_stats")
async def show_global_statistics(callback: CallbackQuery, db: Database):
    """Показать общую статистику бота"""
    await callback.answer()
    
    async with aiosqlite.connect(db.db_path) as database:
        database.row_factory = aiosqlite.Row
        
        # Общее количество пользователей
        cursor = await database.execute('SELECT COUNT(*) as total_users FROM users')
        total_users = (await cursor.fetchone())['total_users']
        
        # Активные пользователи (заходили за последнюю неделю)
        cursor = await database.execute(
            "SELECT COUNT(*) as active_users FROM users WHERE last_active >= datetime('now', '-7 days')"
        )
        active_users = (await cursor.fetchone())['active_users']
        
        # Пользователи с полными анкетами
        cursor = await database.execute(
            'SELECT COUNT(*) as complete_profiles FROM users WHERE name IS NOT NULL AND age IS NOT NULL AND gender IS NOT NULL'
        )
        complete_profiles = (await cursor.fetchone())['complete_profiles']
        
        # Общее количество лайков
        cursor = await database.execute('SELECT COUNT(*) as total_likes FROM swipes WHERE is_like = 1')
        total_likes = (await cursor.fetchone())['total_likes']
        
        # Общее количество матчей
        cursor = await database.execute('SELECT COUNT(*) as total_matches FROM matches')
        total_matches = (await cursor.fetchone())['total_matches']
        
        # Средний возраст пользователей
        cursor = await database.execute('SELECT AVG(age) as avg_age FROM users WHERE age IS NOT NULL')
        avg_age_result = await cursor.fetchone()
        avg_age = round(avg_age_result['avg_age'], 1) if avg_age_result['avg_age'] else 0
        
        # Активность сегодня
        cursor = await database.execute(
            "SELECT COUNT(*) as today_likes FROM swipes WHERE is_like = 1 AND date(created_at) = date('now')"
        )
        today_likes = (await cursor.fetchone())['today_likes']
    
    # Процент успешности (матчи от лайков)
    match_rate = round((total_matches / total_likes * 100), 1) if total_likes > 0 else 0
    
    # Процент активных пользователей
    activity_rate = round((active_users / total_users * 100), 1) if total_users > 0 else 0
    
    global_stats_text = (
        f"📊 <b>Общая статистика бота</b>\n\n"
        
        f"<b>👥 Пользователи:</b>\n"
        f"• Всего зарегистрировано: {total_users} 👤\n"
        f"• Активных за неделю: {active_users} ({activity_rate}%) 🟢\n"
        f"• С полными анкетами: {complete_profiles} ✅\n"
        f"• Средний возраст: {avg_age} лет 📊\n\n"
        
        f"<b>💌 Активность:</b>\n"
        f"• Всего лайков: {total_likes} ❤️\n"
        f"• Лайков сегодня: {today_likes} 🔥\n"
        f"• Успешных матчей: {total_matches} 💕\n"
        f"• Процент совпадений: {match_rate}% 🎯\n\n"
        
        f"<i>Статистика обновляется в реальном времени ⚡</i>"
    )
    
    from utils.keyboards import get_back_to_menu_keyboard
    await safe_edit_message(
        callback.message,
        text=global_stats_text,
        reply_markup=get_back_to_menu_keyboard()
    )

@router.callback_query(F.data == "profile_recommendations")
async def show_profile_recommendations(callback: CallbackQuery, db: Database):
    """Показать рекомендации по улучшению профиля"""
    await callback.answer()
    
    user_id = callback.from_user.id
    recommendations_data = await db.get_profile_recommendations(user_id)
    
    if not recommendations_data:
        await safe_edit_message(
            callback.message,
            text="❌ Сначала создайте анкету!",
            reply_markup=get_main_menu_keyboard(has_profile=False)
        )
        return
    
    text = "💡 <b>Рекомендации для твоего профиля</b>\n\n"
    
    # Текущие показатели
    text += f"<b>📈 Твои показатели:</b>\n"
    text += f"• Фотографий: {recommendations_data['photo_count']}/5 📸\n"
    text += f"• Длина описания: {recommendations_data['bio_length']} символов ✍️\n"
    text += f"• Просмотры: {recommendations_data['profile_views']} (средн: {recommendations_data['avg_views']}) 👀\n"
    text += f"• Успешность лайков: {recommendations_data['success_rate']}% 🎯\n\n"
    
    # Рекомендации
    if recommendations_data['recommendations']:
        text += "<b>🚀 Что можно улучшить:</b>\n"
        for i, rec in enumerate(recommendations_data['recommendations'], 1):
            text += f"{i}. {rec}\n"
        text += "\n"
    else:
        text += "🎉 <b>Отличная анкета!</b>\nВсе основные рекомендации выполнены. Продолжай быть активным!\n\n"
    
    text += "<i>💡 Совет: регулярно обновляй фото и описание для лучших результатов!</i>"
    
    from utils.keyboards import get_back_to_menu_keyboard
    await safe_edit_message(
        callback.message,
        text=text,
        reply_markup=get_back_to_menu_keyboard()
    )

# ======== ОБРАБОТЧИКИ REPLY СООБЩЕНИЙ ========

@router.message(F.text == "📝 Создать анкету")
async def handle_create_profile_reply(message: Message, state: FSMContext):
    """Обработчик reply кнопки 'Создать анкету'"""
    # Очищаем состояние перед началом создания профиля
    await state.clear()
    
    await message.answer(
        "🎭 <b>Создание анкеты</b>\n\n"
        "Сначала выбери свой пол:",
        parse_mode="HTML",
        reply_markup=get_gender_keyboard()
    )

@router.message(F.text == "👀 Смотреть анкеты")
async def handle_start_swiping_reply(message: Message, db: Database):
    """Обработчик reply кнопки 'Смотреть анкеты'"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.name:
        await message.answer(
            "❌ У тебя еще нет анкеты!\n"
            "Создай её сначала:",
            reply_markup=get_main_menu_reply_keyboard(has_profile=False)
        )
        return
    
    # Показываем первую анкету для свайпинга
    from handlers.swipe import show_next_profile
    await show_next_profile(message, db, user_id)

@router.message(F.text.in_(["💌 Лайки", "💌 Лайки (1)", "💌 Лайки (2)", "💌 Лайки (3)", "💌 Лайки (4)", "💌 Лайки (5)", "💌 Лайки (6)", "💌 Лайки (7)", "💌 Лайки (8)", "💌 Лайки (9)"]))
async def handle_my_chats_reply(message: Message, db: Database):
    """Обработчик reply кнопки 'Лайки'"""
    user_id = message.from_user.id
    incoming_likes = await db.get_incoming_likes(user_id)
    
    if not incoming_likes:
        await message.answer(
            "💕 <b>Входящие лайки</b>\n\n"
            "У тебя пока нет новых лайков!\n"
            "Попробуй улучшить свою анкету или посмотри других пользователей 👀",
            parse_mode="HTML"
        )
        return
    
    # Показываем первый лайк
    from handlers.chat import show_like_profile
    await show_like_profile(message, db, user_id, 0)

@router.message(F.text == "📝 Моя анкета")
async def handle_my_profile_reply(message: Message, db: Database):
    """Обработчик reply кнопки 'Моя анкета'"""
    from handlers.profile import profile_command
    await profile_command(message, db)

@router.message(F.text == "⚙️ Настройки")
async def handle_settings_reply(message: Message, db: Database):
    """Обработчик reply кнопки 'Настройки'"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.name:
        await message.answer(
            "❌ У тебя еще нет анкеты!\n"
            "Создай её сначала:",
            reply_markup=get_main_menu_reply_keyboard(has_profile=False)
        )
        return
    
    # Показываем настройки
    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"🎯 <b>Возрастной диапазон:</b> {user.min_age}-{user.max_age} лет\n"
        f"📍 <b>Радиус поиска:</b> {user.search_radius} км\n"
        f"👁️ <b>Показывать возраст:</b> {'Да' if user.show_age else 'Нет'}\n"
        f"🏙️ <b>Показывать город:</b> {'Да' if user.show_location else 'Нет'}\n"
        f"🔔 <b>Уведомления:</b> {'Включены' if user.notifications_enabled else 'Выключены'}"
    )
    
    from utils.keyboards import get_settings_keyboard
    await message.answer(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard()
    )

@router.message(F.text == "📊 Статистика")
async def handle_statistics_reply(message: Message, db: Database):
    """Обработчик reply кнопки 'Статистика'"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await message.answer(
            "❌ Сначала создайте анкету!",
            reply_markup=get_main_menu_reply_keyboard(has_profile=False)
        )
        return
    
    # Получаем расширенную статистику
    stats = await db.get_user_statistics(user_id)
    
    if not stats:
        await message.answer(
            "❌ Ошибка получения статистики"
        )
        return
    
    # Форматируем даты
    from datetime import datetime
    
    created_at = stats['created_at']
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except:
            created_at = datetime.now()
    
    last_active = stats['last_active']
    if isinstance(last_active, str):
        try:
            last_active = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
        except:
            last_active = datetime.now()
    
    # Определяем статус активности
    activity_emoji = "🟢" if (datetime.now() - last_active).days < 1 else "🟡" if (datetime.now() - last_active).days < 7 else "🔴"
    
    stats_text = (
        f"📊 <b>Твоя статистика</b>\n\n"
        
        f"<b>👀 Просмотры и популярность:</b>\n"
        f"• Просмотры анкеты: {stats['profile_views']} 👁️\n"
        f"• Фотографий в анкете: {stats['photo_count']}/5 📸\n\n"
        
        f"<b>💌 Активность в лайках:</b>\n"
        f"• Всего отправлено: {stats['likes_sent']} ➡️\n"
        f"• Сегодня отправлено: {stats['today_likes']} 🔥\n"
        f"• Получено лайков: {stats['likes_received']} ⬅️\n"
        f"• За последнюю неделю: {stats['week_incoming']} 📈\n\n"
        
        f"<b>💝 Успешность знакомств:</b>\n"
        f"• Взаимных симпатий: {stats['matches_count']} 💝\n"
        f"• Активных чатов: {stats['active_matches']} 💬\n"
        f"• Успешность лайков: {stats['success_rate']}% 🎯\n\n"
        
        f"<b>📅 Информация об аккаунте:</b>\n"
        f"• Дата регистрации: {created_at.strftime('%d.%m.%Y')} 📅\n"
        f"• Последняя активность: {last_active.strftime('%d.%m.%Y %H:%M')} {activity_emoji}\n\n"
        
        f"<i>Совет: Обновляй фото и описание для большей популярности! ✨</i>"
    )
    
    from utils.keyboards import get_statistics_keyboard
    await message.answer(
        stats_text, 
        parse_mode="HTML",
        reply_markup=get_statistics_keyboard()
    )

@router.message(F.text == "ℹ️ О боте")
async def handle_about_reply(message: Message):
    """Обработчик reply кнопки 'О боте'"""
    about_text = (
        "ℹ️ <b>О боте Meet Bot</b>\n\n"
        "🤖 Современный бот для знакомств с AI-возможностями\n\n"
        "<b>Возможности:</b>\n"
        "• 📝 Создание детальных анкет\n"
        "• 👀 Просмотр анкет других пользователей\n"
        "• 💌 Система лайков и матчей\n"
        "• 💌 Просмотр входящих лайков\n"
        "• 🤖 AI-помощник для анкет\n"
        "• 📍 Поиск по геолокации\n"
        "• 🎨 До 5 фото в анкете\n\n"
        "Сделано с ❤️ для новых знакомств!"
    )
    
    await message.answer(about_text, parse_mode="HTML")

@router.message(F.text == "🔙 В меню")
async def handle_back_to_menu_reply(message: Message, state: FSMContext, db: Database):
    """Обработчик reply кнопки 'В меню'"""
    # Очищаем состояние FSM при возврате в главное меню
    await state.clear()
    
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    has_profile = is_profile_complete(user)
    
    if has_profile:
        text = f"🏠 <b>Главное меню</b>\n\nПривет, {user.name}! Что будем делать?"
        keyboard = await get_main_menu_reply_keyboard_with_likes(db, user_id, has_profile=True)
    else:
        text = "🏠 <b>Главное меню</b>\n\nДля начала создай свою анкету!"
        keyboard = get_main_menu_reply_keyboard(has_profile=False)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

def register_start_handlers(dp):
    """Регистрация обработчиков старта"""
    dp.include_router(router)
