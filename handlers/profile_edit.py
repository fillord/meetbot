from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, Location
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import Database
from utils.keyboards import (
    get_skip_or_keep_keyboard, get_main_menu_keyboard,
    get_gender_keyboard_with_keep, get_looking_for_keyboard_with_keep,
    get_location_keyboard, get_back_to_profile_keyboard, get_edit_profile_keyboard,
    get_profile_keyboard, get_back_to_menu_keyboard
)
from utils.validators import validate_name, validate_age, validate_bio
from utils.ai_helper import ai_helper
from utils.profile_utils import is_profile_complete
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)
router = Router()

class ProfileEditStates(StatesGroup):
    editing_name = State()
    editing_age = State()
    editing_city = State()
    editing_bio = State()
    editing_gender = State()
    editing_looking_for = State()

@router.callback_query(F.data == "edit_profile")
async def show_edit_profile_menu(callback: CallbackQuery):
    """Показать меню редактирования профиля"""
    await callback.answer()
    
    try:
        await callback.message.edit_caption(
            caption="✏️ <b>Редактирование анкеты</b>\n\nЧто хочешь изменить?",
            parse_mode="HTML",
            reply_markup=get_edit_profile_keyboard()
        )
    except Exception as e:
        logger.error(f"Error editing profile menu caption: {e}")
        try:
            await callback.message.edit_text(
                "✏️ <b>Редактирование анкеты</b>\n\nЧто хочешь изменить?",
                parse_mode="HTML",
                reply_markup=get_edit_profile_keyboard()
            )
        except Exception as e2:
            logger.error(f"Error editing profile menu text: {e2}")
            await callback.message.answer(
                "✏️ <b>Редактирование анкеты</b>\n\nЧто хочешь изменить?",
                parse_mode="HTML",
                reply_markup=get_edit_profile_keyboard()
            )

@router.callback_query(F.data == "set_location")
async def start_location_update(callback: CallbackQuery, state: FSMContext, db: Database):
    """Начать обновление геолокации"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    current_city = user.city if user and user.city and str(user.city).strip() else "Не указан"
    has_location = user and user.latitude and user.longitude
    
    # Устанавливаем состояние ожидания геолокации
    await state.set_state(ProfileEditStates.editing_city)
    
    text = f"📍 <b>Обновление местоположения</b>\n\n"
    text += f"Текущий город: <i>{current_city}</i>\n"
    if has_location:
        text += f"Координаты: ✅ Сохранены\n\n"
    else:
        text += f"Координаты: ❌ Не указаны\n\n"
    
    text += "Отправь свою геолокацию для более точного поиска людей рядом с тобой.\n"
    text += "Мы автоматически определим твой город по координатам.\n\n"
    text += "👇 Нажми кнопку ниже для отправки геолокации:"
    
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML"
        )
        # Отправляем клавиатуру с геолокацией отдельным сообщением
        await callback.message.answer(
            "📍 Выбери способ отправки геолокации:",
            reply_markup=get_location_keyboard()
        )
    except Exception as e:
        logger.error(f"Error editing message for location update: {e}")
        await callback.message.answer(
            text,
            parse_mode="HTML"
        )
        await callback.message.answer(
            "📍 Выбери способ отправки геолокации:",
            reply_markup=get_location_keyboard()
        )

@router.callback_query(F.data == "recreate_profile")
async def start_recreate_profile(callback: CallbackQuery, state: FSMContext, db: Database):
    """Начать перезаполнение анкеты"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    current_name = user.name if user and user.name and str(user.name).strip() else "Не указано"
    has_name = bool(user and user.name and str(user.name).strip())
    
    try:
        await callback.message.edit_text(
            f"✏️ <b>Обновление анкеты</b>\n\n"
            f"Текущее имя: <i>{current_name}</i>\n\n"
            f"Введи новое имя или оставь текущее:",
            parse_mode="HTML",
            reply_markup=get_skip_or_keep_keyboard("name", has_name)
        )
        await state.set_state(ProfileEditStates.editing_name)
    except Exception as e:
        logger.error(f"Error starting profile recreation: {e}")
        await callback.message.answer(
            f"✏️ <b>Обновление анкеты</b>\n\n"
            f"Текущее имя: <i>{current_name}</i>\n\n"
            f"Введи новое имя или оставь текущее:",
            parse_mode="HTML",
            reply_markup=get_skip_or_keep_keyboard("name", has_name)
        )
        await state.set_state(ProfileEditStates.editing_name)

