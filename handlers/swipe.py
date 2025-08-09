from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import Database
from handlers.profile import show_user_profile
from utils.keyboards import get_swipe_keyboard, get_main_menu_keyboard
from utils.ai_helper import ai_helper
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "start_swiping")
async def start_swiping(callback: CallbackQuery, db: Database):
    """Начать просмотр анкет"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Проверяем, что у пользователя есть анкета
    user = await db.get_user(user_id)
    if not user or not user.name or not user.age or not user.gender:
        await callback.message.edit_text(
            "❌ Сначала создай свою анкету!",
            reply_markup=get_main_menu_keyboard(has_profile=False)
        )
        return
    
    # Обновляем время последней активности
    await db.update_last_active(user_id)
    
    # Получаем следующую анкету для просмотра
    await show_next_profile(callback.message, db, user_id)

async def show_next_profile(message, db: Database, user_id: int, exclude_user_id: int = None):
    """Показать следующую анкету для свайпа"""
    # Получаем информацию о текущем пользователе для отладки
    current_user = await db.get_user(user_id)
    logger.info(f"User {user_id} searching for profiles: gender={current_user.gender}, looking_for={current_user.looking_for}")
    
    # Получаем анкеты для просмотра
    potential_matches = await db.get_users_for_swipe(user_id, limit=10, exclude_user_id=exclude_user_id)
    logger.info(f"Found {len(potential_matches)} potential matches for user {user_id}")
    
    if not potential_matches:
        # Проверим, есть ли вообще пользователи в базе (для отладки)
        all_users = await db.get_all_users_debug()
        logger.info(f"Total users in database: {len(all_users)}")
        for user in all_users:
            logger.info(f"User {user.user_id}: gender={user.gender}, age={user.age}, active={user.is_active}")
        
        # Отправляем новое сообщение вместо редактирования
        await message.answer(
            "😔 <b>Анкеты закончились!</b>\n\n"
            "• Попробуй изменить фильтры поиска\n"
            "• Заходи позже - появятся новые пользователи\n"
            "• Расширь возрастной диапазон или радиус поиска",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(has_profile=True)
        )
        return
    
    candidate = potential_matches[0]
    
    # Увеличиваем счетчик просмотров анкеты
    await db.create_or_update_user(
        candidate.user_id,
        profile_views=candidate.profile_views + 1
    )
    
    # Показываем анкету
    await show_user_profile(message, db, candidate.user_id, is_own=False, edit_message=True, for_swipe=True)

@router.callback_query(F.data.regexp(r"^like_\d+$"))
async def process_like(callback: CallbackQuery, db: Database):
    """Обработка лайка"""
    await callback.answer("❤️")
    
    user_id = callback.from_user.id
    target_user_id = int(callback.data.split("_")[1])
    
    # Создаем свайп и проверяем на матч
    is_match = await db.create_swipe(user_id, target_user_id, is_like=True)
    
    # Отправляем уведомление о лайке (только если это не матч)
    if not is_match:
        try:
            from aiogram import Bot
            from config import Config
            bot = Bot(token=Config.BOT_TOKEN)
            await db.send_like_notification(target_user_id, bot)
        except Exception as e:
            logger.error(f"Failed to send like notification: {e}")
    
    if is_match:
        # Получаем данные пользователей для генерации стартера разговора
        user = await db.get_user(user_id)
        target_user = await db.get_user(target_user_id)
        
        # Формируем ссылки на профили
        target_user_link = f"tg://user?id={target_user_id}"
        current_user_link = f"tg://user?id={user_id}"
        
        # Уведомляем о матче
        match_text = (
            f"🔥 <b>ЭТО МАТЧ!</b> 🔥\n\n"
            f"Вы понравились друг другу с <a href='{target_user_link}'>{target_user.name}</a>!\n\n"
            f"💬 <b>Для общения:</b>\n"
            f"• Нажми на имя {target_user.name} выше\n"
            f"• Или перейди к профилю: <a href='{target_user_link}'>@{target_user.name}</a>"
        )
        
        # Генерируем стартер разговора с AI
        if user and target_user:
            user_data = {
                'name': user.name,
                'age': user.age,
                'city': user.city,
                'bio': user.bio
            }
            target_data = {
                'name': target_user.name,
                'age': target_user.age,
                'city': target_user.city,
                'bio': target_user.bio
            }
            
            conversation_starter = await ai_helper.generate_conversation_starter(user_data, target_data)
            if conversation_starter:
                match_text += f"\n\n💡 <b>Идея для начала разговора:</b>\n<i>{conversation_starter}</i>"
        
        # Также отправляем уведомление второму пользователю
        try:
            match_text_for_target = (
                f"🔥 <b>ЭТО МАТЧ!</b> 🔥\n\n"
                f"Вы понравились друг другу с <a href='{current_user_link}'>{user.name}</a>!\n\n"
                f"💬 <b>Для общения:</b>\n"
                f"• Нажми на имя {user.name} выше\n"
                f"• Или перейди к профилю: <a href='{current_user_link}'>@{user.name}</a>"
            )
            
            if conversation_starter:
                match_text_for_target += f"\n\n💡 <b>Идея для начала разговора:</b>\n<i>{conversation_starter}</i>"
            
            # Отправляем уведомление второму пользователю через бота
            from aiogram import Bot
            from config import Config
            bot = Bot(token=Config.BOT_TOKEN)
            await bot.send_message(
                chat_id=target_user_id,
                text=match_text_for_target,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Failed to send match notification to user {target_user_id}: {e}")
        
        from utils.keyboards import get_back_to_menu_keyboard
        await callback.message.edit_text(
            match_text,
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard(),
            disable_web_page_preview=True
        )
    else:
        # Показываем следующую анкету
        await show_next_profile(callback.message, db, user_id)

@router.callback_query(F.data.regexp(r"^dislike_\d+$"))
async def process_dislike(callback: CallbackQuery, db: Database):
    """Обработка дизлайка"""
    await callback.answer("👎")
    
    user_id = callback.from_user.id
    target_user_id = int(callback.data.split("_")[1])
    
    # Создаем свайп
    await db.create_swipe(user_id, target_user_id, is_like=False)
    
    # Показываем следующую анкету
    await show_next_profile(callback.message, db, user_id)

@router.callback_query(F.data == "next_profile")
async def show_next_profile_callback(callback: CallbackQuery, db: Database):
    """Показать следующую анкету через кнопку (без сохранения как дислайк)"""
    await callback.answer("⏭️")
    
    user_id = callback.from_user.id
    
    # Просто показываем следующую анкету БЕЗ сохранения в базу
    # Этот пользователь может снова показаться в будущем
    await show_next_profile(callback.message, db, user_id)

@router.callback_query(F.data.startswith("report_"))
async def report_user(callback: CallbackQuery, db: Database):
    """Пожаловаться на пользователя"""
    await callback.answer()
    
    target_user_id = int(callback.data.split("_")[1])
    
    # TODO: Реализовать систему жалоб
    # Пока просто показываем сообщение
    await callback.message.edit_text(
        "📊 <b>Жалоба отправлена</b>\n\n"
        "Мы рассмотрим вашу жалобу в ближайшее время.\n"
        "Спасибо за помощь в поддержании безопасности сообщества!",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(has_profile=True)
    )
    
    logger.info(f"User {callback.from_user.id} reported user {target_user_id}")

def register_swipe_handlers(dp):
    """Регистрация обработчиков свайпов"""
    dp.include_router(router)
