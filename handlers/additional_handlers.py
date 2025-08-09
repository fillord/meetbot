from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import Database
from utils.keyboards import (
    get_profile_keyboard, get_edit_profile_keyboard, 
    get_back_to_menu_keyboard, get_photos_keyboard,
    get_photo_management_keyboard, get_age_range_keyboard,
    get_search_radius_keyboard, get_delete_profile_confirm_keyboard,
    get_back_to_profile_keyboard
)
from handlers.profile import ProfileStates
import logging

logger = logging.getLogger(__name__)
router = Router()

class PhotoStates(StatesGroup):
    adding_photo = State()

@router.callback_query(F.data == "edit_name")
async def edit_name_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик редактирования имени"""
    await callback.answer()
    
    try:
        await callback.message.edit_text(
            "✏️ <b>Изменение имени</b>\n\n"
            "Введи новое имя (от 2 до 30 символов):",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_name)
    except Exception as e:
        logger.error(f"Error editing name: {e}")
        await callback.message.answer(
            "✏️ <b>Изменение имени</b>\n\n"
            "Введи новое имя (от 2 до 30 символов):",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_name)

@router.callback_query(F.data == "edit_age")
async def edit_age_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик редактирования возраста"""
    await callback.answer()
    
    try:
        await callback.message.edit_text(
            "🎂 <b>Изменение возраста</b>\n\n"
            "Укажи свой возраст (от 18 до 100 лет):",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_age)
    except Exception as e:
        logger.error(f"Error editing age: {e}")
        await callback.message.answer(
            "🎂 <b>Изменение возраста</b>\n\n"
            "Укажи свой возраст (от 18 до 100 лет):",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_age)

@router.callback_query(F.data == "edit_bio")
async def edit_bio_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик редактирования описания"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    current_bio = user.bio if user and user.bio else "Не указано"
    
    try:
        await callback.message.edit_text(
            f"📝 <b>Изменение описания</b>\n\n"
            f"Текущее описание: <i>{current_bio}</i>\n\n"
            f"Введи новое описание о себе (до 500 символов):",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_bio)
    except Exception as e:
        logger.error(f"Error editing bio: {e}")
        await callback.message.answer(
            f"📝 <b>Изменение описания</b>\n\n"
            f"Текущее описание: <i>{current_bio}</i>\n\n"
            f"Введи новое описание о себе (до 500 символов):",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_bio)

