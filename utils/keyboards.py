from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List, Optional

async def get_main_menu_keyboard_with_likes(db, user_id: int, has_profile: bool = False) -> InlineKeyboardMarkup:
    """Главное меню бота с автоматическим подсчетом лайков"""
    unread_likes_count = 0
    if has_profile:
        try:
            unread_likes_count = await db.get_unread_likes_count(user_id)
        except Exception:
            unread_likes_count = 0
    return get_main_menu_keyboard(has_profile, unread_likes_count)

def get_main_menu_keyboard(has_profile: bool = False, unread_likes_count: int = 0) -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    
    if has_profile:
        # Формируем текст для кнопки лайков
        likes_text = "💌 Лайки"
        if unread_likes_count > 0:
            likes_text = f"💌 Лайки ({unread_likes_count})"
        
        builder.row(
            InlineKeyboardButton(text="👀 Смотреть анкеты", callback_data="start_swiping"),
            InlineKeyboardButton(text=likes_text, callback_data="my_chats")
        )
        builder.row(
            InlineKeyboardButton(text="📝 Моя анкета", callback_data="my_profile"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Статистика", callback_data="statistics"),
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="📝 Создать анкету", callback_data="create_profile")
        )
        builder.row(
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")
        )
    
    return builder.as_markup()

def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора пола"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
        InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return builder.as_markup()

def get_gender_keyboard_with_keep(has_current: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура выбора пола с возможностью оставить как есть"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
        InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")
    )
    if has_current:
        builder.row(InlineKeyboardButton(text="Оставить как есть ✅", callback_data="keep_gender"))
    builder.row(InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_edit"))
    return builder.as_markup()

def get_looking_for_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора предпочтений"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👨 Парней", callback_data="looking_male"),
        InlineKeyboardButton(text="👩 Девушек", callback_data="looking_female")
    )
    builder.row(
        InlineKeyboardButton(text="👫 Всех", callback_data="looking_both")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return builder.as_markup()

def get_looking_for_keyboard_with_keep(has_current: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура выбора предпочтений с возможностью оставить как есть"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👨 Парней", callback_data="looking_male"),
        InlineKeyboardButton(text="👩 Девушек", callback_data="looking_female")
    )
    builder.row(
        InlineKeyboardButton(text="👫 Всех", callback_data="looking_both")
    )
    if has_current:
        builder.row(InlineKeyboardButton(text="Оставить как есть ✅", callback_data="keep_looking_for"))
    builder.row(InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_edit"))
    return builder.as_markup()

def get_photo_action_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для действий с фото"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📸 Добавить фото", callback_data="add_photo")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Завершить", callback_data="finish_profile")
    )
    return builder.as_markup()

def get_confirm_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения профиля"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Все верно", callback_data="confirm_profile"),
        InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_profile")
    )
    return builder.as_markup()

