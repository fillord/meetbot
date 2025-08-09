from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database
from utils.keyboards import get_verification_keyboard, get_back_to_menu_keyboard
import random
import asyncio
import logging

logger = logging.getLogger(__name__)
router = Router()

class VerificationStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_code = State()

# Временное хранение кодов верификации (в продакшене использовать Redis)
verification_codes = {}

@router.callback_query(F.data == "verify_phone")
async def start_phone_verification(callback: CallbackQuery, state: FSMContext):
    """Начать верификацию номера телефона"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = await callback.message.bot.get_me()
    
    verification_text = (
        "📱 <b>Верификация номера телефона</b>\n\n"
        "Для повышения безопасности и доверия к твоему профилю "
        "подтверди свой номер телефона.\n\n"
        "🔒 <b>Преимущества верификации:</b>\n"
        "• Бейдж \"Подтвержден\" в профиле\n"
        "• Повышенное доверие других пользователей\n"
        "• Защита от фейковых аккаунтов\n"
        "• Приоритет в поиске\n\n"
        "Нажми кнопку ниже, чтобы поделиться номером:"
    )
    
    await callback.message.edit_text(
        verification_text,
        parse_mode="HTML",
        reply_markup=get_verification_keyboard()
    )
    await state.set_state(VerificationStates.waiting_for_phone)

@router.message(VerificationStates.waiting_for_phone, F.contact)
async def process_phone_number(message: Message, state: FSMContext, db: Database):
    """Обработка полученного номера телефона"""
    contact = message.contact
    user_id = message.from_user.id
    
    # Проверяем, что пользователь отправил свой номер
    if contact.user_id != user_id:
        await message.answer(
            "❌ Пожалуйста, отправь свой собственный номер телефона",
            reply_markup=get_verification_keyboard()
        )
        return
    
    phone_number = contact.phone_number
    
    # Проверяем, не верифицирован ли уже этот номер
    existing_user = await db.get_user_by_phone(phone_number)
    if existing_user and existing_user.user_id != user_id:
        await message.answer(
            "❌ Этот номер уже используется другим аккаунтом",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
    
    # Генерируем код верификации
    verification_code = random.randint(100000, 999999)
    verification_codes[user_id] = {
        'code': verification_code,
        'phone': phone_number,
        'attempts': 0
    }
    
    # В реальном проекте здесь была бы отправка SMS
    # Для демонстрации просто показываем код пользователю
    await message.answer(
        f"📩 <b>Код верификации отправлен!</b>\n\n"
        f"Код: <code>{verification_code}</code>\n\n"
        f"<i>В реальном приложении код придет по SMS на номер {phone_number}</i>\n\n"
        f"Введи полученный код:",
        parse_mode="HTML",
        reply_markup=get_back_to_menu_keyboard()
    )
    
    await state.set_state(VerificationStates.waiting_for_code)
    
    # Автоматически удаляем код через 10 минут
    asyncio.create_task(cleanup_verification_code(user_id))

@router.message(VerificationStates.waiting_for_code)
async def process_verification_code(message: Message, state: FSMContext, db: Database):
    """Обработка кода верификации"""
    user_id = message.from_user.id
    entered_code = message.text.strip()
    
    if user_id not in verification_codes:
        await message.answer(
            "❌ Код верификации истек. Попробуй еще раз",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
    
    verification_data = verification_codes[user_id]
    verification_data['attempts'] += 1
    
    # Проверяем количество попыток
    if verification_data['attempts'] > 3:
        del verification_codes[user_id]
        await message.answer(
            "❌ Превышено количество попыток. Попробуй верификацию заново",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
    
    # Проверяем код
    if entered_code != str(verification_data['code']):
        remaining_attempts = 3 - verification_data['attempts']
        await message.answer(
            f"❌ Неверный код. Осталось попыток: {remaining_attempts}\n"
            f"Попробуй еще раз:",
            reply_markup=get_back_to_menu_keyboard()
        )
        return
    
    # Код верный - сохраняем верификацию
    phone_number = verification_data['phone']
    await db.verify_user_phone(user_id, phone_number)
    
    # Удаляем использованный код
    del verification_codes[user_id]
    await state.clear()
    
    success_text = (
        "✅ <b>Номер телефона подтвержден!</b>\n\n"
        f"📱 Твой номер {phone_number} успешно верифицирован\n\n"
        "🎉 <b>Что изменилось:</b>\n"
        "• В профиле появился бейдж \"Подтвержден\"\n"
        "• Твой профиль стал более надежным\n"
        "• Повысился приоритет в поиске\n\n"
        "Спасибо за верификацию! 🙏"
    )
    
    await message.answer(
        success_text,
        parse_mode="HTML",
        reply_markup=get_back_to_menu_keyboard()
    )

@router.message(VerificationStates.waiting_for_phone)
async def invalid_phone_input(message: Message):
    """Обработка неверного ввода при ожидании номера"""
    await message.answer(
        "❌ Пожалуйста, используй кнопку для отправки номера телефона",
        reply_markup=get_verification_keyboard()
    )

async def cleanup_verification_code(user_id: int):
    """Удалить код верификации через 10 минут"""
    await asyncio.sleep(600)  # 10 минут
    if user_id in verification_codes:
        del verification_codes[user_id]

def register_verification_handlers(dp):
    """Регистрация обработчиков верификации"""
    dp.include_router(router)
