from openai import OpenAI
import logging
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class AIHelper:
    def __init__(self):
        if Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OpenAI API key not found. AI features will be disabled.")
    
    async def improve_bio_with_ai(self, current_bio: str, user_data: Dict[str, Any]) -> Optional[str]:
        """Улучшить описание анкеты с помощью AI"""
        if not Config.OPENAI_API_KEY:
            return None
        
        try:
            prompt = f"""
            Ты помощник для улучшения анкет в приложении знакомств. 
            
            Пользователь: {user_data.get('name', 'Имя не указано')}, {user_data.get('age', 'возраст не указан')} лет, {user_data.get('city', 'город не указан')}
            
            Текущее описание: "{current_bio}"
            
            Задача: Переписать описание так, чтобы оно было:
            - Привлекательным и интересным
            - Естественным и не навязчивым  
            - Максимум 3-4 предложения
            - Отражало личность человека
            - Побуждало к знакомству
            
            Избегай:
            - Банальных фраз
            - Слишком длинных текстов
            - Хвастовства
            - Негатива
            
            Верни только улучшенный текст без дополнительных комментариев.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            improved_bio = response.choices[0].message.content.strip()
            return improved_bio
            
        except Exception as e:
            logger.error(f"Error improving bio with AI: {e}")
            return None
    
    async def generate_conversation_starter(self, user1_data: Dict[str, Any], user2_data: Dict[str, Any]) -> Optional[str]:
        """Сгенерировать начало разговора для матча"""
        if not Config.OPENAI_API_KEY:
            return None
        
        try:
            prompt = f"""
            Ты помощник для создания начальных сообщений в приложении знакомств.
            
            Пользователь 1: {user1_data.get('name')}, {user1_data.get('age')} лет, {user1_data.get('city')}
            Описание: {user1_data.get('bio', 'Описание отсутствует')}
            
            Пользователь 2: {user2_data.get('name')}, {user2_data.get('age')} лет, {user2_data.get('city')}
            Описание: {user2_data.get('bio', 'Описание отсутствует')}
            
            Создай естественное и дружелюбное первое сообщение от пользователя 1 к пользователю 2.
            
            Требования:
            - Персонализированное (упомяни что-то из анкеты)
            - Не слишком длинное (1-2 предложения)
            - Располагающее к ответу
            - Не банальное "Привет, как дела?"
            - Позитивное и легкое
            
            Верни только текст сообщения без дополнительных комментариев.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            
            starter = response.choices[0].message.content.strip()
            return starter
            
        except Exception as e:
            logger.error(f"Error generating conversation starter: {e}")
            return None
    
    async def check_content_appropriateness(self, text: str) -> Dict[str, Any]:
        """Проверить контент на соответствие правилам"""
        if not Config.OPENAI_API_KEY:
            return {"is_appropriate": True, "reason": ""}
        
        try:
            prompt = f"""
            Проверь следующий текст на соответствие правилам приложения знакомств:
            
            Текст: "{text}"
            
            Проверь на:
            - Оскорбления и мат
            - Сексуальный контент
            - Контактные данные (телефон, email, соцсети)
            - Реклама и спам
            - Негативный контент
            
            Ответь в формате:
            ПОДХОДИТ - если текст соответствует правилам
            НЕ ПОДХОДИТ: [причина] - если текст нарушает правила
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            if result.startswith("ПОДХОДИТ"):
                return {"is_appropriate": True, "reason": ""}
            else:
                reason = result.replace("НЕ ПОДХОДИТ:", "").strip()
                return {"is_appropriate": False, "reason": reason}
                
        except Exception as e:
            logger.error(f"Error checking content: {e}")
            return {"is_appropriate": True, "reason": ""}
    
    async def generate_profile_suggestions(self, partial_data: Dict[str, Any]) -> Dict[str, str]:
        """Сгенерировать предложения для заполнения анкеты"""
        if not Config.OPENAI_API_KEY:
            return {}
        
        try:
            prompt = f"""
            Пользователь создает анкету для знакомств. 
            Данные: {partial_data}
            
            Предложи 3 варианта описания "О себе" для этого пользователя.
            Каждый вариант должен быть:
            - Уникальным по стилю (веселый/серьезный/творческий)
            - 2-3 предложения
            - Привлекательным
            - Подходящим для возраста и пола
            
            Формат ответа:
            1. [текст варианта 1]
            2. [текст варианта 2]  
            3. [текст варианта 3]
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.8
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            
            # Парсим варианты
            suggestions = {}
            lines = suggestions_text.split('\n')
            for i, line in enumerate(lines, 1):
                if line.strip() and f"{i}." in line:
                    text = line.split(f"{i}.", 1)[1].strip()
                    suggestions[f"option_{i}"] = text
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating profile suggestions: {e}")
            return {}

# Создаем единственный экземпляр
ai_helper = AIHelper()

# Экспортируемые функции для удобства
async def improve_bio_with_ai(bio: str, user_data: Dict[str, Any]) -> Optional[str]:
    return await ai_helper.improve_bio_with_ai(bio, user_data)

async def generate_conversation_starter(user1: Dict[str, Any], user2: Dict[str, Any]) -> Optional[str]:
    return await ai_helper.generate_conversation_starter(user1, user2)

async def check_content_appropriateness(text: str) -> Dict[str, Any]:
    return await ai_helper.check_content_appropriateness(text)

async def generate_profile_suggestions(data: Dict[str, Any]) -> Dict[str, str]:
    return await ai_helper.generate_profile_suggestions(data)