@router.callback_query(F.data == "edit_location")
async def edit_location_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик редактирования города"""
    await callback.answer()
    
    try:
        await callback.message.edit_text(
            "🌆 <b>Изменение города</b>\n\n"
            "Укажи свой город:",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_location)
    except Exception as e:
        logger.error(f"Error editing location: {e}")
        await callback.message.answer(
            "🌆 <b>Изменение города</b>\n\n"
            "Укажи свой город:",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_location)

@router.callback_query(F.data == "manage_photos")
async def manage_photos_handler(callback: CallbackQuery, db: Database):
    """Обработчик управления фотографиями"""
    await callback.answer()
    
    user_id = callback.from_user.id
    photos = await db.get_user_photos(user_id)
    
    from utils.keyboards import get_photo_management_keyboard
    
    try:
        await callback.message.edit_text(
            f"📸 <b>Управление фотографиями</b>\n\n"
            f"У тебя {len(photos)} фото из 5 возможных\n\n"
            f"Что хочешь сделать?",
            parse_mode="HTML",
            reply_markup=get_photo_management_keyboard()
        )
    except Exception as e:
        logger.error(f"Error managing photos: {e}")
        await callback.message.answer(
            f"📸 <b>Управление фотографиями</b>\n\n"
            f"У тебя {len(photos)} фото из 5 возможных\n\n"
            f"Что хочешь сделать?",
            parse_mode="HTML",
            reply_markup=get_photo_management_keyboard()
        )

@router.callback_query(F.data == "add_photo")
async def add_photo_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик добавления фото"""
    await callback.answer()
    
    user_id = callback.from_user.id
    photos = await db.get_user_photos(user_id)
    
    if len(photos) >= 5:
        try:
            await callback.message.edit_text(
                "❌ <b>Достигнут лимит</b>\n\n"
                "У тебя уже максимальное количество фото (5).\n"
                "Сначала удали одно из существующих.",
                parse_mode="HTML",
                reply_markup=get_photos_keyboard(len(photos))
            )
        except Exception as e:
            await callback.message.answer(
                "❌ <b>Достигнут лимит</b>\n\n"
                "У тебя уже максимальное количество фото (5).\n"
                "Сначала удали одно из существующих.",
                parse_mode="HTML",
                reply_markup=get_photos_keyboard(len(photos))
            )
        return
    
    try:
        await callback.message.edit_text(
            "📸 <b>Добавление фото</b>\n\n"
            "Отправь фотографию, которую хочешь добавить в анкету:",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(PhotoStates.adding_photo)
    except Exception as e:
        logger.error(f"Error adding photo: {e}")
        await callback.message.answer(
            "📸 <b>Добавление фото</b>\n\n"
            "Отправь фотографию, которую хочешь добавить в анкету:",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.set_state(PhotoStates.adding_photo)

@router.message(PhotoStates.adding_photo, F.photo)
async def process_add_photo(message: Message, state: FSMContext, db: Database):
    """Обработка добавления нового фото в существующий профиль"""
    user_id = message.from_user.id
    
    # Получаем фото наилучшего качества
    photo = message.photo[-1]
    
    # Проверяем количество фотографий пользователя еще раз
    existing_photos = await db.get_user_photos(user_id)
    if len(existing_photos) >= 5:
        await message.answer(
            "❌ У тебя уже максимальное количество фотографий (5)",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
    
    # Добавляем фото (НЕ как главное)
    await db.add_user_photo(
        user_id=user_id,
        file_id=photo.file_id,
        file_unique_id=photo.file_unique_id,
        is_main=False
    )
    
    # Очищаем состояние
    await state.clear()
    
    # Показываем успешное сообщение и возвращаем к профилю
    await message.answer(
        "✅ <b>Фото добавлено!</b>\n\n"
        "Фотография успешно добавлена в твою анкету.",
        parse_mode="HTML",
        reply_markup=get_back_to_profile_keyboard()
    )

@router.message(PhotoStates.adding_photo)
async def process_invalid_add_photo(message: Message, state: FSMContext):
    """Обработка неправильного типа сообщения при добавлении фото"""
    await message.answer(
        "❌ Пожалуйста, отправь фотографию",
        reply_markup=get_back_to_menu_keyboard()
    )

@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, db: Database):
    """Показать настройки"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await callback.message.answer("❌ Пользователь не найден")
        return
    
    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"🎯 <b>Возрастной диапазон:</b> {user.min_age}-{user.max_age} лет\n"
        f"� <b>Радиус поиска:</b> {user.search_radius} км\n"
        f"👁️ <b>Показывать возраст:</b> {'Да' if user.show_age else 'Нет'}\n"
        f"📍 <b>Показывать город:</b> {'Да' if user.show_location else 'Нет'}\n"
        f"🔔 <b>Уведомления:</b> {'Включены' if user.notifications_enabled else 'Выключены'}"
    )
    
    from utils.keyboards import get_settings_keyboard
    
    try:
        await callback.message.edit_text(
            settings_text,
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )
    except Exception as e:
        logger.error(f"Error showing settings: {e}")
        await callback.message.answer(
            settings_text,
            parse_mode="HTML",
            reply_markup=get_settings_keyboard()
        )

# Обработчики настроек возрастного диапазона
@router.callback_query(F.data == "age_range_settings")
async def show_age_range_settings(callback: CallbackQuery, db: Database):
    """Показать настройки возрастного диапазона"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    text = (
        f"🎯 <b>Возрастной диапазон</b>\n\n"
        f"Текущие настройки: {user.min_age}-{user.max_age} лет\n\n"
        f"Используй кнопки ➖ и ➕ для изменения диапазона:"
    )
    
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_age_range_keyboard(user.min_age, user.max_age)
        )
    except Exception as e:
        logger.error(f"Error showing age range settings: {e}")
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_age_range_keyboard(user.min_age, user.max_age)
        )

