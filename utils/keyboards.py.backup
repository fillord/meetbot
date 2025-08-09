from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional

def get_main_mendef get_settings_keyboard() -> InlineKeyboardMarkup:
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
    return builder.as_markup()file: bool = False) -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    
    if has_profile:
        builder.row(
            InlineKeyboardButton(text="👀 Смотреть анкеты", callback_data="start_swiping"),
            InlineKeyboardButton(text="� Лайки", callback_data="my_chats")
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
        InlineKeyboardButton(text="🌈 Всех", callback_data="looking_both")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return builder.as_markup()

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")
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

def get_skip_location_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска геолокации"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_location"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return builder.as_markup()

def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для статистики"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏆 Топ пользователей", callback_data="top_users"),
        InlineKeyboardButton(text="📊 Общая статистика", callback_data="global_stats")
    )
    builder.row(
        InlineKeyboardButton(text="� Рекомендации", callback_data="profile_recommendations")
    )
    builder.row(
        InlineKeyboardButton(text="�🔙 В главное меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_profile_keyboard(user_id: int, is_own_profile: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура для анкеты"""
    builder = InlineKeyboardBuilder()
    
    if is_own_profile:
        builder.row(
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile"),
            InlineKeyboardButton(text="📸 Фото", callback_data="manage_photos")
        )
        builder.row(
            InlineKeyboardButton(text="🤖 Улучшить с AI", callback_data="improve_with_ai"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="❤️ Лайк", callback_data=f"like_{user_id}"),
            InlineKeyboardButton(text="👎 Пропустить", callback_data=f"dislike_{user_id}")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Пожаловаться", callback_data=f"report_{user_id}")
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return builder.as_markup()

def get_swipe_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для свайпов"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❤️", callback_data=f"like_{user_id}"),
        InlineKeyboardButton(text="👎", callback_data=f"dislike_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⏩ Следующая", callback_data="next_profile"),
        InlineKeyboardButton(text="🔙 Меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_photo_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления фотографиями"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📷 Добавить фото", callback_data="add_photo"),
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
        InlineKeyboardButton(text="� Радиус поиска", callback_data="search_radius_settings")
    )
    builder.row(
        InlineKeyboardButton(text="�️ Показ возраста", callback_data="toggle_show_age"),
        InlineKeyboardButton(text="📍 Показ локации", callback_data="toggle_show_location")
    )
    builder.row(
        InlineKeyboardButton(text="� Уведомления", callback_data="toggle_notifications")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 В меню", callback_data="main_menu")
    )
    return builder.as_markup()

def get_chat_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для чата"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Написать", callback_data=f"open_chat_{chat_id}"),
        InlineKeyboardButton(text="👤 Профиль", callback_data=f"view_match_profile_{chat_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Удалить матч", callback_data=f"unmatch_{chat_id}"),
        InlineKeyboardButton(text="📊 Пожаловаться", callback_data=f"report_match_{chat_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 К чатам", callback_data="my_chats")
    )
    return builder.as_markup()

def get_age_range_keyboard(current_min: int, current_max: int) -> InlineKeyboardMarkup:
    """Клавиатура для настройки возрастного диапазона"""
    builder = InlineKeyboardBuilder()
    
    # Минимальный возраст
    builder.row(
        InlineKeyboardButton(text="➖", callback_data="age_min_decrease"),
        InlineKeyboardButton(text=f"Мин: {current_min}", callback_data="age_min_info"),
        InlineKeyboardButton(text="➕", callback_data="age_min_increase")
    )
    
    # Максимальный возраст
    builder.row(
        InlineKeyboardButton(text="➖", callback_data="age_max_decrease"),
        InlineKeyboardButton(text=f"Макс: {current_max}", callback_data="age_max_info"),
        InlineKeyboardButton(text="➕", callback_data="age_max_increase")
    )
    
    builder.row(
        InlineKeyboardButton(text="✅ Сохранить", callback_data="settings"),
        InlineKeyboardButton(text="🔄 Сбросить", callback_data="age_range_reset")
    )
    
    return builder.as_markup()

