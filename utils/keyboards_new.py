from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional

def get_main_menu_keyboard(has_profile: bool = False) -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    
    if has_profile:
        builder.row(
            InlineKeyboardButton(text="👀 Смотреть анкеты", callback_data="start_swiping"),
            InlineKeyboardButton(text="💌 Лайки", callback_data="my_chats")
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
        InlineKeyboardButton(text="❤️ Лайк", callback_data=f"swipe_like_{user_id}"),
        InlineKeyboardButton(text="👎 Пас", callback_data=f"swipe_dislike_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="💤 Пауза", callback_data="pause_swiping"),
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

def get_location_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для установки локации"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📍 Поделиться локацией", callback_data="share_location")
    )
    builder.row(
        InlineKeyboardButton(text="🏙️ Ввести город", callback_data="enter_city")
    )
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_location")
    )
    return builder.as_markup()

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

def get_age_range_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора возрастного диапазона"""
    builder = InlineKeyboardBuilder()
    
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
        InlineKeyboardButton(text="✏️ Свой диапазон", callback_data="custom_age_range")
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