@router.message(ProfileEditStates.editing_name)
async def process_name_edit(message: Message, state: FSMContext, db: Database):
    """Обработка имени"""
    name = message.text.strip()
    
    if not validate_name(name):
        await message.answer(
            "❌ Имя должно содержать от 2 до 30 символов и состоять только из букв.\n"
            "Попробуй еще раз:",
            reply_markup=get_skip_or_keep_keyboard("name", False)
        )
        return
    
    # Сохраняем в state и в базу данных
    await state.update_data(name=name)
    user_id = message.from_user.id
    await db.create_or_update_user(user_id, name=name)
    logger.info(f"Name updated for user {user_id}: {name}")
    
    await ask_for_age(message, state, db)

@router.callback_query(F.data.startswith("skip_") | F.data.startswith("keep_"))
async def handle_skip_or_keep(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработка пропуска или сохранения текущего значения"""
    await callback.answer()
    
    action, field = callback.data.split("_", 1)
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    # Пропуск теперь полностью запрещен - все поля обязательны
    if action == "skip":
        await callback.answer("❌ Это поле обязательно для заполнения", show_alert=True)
        return
    elif action == "keep":
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
            
        # Сохраняем текущее значение, только если оно есть
        current_data = await state.get_data()
        if field == "name":
            if user.name and str(user.name).strip():
                # При нажатии "Оставить как есть" сразу обновляем профиль
                await db.create_or_update_user(user_id, name=user.name)
            else:
                # Если имя пустое, просим его заполнить
                await callback.answer("❌ Имя обязательно для заполнения. Введите новое имя.", show_alert=True)
                return
        elif field == "age":
            if user.age:
                # При нажатии "Оставить как есть" сразу обновляем профиль
                await db.create_or_update_user(user_id, age=user.age)
            else:
                # Если возраст не указан, просим его заполнить
                await callback.answer("❌ Возраст обязателен для заполнения. Введите свой возраст.", show_alert=True)
                return
        elif field == "city":
            # Геолокация теперь обязательна для всех
            await callback.answer("⚠️ Геолокация обязательна для обновления. Отправь свою геолокацию, нажав кнопку ниже.", show_alert=True)
            return
        elif field == "bio":
            # Описание теперь обязательное поле
            logger.info(f"Checking bio for user {user_id}: current bio = '{user.bio}', stripped = '{str(user.bio).strip() if user.bio else None}'")
            if user.bio and str(user.bio).strip():
                # При нажатии "Оставить как есть" сразу обновляем профиль
                await db.create_or_update_user(user_id, bio=user.bio)
                logger.info(f"Bio kept and updated for user {user_id}: '{user.bio}'")
            else:
                # Если описание пустое, просим его заполнить
                logger.warning(f"Bio is empty for user {user_id}, requesting new bio")
                await callback.answer("❌ Описание обязательно для заполнения. Введите описание о себе.", show_alert=True)
                return
        elif field == "gender":
            if user.gender and str(user.gender).strip():
                # При нажатии "Оставить как есть" сразу обновляем профиль
                await db.create_or_update_user(user_id, gender=user.gender)
            else:
                # Если пол не указан, просим его заполнить
                await callback.answer("❌ Пол обязателен для заполнения. Выберите свой пол.", show_alert=True)
                return
        elif field == "looking_for":
            if user.looking_for and str(user.looking_for).strip():
                # При нажатии "Оставить как есть" сразу обновляем профиль
                await db.create_or_update_user(user_id, looking_for=user.looking_for)
            else:
                # Если предпочтения не указаны, просим их заполнить
                await callback.answer("❌ Предпочтения обязательны для заполнения. Выберите кого ищете.", show_alert=True)
                return
    
    # Переходим к следующему шагу
    if field == "name":
        await ask_for_age(callback.message, state, db, user_id)
    elif field == "age":
        await ask_for_city(callback.message, state, db, user_id)
    elif field == "city":
        await ask_for_bio(callback.message, state, db, user_id)
    elif field == "bio":
        await ask_for_gender(callback.message, state, db, user_id)
    elif field == "gender":
        await ask_for_looking_for(callback.message, state, db, user_id)
    elif field == "looking_for":
        await finalize_profile_edit(callback.message, state, db)

@router.callback_query(F.data == "cancel_edit")
async def handle_cancel_edit(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработка отмены редактирования"""
    await callback.answer()
    await state.clear()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    has_complete_profile = is_profile_complete(user)
    
    try:
        await callback.message.edit_text(
            "🔙 <b>Редактирование отменено</b>\n\n"
            "Возвращаемся в главное меню.",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(has_profile=has_complete_profile)
        )
    except Exception:
        await callback.message.answer(
            "🔙 <b>Редактирование отменено</b>\n\n"
            "Возвращаемся в главное меню.",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(has_profile=has_complete_profile)
        )

async def ask_for_age(message, state: FSMContext, db: Database, user_id: int = None):
    """Запросить возраст"""
    if user_id is None:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    user = await db.get_user(user_id)
    
    current_age = str(user.age) if user and user.age else "Не указан"
    has_age = bool(user and user.age)
    
    # Явно устанавливаем состояние
    await state.set_state(ProfileEditStates.editing_age)
    
    try:
        await message.edit_text(
            f"🎂 <b>Возраст</b>\n\n"
            f"Текущий возраст: <i>{current_age}</i>\n\n"
            f"Введи свой возраст (от 18 до 100 лет) или оставь текущий:",
            parse_mode="HTML",
            reply_markup=get_skip_or_keep_keyboard("age", has_age)
        )
    except Exception:
        await message.answer(
            f"🎂 <b>Возраст</b>\n\n"
            f"Текущий возраст: <i>{current_age}</i>\n\n"
            f"Введи свой возраст (от 18 до 100 лет) или оставь текущий:",
            parse_mode="HTML",
            reply_markup=get_skip_or_keep_keyboard("age", has_age)
        )

@router.message(ProfileEditStates.editing_age)
async def process_age_edit(message: Message, state: FSMContext, db: Database):
    """Обработка возраста"""
    try:
        age = int(message.text.strip())
        is_valid, validated_age, error_msg = validate_age(age)
        if not is_valid:
            await message.answer(
                f"❌ {error_msg}\n"
                "Попробуй еще раз:",
                reply_markup=get_skip_or_keep_keyboard("age", False)
            )
            return
        
        # Сохраняем в state и в базу данных
        await state.update_data(age=validated_age)
        user_id = message.from_user.id
        await db.create_or_update_user(user_id, age=validated_age)
        logger.info(f"Age updated for user {user_id}: {validated_age}")
        
        await ask_for_city(message, state, db)
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введи возраст числом.\n"
            "Попробуй еще раз:",
            reply_markup=get_skip_or_keep_keyboard("age", False)
        )

