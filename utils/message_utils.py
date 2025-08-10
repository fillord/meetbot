"""
Утилиты для работы с сообщениями Telegram
"""
from aiogram.types import Message


async def safe_edit_message(message: Message, text: str = None, media=None, reply_markup=None, parse_mode="HTML"):
    """
    Безопасное редактирование сообщения с fallback
    
    Args:
        message: Сообщение для редактирования
        text: Текст для редактирования (если нет media)
        media: Медиа для редактирования (фото, видео и т.д.)
        reply_markup: Клавиатура
        parse_mode: Режим парсинга HTML/Markdown
    """
    try:
        if media:
            await message.edit_media(
                media=media,
                reply_markup=reply_markup
            )
        elif text:
            await message.edit_text(
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            # Если ни текста, ни медиа - редактируем только клавиатуру
            await message.edit_reply_markup(reply_markup=reply_markup)
    except Exception:
        # Если не удалось редактировать, удаляем и отправляем новое
        try:
            await message.delete()
        except Exception:
            pass
        
        if media and hasattr(media, 'media'):
            # Отправляем новое сообщение с медиа
            if hasattr(media, 'caption'):
                await message.answer_photo(
                    photo=media.media,
                    caption=media.caption,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            else:
                await message.answer_photo(
                    photo=media.media,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
        elif text:
            # Отправляем новое текстовое сообщение
            await message.answer(
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )


async def safe_delete_message(message: Message):
    """
    Безопасное удаление сообщения
    
    Args:
        message: Сообщение для удаления
    """
    try:
        await message.delete()
    except Exception:
        # Игнорируем ошибки удаления (сообщение может быть уже удалено)
        pass


async def safe_answer_message(message: Message, text: str, reply_markup=None, parse_mode="HTML"):
    """
    Безопасная отправка ответного сообщения
    
    Args:
        message: Исходное сообщение
        text: Текст ответа
        reply_markup: Клавиатура
        parse_mode: Режим парсинга HTML/Markdown
    """
    try:
        return await message.answer(
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except Exception as e:
        # Если не удалось отправить с разметкой, пробуем без неё
        try:
            return await message.answer(
                text=text,
                reply_markup=reply_markup
            )
        except Exception:
            # В крайнем случае отправляем только текст
            return await message.answer(text=text)
