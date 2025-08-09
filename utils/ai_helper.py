from typing import Optional, Dict, Any
import logging
from config import Config

logger = logging.getLogger(__name__)

class AIHelper:
    def __init__(self):
        self.client = None
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.warning("OpenAI package not found. AI features will be disabled.")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI API key not found. AI features will be disabled.")
    
    async def improve_bio_with_ai(self, current_bio: str, user_data: Dict[str, Any]) -> Optional[str]:
        """Улучшить описание анкеты с помощью AI"""
        if not self.client:
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
            
            response = self.client.chat.completions.create(
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
        if not self.client:
            return None
        
        try:
            prompt = f"""
            Создай естественное начало разговора между двумя людьми, которые понравились друг другу:
            
            Пользователь 1: {user1_data.get('name', 'Имя не указано')}, {user1_data.get('age', 'возраст не указан')} лет
            О себе: {user1_data.get('bio', 'описание не указано')}
            
            Пользователь 2: {user2_data.get('name', 'Имя не указано')}, {user2_data.get('age', 'возраст не указан')} лет  
            О себе: {user2_data.get('bio', 'описание не указано')}
            
            Создай несколько (2-3) вариантов первого сообщения, которое первый пользователь мог бы отправить второму.
            
            Требования:
            - Дружелюбный и искренний тон
            - Опирайся на информацию из анкет
            - Не слишком формально
            - Интересный вопрос или комментарий
            
            Формат ответа:
            1. [первый вариант]
            2. [второй вариант]
            3. [третий вариант]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )
            
            starters = response.choices[0].message.content.strip()
            return starters
            
        except Exception as e:
            logger.error(f"Error generating conversation starter: {e}")
            return None
    
    async def check_content_safety(self, text: str) -> bool:
        """Проверить контент на безопасность"""
        if not self.client:
            # Базовая проверка без AI
            forbidden_words = ['sex', 'секс', 'интим', 'nsfw', 'porn', 'порно']
            text_lower = text.lower()
            return not any(word in text_lower for word in forbidden_words)
        
        try:
            prompt = f"""
            Проверь следующий текст на уместность для приложения знакомств:
            
            "{text}"
            
            Неуместно если содержит:
            - Сексуальный контент
            - Оскорбления
            - Дискриминацию  
            - Спам или рекламу
            - Контактную информацию (телефон, email, соцсети)
            
            Ответь только "ДА" если текст уместен, или "НЕТ" если неуместен.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "ДА"
            
        except Exception as e:
            logger.error(f"Error checking content: {e}")
            # Fallback к базовой проверке
            forbidden_words = ['sex', 'секс', 'интим', 'nsfw', 'porn', 'порно']
            text_lower = text.lower()
            return not any(word in text_lower for word in forbidden_words)
    
    async def suggest_profile_improvements(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Предложить улучшения для профиля"""
        if not self.client:
            return None
        
        try:
            prompt = f"""
            Проанализируй анкету пользователя и дай советы по улучшению:
            
            Имя: {user_data.get('name', 'не указано')}
            Возраст: {user_data.get('age', 'не указан')}
            Пол: {user_data.get('gender', 'не указан')}
            Город: {user_data.get('location', 'не указан')}
            О себе: {user_data.get('bio', 'не указано')}
            Количество фото: {user_data.get('photo_count', 0)}
            
            Дай 2-3 конкретных совета как улучшить анкету для большего успеха в знакомствах.
            
            Фокусируйся на:
            - Качество описания
            - Количество и качество фото
            - Заполненность профиля
            
            Будь конструктивным и дружелюбным.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            suggestions = response.choices[0].message.content.strip()
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating profile suggestions: {e}")
            return None

# Создаем глобальный экземпляр
ai_helper = AIHelper()