def get_swipe_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для свайпа"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❤️ Лайк", callback_data=f"like_{user_id}"),
        InlineKeyboardButton(text="👎 Пас", callback_data=f"dislike_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⏭️ Следующий", callback_data=f"next_profile_{user_id}"),
        InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_profile_keyboard(is_own: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура профиля"""
    builder = InlineKeyboardBuilder()
    
    if is_own:
        builder.row(
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile"),
            InlineKeyboardButton(text="📸 Фото", callback_data="manage_photos")
        )
        builder.row(
            InlineKeyboardButton(text="📍 Геолокация", callback_data="set_location")
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_photo_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления фото"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Добавить фото", callback_data="add_photo"),
        InlineKeyboardButton(text="🗑️ Удалить фото", callback_data="delete_photo")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Все фото", callback_data="view_all_photos"),
        InlineKeyboardButton(text="⭐ Главное фото", callback_data="set_main_photo")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 К анкете", callback_data="my_profile")
    )
    return builder.as_markup()

def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура редактирования профиля (упрощенная)"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✏️ Перезаполнить анкету", callback_data="recreate_profile")
    )
    builder.row(
        InlineKeyboardButton(text="📸 Управление фото", callback_data="manage_photos")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 Улучшить с AI", callback_data="improve_with_ai")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="my_profile")
    )
    
    return builder.as_markup()

def get_photo_add_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для добавления фото во время создания профиля"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Добавить еще фото", callback_data="add_more_photo"),
        InlineKeyboardButton(text="✅ Завершить", callback_data="finish_profile")
    )
    return builder.as_markup()

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎯 Возрастной диапазон", callback_data="age_range_settings"),
        InlineKeyboardButton(text="📍 Радиус поиска", callback_data="search_radius_settings")
    )
    builder.row(
        InlineKeyboardButton(text="🎂 Показ возраста", callback_data="toggle_show_age"),
        InlineKeyboardButton(text="📍 Показ локации", callback_data="toggle_show_location")
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications")
    )
    builder.row(
        InlineKeyboardButton(text="🗑️ Удалить анкету", callback_data="delete_profile_confirm")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_delete_profile_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления анкеты"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Да, удалить", callback_data="delete_profile_confirmed"),
        InlineKeyboardButton(text="🔙 Отмена", callback_data="settings")
    )
    return builder.as_markup()

def get_location_keyboard():
    """Клавиатура для отправки геолокации"""
    from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Нажми кнопку ниже для отправки местоположения"
    )
    return keyboard

def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура статистики"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏆 Топ пользователей", callback_data="top_users"),
        InlineKeyboardButton(text="🌍 Общая статистика", callback_data="global_stats")
    )
    builder.row(
        InlineKeyboardButton(text="💡 Рекомендации", callback_data="profile_recommendations")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура возврата в меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_like_response_keyboard(liked_user_id: int, like_index: int) -> InlineKeyboardMarkup:
    """Клавиатура для ответа на лайк"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💖 Лайк", callback_data=f"like_response_like_{liked_user_id}_{like_index}"),
        InlineKeyboardButton(text="👎 Пас", callback_data=f"like_response_dislike_{liked_user_id}_{like_index}")
    )
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"skip_like_{like_index}")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_confirm_keyboard(action: str, data: str = "") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{data}"),
        InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
    )
    return builder.as_markup()

def get_age_range_keyboard(current_min: int = 18, current_max: int = 99) -> InlineKeyboardMarkup:
    """Клавиатура управления возрастным диапазоном"""
    builder = InlineKeyboardBuilder()
    
    # Управление минимальным возрастом
    builder.row(
        InlineKeyboardButton(text="➖", callback_data=f"age_min_down_{current_min}"),
        InlineKeyboardButton(text=f"Мин: {current_min}", callback_data="age_min_info"),
        InlineKeyboardButton(text="➕", callback_data=f"age_min_up_{current_min}")
    )
    
    # Управление максимальным возрастом
    builder.row(
        InlineKeyboardButton(text="➖", callback_data=f"age_max_down_{current_max}"),
        InlineKeyboardButton(text=f"Макс: {current_max}", callback_data="age_max_info"),
        InlineKeyboardButton(text="➕", callback_data=f"age_max_up_{current_max}")
    )
    
    # Предустановленные диапазоны
    builder.row(
        InlineKeyboardButton(text="👶 18-25", callback_data="age_range_18_25"),
        InlineKeyboardButton(text="👨 26-35", callback_data="age_range_26_35")
    )
    builder.row(
        InlineKeyboardButton(text="👴 36-50", callback_data="age_range_36_50"),
        InlineKeyboardButton(text="🔄 Любой", callback_data="age_range_18_99")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="settings")
    )
    return builder.as_markup()

def get_search_radius_keyboard(current_radius: int = 50) -> InlineKeyboardMarkup:
    """Клавиатура управления радиусом поиска"""
    builder = InlineKeyboardBuilder()
    
    # Управление радиусом поиска
    builder.row(
        InlineKeyboardButton(text="➖", callback_data=f"radius_down_{current_radius}"),
        InlineKeyboardButton(text=f"{current_radius} км", callback_data="radius_info"),
        InlineKeyboardButton(text="➕", callback_data=f"radius_up_{current_radius}")
    )
    
    # Предустановленные значения
    builder.row(
        InlineKeyboardButton(text="🏠 5 км", callback_data="radius_5"),
        InlineKeyboardButton(text="🚗 25 км", callback_data="radius_25")
    )
    builder.row(
        InlineKeyboardButton(text="🚄 50 км", callback_data="radius_50"),
        InlineKeyboardButton(text="🌍 100 км", callback_data="radius_100")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="settings")
    )
    return builder.as_markup()

