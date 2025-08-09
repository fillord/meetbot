from .start import register_start_handlers
from .profile import register_profile_handlers
from .profile_edit import register_profile_edit_handlers
from .swipe import register_swipe_handlers
from .chat import register_chat_handlers
from .additional_handlers import register_additional_handlers

def register_all_handlers(dp):
    """Регистрация всех обработчиков"""
    register_start_handlers(dp)
    register_profile_edit_handlers(dp)  # Сначала специфичные обработчики с состояниями
    register_profile_handlers(dp)       # Потом общие обработчики
    register_swipe_handlers(dp)
    register_chat_handlers(dp)
    register_additional_handlers(dp)
