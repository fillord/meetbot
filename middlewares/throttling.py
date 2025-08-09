from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import time
import logging

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для защиты от спама"""
    
    def __init__(self, rate_limit: float = 1.0):
        """
        :param rate_limit: Минимальный интервал между сообщениями в секундах
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.last_message_time: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Основная логика middleware"""
        
        # Получаем user_id из события
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        
        if user_id:
            current_time = time.time()
            last_time = self.last_message_time.get(user_id, 0)
            
            # Проверяем, не превышен ли лимит
            if current_time - last_time < self.rate_limit:
                logger.warning(f"Throttling user {user_id}")
                
                # Если это callback query, отвечаем с уведомлением
                if hasattr(event, 'answer'):
                    await event.answer(
                        "⏳ Слишком быстро! Подожди немного.",
                        show_alert=True
                    )
                return
            
            # Обновляем время последнего сообщения
            self.last_message_time[user_id] = current_time
        
        # Продолжаем обработку
        return await handler(event, data)
