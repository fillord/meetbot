import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # База данных
    DATABASE_URL = os.getenv('DATABASE_URL', 'meet_bot.db')
    
    # Настройки
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',') if os.getenv('ADMIN_IDS') else []))
    
    # Лимиты
    MAX_PHOTOS_PER_PROFILE = int(os.getenv('MAX_PHOTOS_PER_PROFILE', 5))
    MAX_BIO_LENGTH = int(os.getenv('MAX_BIO_LENGTH', 500))
    DAILY_SWIPES_LIMIT = int(os.getenv('DAILY_SWIPES_LIMIT', 50))
    
    # Возрастные ограничения
    MIN_AGE = 18
    MAX_AGE = 80
    
    # Расстояния для геопоиска (в км)
    DEFAULT_SEARCH_RADIUS = 50
    MAX_SEARCH_RADIUS = 200