def get_skip_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой пропуска"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data=callback_data)
    )
    return builder.as_markup()

def get_skip_or_keep_keyboard(field: str, has_current_value: bool = False):
    """Создает клавиатуру для редактирования полей профиля"""
    keyboard = []
    
    # Добавляем кнопку "Оставить как есть" только если есть текущее значение
    if has_current_value:
        keyboard.append([InlineKeyboardButton(text="Оставить как есть ✅", callback_data=f"keep_{field}")])
    
    # Всегда добавляем кнопку отмены
    keyboard.append([InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_edit")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_photos_keyboard(photo_count: int) -> InlineKeyboardMarkup:
    """Клавиатура для работы с фотографиями"""
    builder = InlineKeyboardBuilder()
    
    if photo_count > 0:
        builder.row(
            InlineKeyboardButton(text="📸 Добавить фото", callback_data="add_photo"),
            InlineKeyboardButton(text="🗑️ Удалить фото", callback_data="delete_photo")
        )
        builder.row(
            InlineKeyboardButton(text="⭐ Главное фото", callback_data="set_main_photo"),
            InlineKeyboardButton(text="📋 Все фото", callback_data="view_all_photos")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="📸 Добавить фото", callback_data="add_photo")
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 К анкете", callback_data="my_profile")
    )
    return builder.as_markup()


def get_back_to_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для возврата к профилю после обновления"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Вернуться к анкете", callback_data="my_profile")
    )
    return builder.as_markup()

def get_set_main_photo_keyboard(photos: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора главного фото"""
    builder = InlineKeyboardBuilder()
    
    for i, photo in enumerate(photos):
        # Помечаем текущее главное фото звездочкой
        prefix = "⭐ " if photo.is_main else ""
        button_text = f"{prefix}Фото {i + 1}"
        builder.button(
            text=button_text,
            callback_data=f"set_main_photo_{photo.photo_id}"
        )
    
    # Кнопка возврата
    builder.row(
        InlineKeyboardButton(text="🔙 К управлению фото", callback_data="manage_photos")
    )
    
    # Делаем максимум 2 кнопки в ряду
    builder.adjust(2)
    return builder.as_markup()

# ======== REPLY КЛАВИАТУРЫ ========

def get_main_menu_reply_keyboard(has_profile: bool = False, unread_likes_count: int = 0) -> ReplyKeyboardMarkup:
    """Главное меню бота (reply клавиатура)"""
    builder = ReplyKeyboardBuilder()
    
    if has_profile:
        # Формируем текст для кнопки лайков
        likes_text = "💌 Лайки"
        if unread_likes_count > 0:
            likes_text = f"💌 Лайки ({unread_likes_count})"
        
        builder.row(
            KeyboardButton(text="👀 Смотреть анкеты"),
            KeyboardButton(text=likes_text)
        )
        builder.row(
            KeyboardButton(text="📝 Моя анкета"),
            KeyboardButton(text="⚙️ Настройки")
        )
        builder.row(
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="ℹ️ О боте")
        )
    else:
        builder.row(
            KeyboardButton(text="📝 Создать анкету")
        )
        builder.row(
            KeyboardButton(text="ℹ️ О боте")
        )
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

async def get_main_menu_reply_keyboard_with_likes(db, user_id: int, has_profile: bool = False) -> ReplyKeyboardMarkup:
    """Главное меню бота с автоматическим подсчетом лайков (reply клавиатура)"""
    unread_likes_count = 0
    if has_profile:
        try:
            unread_likes_count = await db.get_unread_likes_count(user_id)
        except Exception:
            unread_likes_count = 0
    return get_main_menu_reply_keyboard(has_profile, unread_likes_count)

def get_back_to_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    """Простая reply клавиатура возврата в меню"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔙 В меню")
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