def get_search_radius_keyboard(current_radius: int) -> InlineKeyboardMarkup:
    """Клавиатура для настройки радиуса поиска"""
    builder = InlineKeyboardBuilder()
    
    # Радиус поиска
    builder.row(
        InlineKeyboardButton(text="➖", callback_data="radius_decrease"),
        InlineKeyboardButton(text=f"{current_radius} км", callback_data="radius_info"),
        InlineKeyboardButton(text="➕", callback_data="radius_increase")
    )
    
    # Быстрые настройки
    builder.row(
        InlineKeyboardButton(text="5 км", callback_data="radius_set_5"),
        InlineKeyboardButton(text="10 км", callback_data="radius_set_10"),
        InlineKeyboardButton(text="25 км", callback_data="radius_set_25")
    )
    
    builder.row(
        InlineKeyboardButton(text="50 км", callback_data="radius_set_50"),
        InlineKeyboardButton(text="100 км", callback_data="radius_set_100"),
        InlineKeyboardButton(text="Везде", callback_data="radius_set_999")
    )
    
    builder.row(
        InlineKeyboardButton(text="✅ Сохранить", callback_data="settings")
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

def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура пагинации"""
    builder = InlineKeyboardBuilder()
    
    buttons = []
    if current_page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}_page_{current_page-1}"))
    
    buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}_page_{current_page+1}"))
    
    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    
    return builder.as_markup()

def get_photos_keyboard(current_count: int) -> InlineKeyboardMarkup:
    """Клавиатура управления фотографиями (используем расширенную версию)"""
    # Для совместимости создаем пустой список фото
    fake_photos = [type('Photo', (), {'id': i, 'order_num': i+1}) for i in range(current_count)]
    return get_photo_management_keyboard(fake_photos)

def get_skip_or_keep_keyboard(step: str, has_current_value: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура с опциями пропустить или оставить как есть"""
    builder = InlineKeyboardBuilder()
    
    # Убираем возможность пропустить описание - теперь оно обязательно
    if has_current_value:
        builder.row(
            InlineKeyboardButton(text="💾 Оставить как есть", callback_data=f"keep_{step}")
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Отмена", callback_data="main_menu")
    )
    
    return builder.as_markup()

def get_delete_photos_keyboard(photos) -> InlineKeyboardMarkup:
    """Создает клавиатуру для удаления фотографий"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки для удаления конкретных фото (по 2 в ряд)
    for i in range(0, len(photos), 2):
        row_buttons = []
        for j in range(i, min(i + 2, len(photos))):
            photo = photos[j]
            button_text = f"📸 Фото {j+1}"
            if photo.is_main:
                button_text += " ⭐"
            
            row_buttons.append(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"delete_photo_{photo.photo_id}"
                )
            )
        builder.row(*row_buttons)
    
    # Кнопка "Назад"
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="manage_photos")
    )
    
    return builder.as_markup()

def get_photo_management_keyboard(photos: List) -> InlineKeyboardMarkup:
    """Расширенная клавиатура управления фотографиями"""
    builder = InlineKeyboardBuilder()
    
    if len(photos) < 5:
        builder.row(
            InlineKeyboardButton(text="➕ Добавить фото", callback_data="add_photo")
        )
    
    if len(photos) > 0:
        builder.row(
            InlineKeyboardButton(text="👁️ Посмотреть все", callback_data="view_photos"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data="delete_photo_menu")
        )
        
        if len(photos) > 1:
            builder.row(
                InlineKeyboardButton(text="⭐ Главное фото", callback_data="set_main_photo_menu")
            )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад к профилю", callback_data="edit_profile")
    )
    
    return builder.as_markup()

def get_set_main_photo_keyboard(photos: List) -> InlineKeyboardMarkup:
    """Клавиатура для выбора главного фото"""
    builder = InlineKeyboardBuilder()
    
    # Группируем по 2 кнопки в ряд
    for i in range(0, len(photos), 2):
        row_buttons = []
        for j in range(i, min(i + 2, len(photos))):
            photo = photos[j]
            emoji = "⭐" if photo.order_num == 1 else "📸"
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{emoji} Фото {j+1}", 
                    callback_data=f"set_main_photo_{photo.photo_id}"
                )
            )
        builder.row(*row_buttons)
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="manage_photos")
    )
    
    return builder.as_markup()