@router.callback_query(F.data.startswith("age_min_"))
async def handle_age_min_change(callback: CallbackQuery, db: Database):
    """Изменение минимального возраста"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    # Парсим callback_data: age_min_down_18 или age_min_up_18
    parts = callback.data.split("_")
    action = parts[2]  # down, up, info
    
    if action == "down" and user.min_age > 18:
        new_min_age = user.min_age - 1
        if new_min_age < user.max_age:
            await db.create_or_update_user(user_id, min_age=new_min_age)
    elif action == "up" and user.min_age < 99:
        new_min_age = user.min_age + 1
        if new_min_age < user.max_age:
            await db.create_or_update_user(user_id, min_age=new_min_age)
    elif action == "info":
        await callback.answer(f"Минимальный возраст: {user.min_age} лет")
        return
    
    # Обновляем клавиатуру без отправки нового сообщения
    updated_user = await db.get_user(user_id)
    text = (
        f"🎯 <b>Возрастной диапазон</b>\n\n"
        f"Текущие настройки: {updated_user.min_age}-{updated_user.max_age} лет\n\n"
        f"Используй кнопки ➖ и ➕ для изменения диапазона:"
    )
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_age_range_keyboard(updated_user.min_age, updated_user.max_age)
        )
    except Exception:
        pass  # Игнорируем ошибки редактирования

@router.callback_query(F.data.startswith("age_max_"))
async def handle_age_max_change(callback: CallbackQuery, db: Database):
    """Изменение максимального возраста"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    # Парсим callback_data: age_max_down_35 или age_max_up_35
    parts = callback.data.split("_")
    action = parts[2]  # down, up, info
    
    if action == "down" and user.max_age > 18:
        new_max_age = user.max_age - 1
        if new_max_age > user.min_age:
            await db.create_or_update_user(user_id, max_age=new_max_age)
    elif action == "up" and user.max_age < 99:
        new_max_age = user.max_age + 1
        await db.create_or_update_user(user_id, max_age=new_max_age)
    elif action == "info":
        await callback.answer(f"Максимальный возраст: {user.max_age} лет")
        return
    
    # Обновляем клавиатуру без отправки нового сообщения
    updated_user = await db.get_user(user_id)
    text = (
        f"🎯 <b>Возрастной диапазон</b>\n\n"
        f"Текущие настройки: {updated_user.min_age}-{updated_user.max_age} лет\n\n"
        f"Используй кнопки ➖ и ➕ для изменения диапазона:"
    )
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_age_range_keyboard(updated_user.min_age, updated_user.max_age)
        )
    except Exception:
        pass  # Игнорируем ошибки редактирования

@router.callback_query(F.data.startswith("age_range_"))
async def handle_age_range_preset(callback: CallbackQuery, db: Database):
    """Обработка предустановленных возрастных диапазонов"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Парсим callback_data: age_range_18_25, age_range_26_35, etc.
    parts = callback.data.split("_")
    if len(parts) >= 4:
        min_age = int(parts[2])
        max_age = int(parts[3])
        await db.create_or_update_user(user_id, min_age=min_age, max_age=max_age)
        
        # Обновляем клавиатуру
        text = (
            f"🎯 <b>Возрастной диапазон</b>\n\n"
            f"Текущие настройки: {min_age}-{max_age} лет\n\n"
            f"Используй кнопки ➖ и ➕ для изменения диапазона:"
        )
        try:
            await callback.message.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=get_age_range_keyboard(min_age, max_age)
            )
        except Exception:
            pass

# Обработчики настроек радиуса поиска
@router.callback_query(F.data == "search_radius_settings")
async def show_search_radius_settings(callback: CallbackQuery, db: Database):
    """Показать настройки радиуса поиска"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    text = (
        f"📏 <b>Радиус поиска</b>\n\n"
        f"Текущий радиус: {user.search_radius} км\n\n"
        f"Измени радиус поиска анкет:"
    )
    
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_search_radius_keyboard(user.search_radius)
        )
    except Exception as e:
        logger.error(f"Error showing search radius settings: {e}")
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_search_radius_keyboard(user.search_radius)
        )

@router.callback_query(F.data.startswith("radius_"))
async def handle_radius_change(callback: CallbackQuery, db: Database):
    """Изменение радиуса поиска"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    # Парсим callback_data
    parts = callback.data.split("_")
    action = parts[1]
    
    if action == "down" and user.search_radius > 5:
        new_radius = max(5, user.search_radius - 5)
        await db.create_or_update_user(user_id, search_radius=new_radius)
    elif action == "up" and user.search_radius < 500:
        new_radius = min(500, user.search_radius + 5)
        await db.create_or_update_user(user_id, search_radius=new_radius)
    elif action == "info":
        await callback.answer(f"Радиус поиска: {user.search_radius} км")
        return
    elif action.isdigit():  # Предустановленные значения: radius_5, radius_25, etc.
        new_radius = int(action)
        await db.create_or_update_user(user_id, search_radius=new_radius)
    
    # Обновляем клавиатуру без отправки нового сообщения
    updated_user = await db.get_user(user_id)
    text = (
        f"📏 <b>Радиус поиска</b>\n\n"
        f"Текущий радиус: {updated_user.search_radius} км\n\n"
        f"Измени радиус поиска анкет:"
    )
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_search_radius_keyboard(updated_user.search_radius)
        )
    except Exception:
        pass  # Игнорируем ошибки редактирования

# Обработчики переключателей настроек
@router.callback_query(F.data == "toggle_show_age")
async def toggle_show_age(callback: CallbackQuery, db: Database):
    """Переключить показ возраста"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    new_value = not user.show_age
    await db.create_or_update_user(user_id, show_age=new_value)
    
    status = "включен" if new_value else "выключен"
    await callback.answer(f"Показ возраста {status}")
    
    # Обновляем отображение настроек
    await show_settings(callback, db)