async def ask_for_city(message, state: FSMContext, db: Database, user_id: int = None):
    """Запросить геолокацию для обновления местоположения"""
    if user_id is None:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    user = await db.get_user(user_id)
    
    current_city = user.city if user and user.city and str(user.city).strip() else "Не указан"
    has_location = user and user.latitude and user.longitude
    
    # Устанавливаем состояние ожидания геолокации
    await state.set_state(ProfileEditStates.editing_city)
    
    text = f"📍 <b>Обновление местоположения</b>\n\n"
    text += f"Текущий город: <i>{current_city}</i>\n"
    if has_location:
        text += f"Координаты: ✅ Сохранены\n\n"
    else:
        text += f"Координаты: ❌ Не указаны\n\n"
    
    text += "Отправь свою геолокацию для более точного поиска людей рядом с тобой.\n"
    text += "Мы автоматически определим твой город по координатам.\n\n"
    text += "⚠️ <b>Этот шаг обязателен</b> - нажми кнопку ниже 👇"
    
    try:
        await message.edit_text(
            text,
            parse_mode="HTML"
        )
        # Отправляем клавиатуру с геолокацией отдельным сообщением
        await message.answer(
            "👇 Нажми кнопку ниже для отправки геолокации:",
            reply_markup=get_location_keyboard()
        )
    except Exception:
        await message.answer(
            text,
            parse_mode="HTML"
        )
        await message.answer(
            "👇 Нажми кнопку ниже для отправки геолокации:",
            reply_markup=get_location_keyboard()
        )

