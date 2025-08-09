from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from database import Database
from utils.keyboards import get_main_menu_keyboard, get_like_response_keyboard
import logging

logger = logging.getLogger(__name__)

router = Router()

async def safe_edit_message(message, text: str = None, media=None, reply_markup=None, parse_mode="HTML"):
    """Безопасное редактирование сообщения с fallback"""
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
    except:
        # Если не удалось редактировать, удаляем и отправляем новое
        try:
            await message.delete()
        except:
            pass
        
        if media and hasattr(media, 'media'):
            await message.answer_photo(
                photo=media.media,
                caption=media.caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        elif text:
            await message.answer(
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )

@router.callback_query(F.data == "my_chats")
async def show_incoming_likes(callback: CallbackQuery, db: Database):
    """Показать входящие лайки для просмотра"""
    await callback.answer()
    
    user_id = callback.from_user.id
    incoming_likes = await db.get_incoming_likes(user_id)
    
    if not incoming_likes:
        try:
            await callback.message.edit_text(
                "💕 <b>Входящие лайки</b>\n\n"
                "У тебя пока нет новых лайков!\n"
                "Попробуй улучшить свою анкету или посмотри других пользователей 👀",
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard(has_profile=True)
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            await callback.message.answer(
                "💕 <b>Входящие лайки</b>\n\n"
                "У тебя пока нет новых лайков!\n"
                "Попробуй улучшить свою анкету или посмотри других пользователей 👀",
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard(has_profile=True)
            )
        return
    
    # Показываем первый лайк
    await show_like_profile(callback.message, db, user_id, 0)

async def show_like_profile(message, db: Database, user_id: int, like_index: int):
    """Показать профиль пользователя, который лайкнул"""
    incoming_likes = await db.get_incoming_likes(user_id)
    
    if like_index >= len(incoming_likes):
        await safe_edit_message(
            message,
            text="✅ <b>Все лайки просмотрены!</b>\n\n"
                 "Больше новых лайков пока нет.",
            reply_markup=get_main_menu_keyboard(has_profile=True)
        )
        return
    
    like_data = incoming_likes[like_index]
    liked_user_id = like_data['user_id']
    
    # Формируем информацию о профиле
    gender_emoji = "👨" if like_data['gender'] == "male" else "👩"
    
    profile_text = (
        f"💕 <b>Кто-то тебе понравился!</b>\n\n"
        f"{gender_emoji} <b>{like_data['name']}</b>, {like_data['age']} лет\n"
        f"🏙️ {like_data['city']}\n\n"
        f"📖 <b>О себе:</b>\n{like_data['bio']}\n\n"
        f"📊 Лайк {like_index + 1} из {len(incoming_likes)}"
    )
    
    keyboard = get_like_response_keyboard(liked_user_id, like_index)
    
    # Если есть фото, показываем с фото
    if like_data['main_photo']:
        media = InputMediaPhoto(
            media=like_data['main_photo'],
            caption=profile_text,
            parse_mode="HTML"
        )
        await safe_edit_message(message, media=media, reply_markup=keyboard)
    else:
        # Без фото
        await safe_edit_message(message, text=profile_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("like_response_"))
async def handle_like_response(callback: CallbackQuery, db: Database):
    """Обработка ответа на лайк"""
    await callback.answer()
    
    # Парсим данные: like_response_{action}_{liked_user_id}_{like_index}
    parts = callback.data.split("_")
    action = parts[2]  # like или dislike
    liked_user_id = int(parts[3])
    like_index = int(parts[4])
    
    user_id = callback.from_user.id
    is_like = (action == "like")
    
    # Отвечаем на лайк
    is_match = await db.respond_to_like(user_id, liked_user_id, is_like)
    
    if is_match:
        # Уведомляем о матче
        liked_user = await db.get_user(liked_user_id)
        current_user = await db.get_user(user_id)
        
        # Формируем ссылки на профили
        liked_user_link = f"tg://user?id={liked_user_id}"
        current_user_link = f"tg://user?id={user_id}"
        
        # Формируем username для отображения
        liked_username = f"@{liked_user.username}" if liked_user.username else liked_user.name
        current_username = f"@{current_user.username}" if current_user.username else current_user.name
        
        match_text = (
            f"🎉 <b>Взаимная симпатия!</b>\n\n"
            f"Ты понравился(лась) <a href='{liked_user_link}'>{liked_user.name}</a> и он(а) тебе тоже!\n\n"
            f"💬 <b>Для общения:</b>\n"
            f"• Нажми на имя {liked_user.name} выше\n"
            f"• Или напиши пользователю: {liked_username}\n"
            f"• Начинай диалог! 💕"
        )
        
        # Также отправляем уведомление второму пользователю
        try:
            match_text_for_liked_user = (
                f"🎉 <b>Взаимная симпатия!</b>\n\n"
                f"Ты понравился(лась) <a href='{current_user_link}'>{current_user.name}</a> и он(а) тебе тоже!\n\n"
                f"💬 <b>Для общения:</b>\n"
                f"• Нажми на имя {current_user.name} выше\n"
                f"• Или напиши пользователю: {current_username}\n"
                f"• Начинай диалог! 💕"
            )
            
            # Отправляем уведомление второму пользователю через бота
            from aiogram import Bot
            from config import Config
            bot = Bot(token=Config.BOT_TOKEN)
            await bot.send_message(
                chat_id=liked_user_id,
                text=match_text_for_liked_user,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Failed to send match notification to user {liked_user_id}: {e}")
        
        await callback.message.answer(
            match_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    # Показываем следующий лайк
    await show_like_profile(callback.message, db, user_id, like_index + 1)

@router.callback_query(F.data.startswith("skip_like_"))
async def skip_like(callback: CallbackQuery, db: Database):
    """Пропустить просмотр лайка"""
    await callback.answer()
    
    # Парсим индекс: skip_like_{like_index}
    like_index = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    # Показываем следующий лайк
    await show_like_profile(callback.message, db, user_id, like_index + 1)

def register_chat_handlers(dp):
    """Регистрация обработчиков чатов"""
    dp.include_router(router)