@router.callback_query(F.data == "toggle_show_location")
async def toggle_show_location(callback: CallbackQuery, db: Database):
    """Переключить показ локации"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    new_value = not user.show_location
    await db.create_or_update_user(user_id, show_location=new_value)
    
    status = "включен" if new_value else "выключен"
    await callback.answer(f"Показ города {status}")
    
    # Обновляем отображение настроек
    await show_settings(callback, db)

@router.callback_query(F.data == "toggle_notifications")
async def toggle_notifications(callback: CallbackQuery, db: Database):
    """Переключить уведомления"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    new_value = not user.notifications_enabled
    await db.create_or_update_user(user_id, notifications_enabled=new_value)
    
    status = "включены" if new_value else "выключены"
    await callback.answer(f"Уведомления {status}")
    
    # Обновляем отображение настроек
    await show_settings(callback, db)

@router.callback_query(F.data == "delete_photo")
async def delete_photo_handler(callback: CallbackQuery, db: Database):
    """Обработчик кнопки удаления фото - показывает меню с фото для удаления"""
    await callback.answer()
    await show_delete_photo_menu(callback, db)

@router.callback_query(F.data == "delete_photo_menu")
async def show_delete_photo_menu(callback: CallbackQuery, db: Database):
    """Показать меню удаления фото с превью"""
    await callback.answer()
    
    user_id = callback.from_user.id
    photos = await db.get_user_photos(user_id)
    
    if not photos:
        try:
            await callback.message.edit_text(
                "📸 <b>У тебя нет фотографий</b>\n\n"
                "Сначала добавь фото в анкету!",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
        except Exception:
            await callback.message.answer(
                "📸 <b>У тебя нет фотографий</b>\n\n"
                "Сначала добавь фото в анкету!",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
        return

    # Сначала показываем сообщение с инструкцией
    try:
        await callback.message.edit_text(
            f"🗑️ <b>Удаление фото</b>\n\n"
            f"У тебя {len(photos)} фото. Сейчас покажу все фото с кнопками для удаления.\n"
            f"Нажми на кнопку под тем фото, которое хочешь удалить:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Назад", callback_data="manage_photos")
            ]])
        )
    except Exception:
        await callback.message.answer(
            f"🗑️ <b>Удаление фото</b>\n\n"
            f"У тебя {len(photos)} фото. Сейчас покажу все фото с кнопками для удаления.\n"
            f"Нажми на кнопку под тем фото, которое хочешь удалить:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Назад", callback_data="manage_photos")
            ]])
        )
    
    # Отправляем каждое фото с кнопкой удаления
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    for i, photo in enumerate(photos, 1):
        builder = InlineKeyboardBuilder()
        
        button_text = f"🗑️ Удалить фото {i}"
        if photo.is_main:
            button_text += " ⭐ (главное)"
            
        builder.button(
            text=button_text,
            callback_data=f"delete_photo_{photo.photo_id}"
        )
        
        try:
            await callback.message.answer_photo(
                photo=photo.file_id,
                caption=f"📸 <b>Фото {i} из {len(photos)}</b>" + (" ⭐ <i>(главное)</i>" if photo.is_main else ""),
                parse_mode="HTML",
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            logger.error(f"Error sending photo for deletion: {e}")


@router.callback_query(F.data.startswith("delete_photo_") & ~F.data.endswith("_menu"))
async def delete_photo_handler(callback: CallbackQuery, db: Database):
    """Обработчик удаления конкретного фото"""
    await callback.answer()
    
    try:
        photo_id = int(callback.data.split("_")[-1])
    except ValueError:
        await callback.answer("❌ Ошибка в данных", show_alert=True)
        return
    
    user_id = callback.from_user.id
    
    success = await db.delete_user_photo(user_id, photo_id)
    
    if success:
        photos = await db.get_user_photos(user_id)
        from utils.keyboards import get_photo_management_keyboard
        try:
            await callback.message.edit_text(
                f"✅ <b>Фото удалено</b>\n\n"
                f"У тебя осталось {len(photos)} фото из 5 возможных",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
        except Exception as e:
            await callback.message.answer(
                f"✅ <b>Фото удалено</b>\n\n"
                f"У тебя осталось {len(photos)} фото из 5 возможных",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
    else:
        try:
            await callback.message.edit_text(
                "❌ <b>Ошибка</b>\n\n"
                "Не удалось удалить фото",
                parse_mode="HTML",
                reply_markup=get_back_to_menu_keyboard()
            )
        except Exception as e:
            await callback.message.answer(
                "❌ <b>Ошибка</b>\n\n"
                "Не удалось удалить фото",
                parse_mode="HTML",
                reply_markup=get_back_to_menu_keyboard()
            )

@router.callback_query(F.data == "view_all_photos")
async def view_all_photos_handler(callback: CallbackQuery, db: Database):
    """Обработчик кнопки просмотра всех фото"""
    await callback.answer()
    await view_photos_handler(callback, db)

@router.callback_query(F.data == "view_photos")
async def view_photos_handler(callback: CallbackQuery, db: Database):
    """Показать все фото пользователя"""
    await callback.answer()
    
    user_id = callback.from_user.id
    photos = await db.get_user_photos(user_id)
    
    if not photos:
        from utils.keyboards import get_photo_management_keyboard
        try:
            await callback.message.edit_text(
                "📸 <b>У тебя нет фотографий</b>\n\n"
                "Добавь фото в анкету!",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
        except Exception:
            await callback.message.answer(
                "📸 <b>У тебя нет фотографий</b>\n\n"
                "Добавь фото в анкету!",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
        return
    
    # Отправляем все фото
    await callback.message.answer(
        f"📸 <b>Твои фото ({len(photos)})</b>",
        parse_mode="HTML"
    )
    
    for i, photo in enumerate(photos, 1):
        try:
            await callback.message.answer_photo(
                photo=photo.file_id,
                caption=f"Фото {i} из {len(photos)}"
            )
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
    
    # Возвращаемся к управлению фото
    from utils.keyboards import get_photo_management_keyboard
    await callback.message.answer(
        "Управление фотографиями:",
        reply_markup=get_photo_management_keyboard()
    )

@router.callback_query(F.data.startswith("set_main_photo_"))
async def set_main_photo_handler(callback: CallbackQuery, db: Database):
    """Установить главное фото"""
    await callback.answer()
    
    try:
        photo_id = int(callback.data.split("_")[-1])
        logger.info(f"Setting main photo for user {callback.from_user.id}, photo_id: {photo_id}")
    except ValueError:
        await callback.answer("❌ Ошибка в данных", show_alert=True)
        return
    
    user_id = callback.from_user.id
    
    # Сбрасываем порядок всех фото и устанавливаем выбранное как первое
    success = await db.set_main_photo(user_id, photo_id)
    logger.info(f"Set main photo result for user {user_id}: {success}")
    
    if success:
        await callback.answer("✅ Главное фото установлено!", show_alert=True)
        photos = await db.get_user_photos(user_id)
        logger.info(f"Photos after update: {[(p.photo_id, p.is_main, p.order_num) for p in photos]}")
        from utils.keyboards import get_photo_management_keyboard
        try:
            await callback.message.edit_text(
                f"📸 <b>Управление фотографиями</b>\n\n"
                f"У тебя {len(photos)} фото из 5 возможных\n"
                f"Главное фото обновлено!",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
        except Exception:
            await callback.message.answer(
                f"📸 <b>Управление фотографиями</b>\n\n"
                f"У тебя {len(photos)} фото из 5 возможных\n"
                f"Главное фото обновлено!",
                parse_mode="HTML",
                reply_markup=get_photo_management_keyboard()
            )
    else:
        await callback.answer("❌ Не удалось установить главное фото", show_alert=True)

@router.callback_query(F.data == "set_main_photo")
async def set_main_photo_button_handler(callback: CallbackQuery, db: Database):
    """Обработчик кнопки установки главного фото"""
    await callback.answer()
    await show_set_main_photo_menu(callback, db)

@router.callback_query(F.data == "set_main_photo_menu")
async def show_set_main_photo_menu(callback: CallbackQuery, db: Database):
    """Показать меню выбора главного фото"""
    await callback.answer()
    
    user_id = callback.from_user.id
    photos = await db.get_user_photos(user_id)
    
    if len(photos) < 2:
        await callback.answer("У тебя должно быть минимум 2 фото", show_alert=True)
        return
    
    from utils.keyboards import get_set_main_photo_keyboard
    try:
        await callback.message.edit_text(
            f"⭐ <b>Выбор главного фото</b>\n\n"
            f"Выбери, какое фото будет показываться первым в анкете:\n"
            f"⭐ - текущее главное фото",
            parse_mode="HTML",
            reply_markup=get_set_main_photo_keyboard(photos)
        )
    except Exception:
        await callback.message.answer(
            f"⭐ <b>Выбор главного фото</b>\n\n"
            f"Выбери, какое фото будет показываться первым в анкете:\n"
            f"⭐ - текущее главное фото",
            parse_mode="HTML",
            reply_markup=get_set_main_photo_keyboard(photos)
        )

def register_additional_handlers(dp):
    """Регистрация дополнительных обработчиков"""
    dp.include_router(router)

@router.callback_query(F.data == "delete_profile_confirm")
async def delete_profile_confirm(callback: CallbackQuery, db: Database):
    """Подтверждение удаления анкеты"""
    await callback.answer()
    
    try:
        await callback.message.edit_text(
            "🗑️ <b>Удаление анкеты</b>\n\n"
            "⚠️ <b>Внимание!</b> Это действие необратимо.\n\n"
            "При удалении анкеты будет удалено:\n"
            "• Вся информация о профиле\n"
            "• Все фотографии\n"
            "• История лайков и матчей\n"
            "• Все настройки\n\n"
            "❓ Вы уверены, что хотите удалить анкету?",
            parse_mode="HTML",
            reply_markup=get_delete_profile_confirm_keyboard()
        )
    except Exception:
        await callback.message.answer(
            "🗑️ <b>Удаление анкеты</b>\n\n"
            "⚠️ <b>Внимание!</b> Это действие необратимо.\n\n"
            "При удалении анкеты будет удалено:\n"
            "• Вся информация о профиле\n"
            "• Все фотографии\n"
            "• История лайков и матчей\n"
            "• Все настройки\n\n"
            "❓ Вы уверены, что хотите удалить анкету?",
            parse_mode="HTML",
            reply_markup=get_delete_profile_confirm_keyboard()
        )

@router.callback_query(F.data == "delete_profile_confirmed")
async def delete_profile_confirmed(callback: CallbackQuery, db: Database):
    """Подтверждение удаления анкеты"""
    await callback.answer("Анкета удаляется...")
    
    user_id = callback.from_user.id
    
    try:
        # Удаляем анкету из базы данных
        await db.delete_user_profile(user_id)
        
        from utils.keyboards import get_main_menu_keyboard
        
        await callback.message.edit_text(
            "✅ <b>Анкета успешно удалена</b>\n\n"
            "Вся информация о профиле была удалена.\n"
            "Вы можете создать новую анкету в любое время.",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(has_profile=False)
        )
    except Exception as e:
        logger.error(f"Error deleting profile: {e}")
        await callback.message.edit_text(
            "❌ <b>Ошибка при удалении анкеты</b>\n\n"
            "Произошла ошибка. Попробуйте позже.",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )

# Обработчики для кнопок "Оставить текущее" при редактировании профиля
@router.callback_query(F.data.startswith("keep_"))
async def keep_field_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик кнопки 'Оставить текущее'"""
    await callback.answer()
    
    field = callback.data.split("_")[1]  # получаем поле (name, age, city, bio)
    
    # Импортируем функцию из profile_edit
    from handlers.profile_edit import handle_keep_current
    await handle_keep_current(callback, state, db, field)

@router.callback_query(F.data.startswith("skip_"))
async def skip_field_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик кнопки 'Пропустить'"""
    await callback.answer()
    
    field = callback.data.split("_")[1]  # получаем поле (name, age, city, bio)
    
    # Импортируем функцию из profile_edit
    from handlers.profile_edit import handle_keep_current
    # Для пропуска используем ту же логику, что и для сохранения текущего
    await handle_keep_current(callback, state, db, field)