async def get_city_from_coordinates(lat: float, lon: float) -> str:
    """Получить название города по координатам через OpenStreetMap Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': 'Meet Bot'}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Извлекаем город из ответа
                    address = data.get('address', {})
                    city = (address.get('city') or 
                           address.get('town') or 
                           address.get('village') or 
                           address.get('municipality') or
                           address.get('county') or
                           'Неизвестный город')
                    
                    return city
                else:
                    return "Неизвестный город"
    except Exception as e:
        logger.error(f"Ошибка при получении города: {e}")
        return "Неизвестный город"

@router.message(ProfileEditStates.editing_city)
async def process_city_edit(message: Message, state: FSMContext, db: Database):
    """Обработка геолокации или текста для города"""
    if message.location:
        # Получили геолокацию
        lat = message.location.latitude
        lon = message.location.longitude
        
        # Получаем город по координатам
        city = await get_city_from_coordinates(lat, lon)
        
        # Сохраняем в state и в базу данных
        await state.update_data(
            city=city,
            latitude=lat,
            longitude=lon
        )
        
        user_id = message.from_user.id
        await db.create_or_update_user(
            user_id, 
            city=city,
            latitude=lat,
            longitude=lon
        )
        logger.info(f"Location updated for user {user_id}: city={city}, lat={lat}, lon={lon}")
        
        # Убираем клавиатуру с геолокацией
        from aiogram.types import ReplyKeyboardRemove
        await message.answer(
            f"✅ Отлично! Определили твой город: <b>{city}</b>\n"
            f"📍 Координаты обновлены для поиска людей рядом",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Переходим к био
        await ask_for_bio(message, state, db)
        
    elif message.text:
        # Получили текст (устаревший способ)
        await message.answer(
            "🔄 Теперь мы используем геолокацию для более точного определения местоположения.\n"
            "Нажми кнопку ниже, чтобы отправить свою геолокацию:",
            reply_markup=get_location_keyboard()
        )
    else:
        await message.answer(
            "❌ Пожалуйста, отправь геолокацию, нажав кнопку ниже 👇",
            reply_markup=get_location_keyboard()
        )

async def ask_for_bio(message, state: FSMContext, db: Database, user_id: int = None):
    """Запросить описание"""
    if user_id is None:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    user = await db.get_user(user_id)
    
    current_bio = user.bio if user and user.bio and str(user.bio).strip() else "Не указано"
    bio_preview = current_bio[:100] + "..." if len(current_bio) > 100 else current_bio
    has_bio = user and user.bio and str(user.bio).strip()
    
    # Явно устанавливаем состояние
    await state.set_state(ProfileEditStates.editing_bio)
    
    try:
        await message.edit_text(
            f"📝 <b>О себе</b>\n\n"
            f"Текущее описание: <i>{bio_preview}</i>\n\n"
            f"Расскажи о себе (от 10 до 500 символов). Это поле обязательно:",
            parse_mode="HTML",
            reply_markup=get_skip_or_keep_keyboard("bio", has_bio)
        )
    except Exception:
        await message.answer(
            f"📝 <b>О себе</b>\n\n"
            f"Текущее описание: <i>{bio_preview}</i>\n\n"
            f"Расскажи о себе (от 10 до 500 символов). Это поле обязательно:",
            parse_mode="HTML",
            reply_markup=get_skip_or_keep_keyboard("bio", has_bio)
        )

@router.message(ProfileEditStates.editing_bio)
async def process_bio_edit(message: Message, state: FSMContext, db: Database):
    """Обработка описания"""
    bio = message.text.strip()
    
    is_valid, validated_bio, error = validate_bio(bio)
    if not is_valid:
        await message.answer(
            f"❌ {error}\n"
            "Попробуй еще раз:",
            reply_markup=get_skip_or_keep_keyboard("bio", False)
        )
        return
    
    # Проверяем контент
    content_check = await ai_helper.check_content_safety(validated_bio)
    if not content_check:
        await message.answer(
            "❌ Описание содержит неподходящий контент.\n"
            "Попробуй написать по-другому:",
            reply_markup=get_skip_or_keep_keyboard("bio", False)
        )
        return
    
    # Сохраняем в базу данных
    user_id = message.from_user.id
    await db.create_or_update_user(user_id, bio=validated_bio)
    logger.info(f"Bio updated for user {user_id}: {validated_bio}")
    
    await ask_for_gender(message, state, db)

async def ask_for_gender(message, state: FSMContext, db: Database, user_id: int = None):
    """Запросить пол"""
    if user_id is None:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    user = await db.get_user(user_id)
    
    current_gender = "Не указан"
    has_gender = False
    if user and user.gender:
        gender_map = {"male": "Мужской", "female": "Женский"}
        current_gender = gender_map.get(user.gender, user.gender)
        has_gender = True
    
    # Явно устанавливаем состояние
    await state.set_state(ProfileEditStates.editing_gender)
    
    try:
        await message.edit_text(
            f"👫 <b>Пол</b>\n\n"
            f"Текущий пол: <i>{current_gender}</i>\n\n"
            f"Укажи свой пол или оставь текущий:",
            parse_mode="HTML",
            reply_markup=get_gender_keyboard_with_keep(has_gender)
        )
    except Exception:
        await message.answer(
            f"👫 <b>Пол</b>\n\n"
            f"Текущий пол: <i>{current_gender}</i>\n\n"
            f"Укажи свой пол или оставь текущий:",
            parse_mode="HTML",
            reply_markup=get_gender_keyboard_with_keep(has_gender)
        )

@router.callback_query(F.data.startswith("gender_"), ProfileEditStates.editing_gender)
async def process_gender_edit(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработка выбора пола"""
    await callback.answer()
    
    user_id = callback.from_user.id
    gender = callback.data.split("_")[1]
    # Сразу сохраняем в базу данных
    await db.create_or_update_user(user_id, gender=gender)
    logger.info(f"Gender updated for user {user_id}: {gender}")
    await ask_for_looking_for(callback.message, state, db, user_id)

