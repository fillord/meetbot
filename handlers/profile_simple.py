from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize, Location
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database
from utils.keyboards import *
from utils.validators import *
from utils.ai_helper import ai_helper
from config import Config
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("profile"))
async def profile_command(message: Message, db: Database):
    """Обработчик команды /profile"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.name:
        await message.answer(
            "❌ У тебя еще нет анкеты!\n"
            "Создай её сначала:",
            reply_markup=get_main_menu_keyboard(has_profile=False)
        )
        return
    
    await show_user_profile(message, db, user_id, is_own=True)

class ProfileStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_for_location = State()
    waiting_for_bio = State()
    waiting_for_photo = State()
    editing_field = State()

async def finalize_profile_creation(message, state: FSMContext, db: Database):
    """Завершить создание профиля"""
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    
    logger.info(f"Finalizing profile creation for user {user_id}")
    
    # Очищаем состояние
    await state.clear()
    
    # Проверяем, что пользователь существует в базе
    user = await db.get_user(user_id)
    logger.info(f"User exists check: {user is not None}")
    if user:
        logger.info(f"User data: name='{user.name}', age={user.age}, city='{user.city}', gender='{user.gender}', looking_for='{user.looking_for}'")
    
    if not user:
        logger.error(f"User {user_id} not found in database during profile finalization!")
        await message.answer(
            "❌ Ошибка при создании анкеты. Попробуй еще раз.",
            reply_markup=get_main_menu_keyboard(has_profile=False)
        )
        return
    
    # Показываем готовую анкету
    await show_user_profile(message, db, user_id, is_own=True)
    
    await message.answer(
        "🎉 <b>Отлично! Твоя анкета готова!</b>\n\n"
        "Теперь ты можешь:\n"
        "• Посмотреть анкеты других пользователей\n"
        "• Редактировать свою анкету\n"
        "• Добавить еще фотографий\n"
        "• Настроить фильтры поиска",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(has_profile=True)
    )

async def show_user_profile(message: Message, db: Database, user_id: int, is_own: bool = False, edit_message: bool = False):
    """Универсальная функция показа профиля"""
    user = await db.get_user(user_id)
    if not user:
        text = "❌ Анкета не найдена"
        keyboard = get_main_menu_keyboard(has_profile=False)
        await message.answer(text, reply_markup=keyboard)
        return
        
    # Формируем текст анкеты
    gender_emoji = "👨" if user.gender == "male" else "👩"
    looking_emoji = "👨" if user.looking_for == "male" else "👩" if user.looking_for == "female" else "🌈"
    
    text = (
        f"{gender_emoji} <b>{user.name}</b>, {user.age} лет\n"
        f"🏙️ {user.city}\n\n"
        f"📖 <b>О себе:</b>\n{user.bio}\n\n"
        f"❤️ <b>Ищет:</b> {looking_emoji} "
    )
    
    if user.looking_for == "male":
        text += "Парней"
    elif user.looking_for == "female":
        text += "Девушек"
    else:
        text += "Всех"
    
    # Статистика для собственной анкеты
    if is_own:
        text += f"\n\n📊 <b>Статистика:</b>\n"
        text += f"👀 Просмотры: {user.profile_views}\n"
        text += f"❤️ Лайки: {user.likes_received}"
    
    keyboard = get_profile_keyboard(is_own=is_own)

    # Получаем главное фото
    photos = await db.get_user_photos(user_id)
    main_photo = photos[0] if photos else None
    
    logger.info(f"Showing profile for user {user_id}, photos: {len(photos)}")
    
    try:
        if main_photo:
            await message.answer_photo(
                photo=main_photo.file_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                text=f"📷 <i>Фото отсутствует</i>\n\n{text}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Error showing profile: {e}")
        await message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

@router.callback_query(F.data == "my_profile")
async def show_my_profile(callback: CallbackQuery, db: Database):
    """Показать свою анкету"""
    await callback.answer()
    
    user_id = callback.from_user.id
    await show_user_profile(callback.message, db, user_id, is_own=True, edit_message=True)

@router.message(ProfileStates.waiting_for_photo, F.photo)
async def process_photo_input(message: Message, state: FSMContext, db: Database):
    """Обработка добавления фото"""
    user_id = message.from_user.id
    
    logger.info(f"Processing photo input for user {user_id}")
    
    # Получаем фото наилучшего качества
    photo = message.photo[-1]
    
    # Проверяем количество фотографий пользователя
    existing_photos = await db.get_user_photos(user_id)
    logger.info(f"User {user_id} has {len(existing_photos)} existing photos")
    
    if len(existing_photos) >= Config.MAX_PHOTOS_PER_PROFILE:
        await message.answer(
            f"❌ У тебя уже максимальное количество фотографий ({Config.MAX_PHOTOS_PER_PROFILE})"
        )
        # Завершаем создание профиля при достижении лимита
        await finalize_profile_creation(message, state, db)
        return
    
    # Добавляем фото
    is_main = len(existing_photos) == 0  # Первое фото становится главным
    logger.info(f"Adding photo for user {user_id}, is_main: {is_main}")
    
    await db.add_user_photo(
        user_id=user_id,
        file_id=photo.file_id,
        file_unique_id=photo.file_unique_id,
        is_main=is_main
    )
    
    # Подтверждаем добавление фото
    current_count = len(existing_photos) + 1
    max_photos = Config.MAX_PHOTOS_PER_PROFILE
    
    logger.info(f"Photo added for user {user_id}, current count: {current_count}")
    
    if current_count == 1:
        await message.answer(
            f"✅ Главное фото добавлено!\n\n"
            f"📸 У тебя {current_count} из {max_photos} фото\n\n"
            f"Можешь добавить еще фото или завершить создание анкеты:",
            reply_markup=get_photo_add_keyboard()
        )
    elif current_count < max_photos:
        await message.answer(
            f"✅ Фото добавлено!\n\n"
            f"📸 У тебя {current_count} из {max_photos} фото\n\n"
            f"Можешь добавить еще фото или завершить создание анкеты:",
            reply_markup=get_photo_add_keyboard()
        )
    else:
        # Достигнут лимит фото - завершаем создание профиля
        await message.answer(f"✅ Фото добавлено! Достигнут лимит ({max_photos} фото)")
        await finalize_profile_creation(message, state, db)

@router.message(ProfileStates.waiting_for_photo)
async def process_invalid_photo(message: Message):
    """Обработка неправильного типа сообщения при ожидании фото"""
    await message.answer(
        "❌ Пожалуйста, пришли фотографию",
        reply_markup=get_photo_add_keyboard()
    )

@router.callback_query(F.data == "add_more_photo", ProfileStates.waiting_for_photo)
async def continue_adding_photos(callback: CallbackQuery):
    """Продолжить добавление фотографий"""
    await callback.answer()
    await callback.message.edit_text(
        "📸 <b>Добавь еще фото</b>\n\n"
        "Пришли следующую фотографию для твоей анкеты.",
        parse_mode="HTML",
        reply_markup=get_photo_add_keyboard()
    )

@router.callback_query(F.data == "finish_profile", ProfileStates.waiting_for_photo)
async def finish_profile_creation(callback: CallbackQuery, state: FSMContext, db: Database):
    """Завершить создание профиля"""
    await callback.answer()
    logger.info(f"Finish profile button clicked by user {callback.from_user.id}")
    await finalize_profile_creation(callback.message, state, db)