async def ask_for_looking_for(message, state: FSMContext, db: Database, user_id: int = None):
    """Запросить предпочтения"""
    if user_id is None:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    user = await db.get_user(user_id)
    
    current_looking_for = "Не указано"
    has_looking_for = False
    if user and user.looking_for:
        looking_for_map = {"male": "Парней", "female": "Девушек", "both": "Всех"}
        current_looking_for = looking_for_map.get(user.looking_for, user.looking_for)
        has_looking_for = True
    
    # Явно устанавливаем состояние
    await state.set_state(ProfileEditStates.editing_looking_for)
    
    try:
        await message.edit_text(
            f"💕 <b>Кого ищешь?</b>\n\n"
            f"Текущие предпочтения: <i>{current_looking_for}</i>\n\n"
            f"Выбери, кто тебе интересен, или оставь текущие предпочтения:",
            parse_mode="HTML",
            reply_markup=get_looking_for_keyboard_with_keep(has_looking_for)
        )
    except Exception:
        await message.answer(
            f"💕 <b>Кого ищешь?</b>\n\n"
            f"Текущие предпочтения: <i>{current_looking_for}</i>\n\n"
            f"Выбери, кто тебе интересен, или оставь текущие предпочтения:",
            parse_mode="HTML",
            reply_markup=get_looking_for_keyboard_with_keep(has_looking_for)
        )

@router.callback_query(F.data.startswith("looking_"), ProfileEditStates.editing_looking_for)
async def process_looking_for_edit(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработка выбора предпочтений"""
    await callback.answer()
    
    user_id = callback.from_user.id
    looking_for = callback.data.split("_")[1]
    # Сразу сохраняем в базу данных
    await db.create_or_update_user(user_id, looking_for=looking_for)
    logger.info(f"Looking for updated for user {user_id}: {looking_for}")
    await finalize_profile_edit(callback.message, state, db)

async def finalize_profile_edit(message, state: FSMContext, db: Database):
    """Завершить редактирование профиля"""
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    
    logger.info(f"Finalizing profile edit for user {user_id}")
    
    # Получаем все данные из состояния перед очисткой
    state_data = await state.get_data()
    logger.info(f"State data before finalizing: {state_data}")
    
    # Сохраняем все изменения из состояния в базу данных
    update_data = {}
    if 'name' in state_data:
        update_data['name'] = state_data['name']
    if 'age' in state_data:
        update_data['age'] = state_data['age']
    if 'city' in state_data:
        update_data['city'] = state_data['city']
    if 'latitude' in state_data:
        update_data['latitude'] = state_data['latitude']
    if 'longitude' in state_data:
        update_data['longitude'] = state_data['longitude']
    if 'bio' in state_data:
        update_data['bio'] = state_data['bio']
    # gender и looking_for уже сохранены в процессе выбора
    
    # Обновляем профиль, если есть изменения
    if update_data:
        await db.create_or_update_user(user_id, **update_data)
        logger.info(f"Updated user {user_id} with data: {update_data}")
    
    # Очищаем состояние FSM
    await state.clear()
    
    # Получаем свежие данные пользователя из базы
    updated_user = await db.get_user(user_id)
    logger.info(f"Final user data: name='{updated_user.name}', age={updated_user.age}, city='{updated_user.city}', bio='{updated_user.bio}', gender='{updated_user.gender}', looking_for='{updated_user.looking_for}'")
    
    has_complete_profile = is_profile_complete(updated_user)
    logger.info(f"Profile complete check result: {has_complete_profile}")
    
    # Показываем успешное сообщение
    success_text = "✅ <b>Анкета обновлена!</b>\n\nВсе изменения сохранены. Теперь можешь посмотреть свою обновленную анкету."
    
    try:
        await message.edit_text(
            success_text,
            parse_mode="HTML",
            reply_markup=get_back_to_profile_keyboard()
        )
    except Exception:
        await message.answer(
            success_text,
            parse_mode="HTML",
            reply_markup=get_back_to_profile_keyboard()
        )

@router.callback_query(F.data == "improve_with_ai")
async def improve_profile_with_ai(callback: CallbackQuery, db: Database):
    """Улучшить анкету с помощью AI"""
    await callback.answer("🤖 Анализирую твою анкету...")
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user or not user.bio:
        try:
            await callback.message.edit_caption(
                caption="❌ Сначала заполни описание анкеты",
                parse_mode="HTML",
                reply_markup=get_profile_keyboard(is_own=True)
            )
        except Exception:
            await callback.message.edit_text(
                "❌ Сначала заполни описание анкеты",
                parse_mode="HTML",
                reply_markup=get_profile_keyboard(is_own=True)
            )
        return
    
    # Улучшаем описание с помощью AI
    user_data = {
        'name': user.name,
        'age': user.age,
        'city': user.city,
        'gender': user.gender
    }
    
    improved_bio = await ai_helper.improve_bio_with_ai(user.bio, user_data)
    
    if improved_bio:
        # Сохраняем улучшенное описание
        await db.create_or_update_user(user_id, bio=improved_bio)
        
        try:
            await callback.message.edit_caption(
                caption="✨ <b>Описание улучшено с помощью AI!</b>\n\nВот твоя обновленная анкета:",
                parse_mode="HTML",
                reply_markup=get_back_to_menu_keyboard()
            )
        except Exception:
            await callback.message.edit_text(
                "✨ <b>Описание улучшено с помощью AI!</b>\n\nВот твоя обновленная анкета:",
                parse_mode="HTML",
                reply_markup=get_back_to_menu_keyboard()
            )
        
        # Показываем обновленную анкету
        from handlers.profile import show_user_profile
        await show_user_profile(callback.message, db, user_id, is_own=True)
    else:
        try:
            await callback.message.edit_caption(
                caption="❌ Не удалось улучшить описание. AI-сервис временно недоступен.",
                parse_mode="HTML",
                reply_markup=get_profile_keyboard(is_own=True)
            )
        except Exception:
            await callback.message.edit_text(
                "❌ Не удалось улучшить описание. AI-сервис временно недоступен.",
                parse_mode="HTML",
                reply_markup=get_profile_keyboard(is_own=True)
            )

def register_profile_edit_handlers(dp):
    """Регистрация обработчиков редактирования профиля"""
    dp.include_router(router)
