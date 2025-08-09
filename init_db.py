import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from config import Config

async def init_database():
    """Инициализация базы данных"""
    print("🗄️ Инициализация базы данных...")
    
    db = Database(Config.DATABASE_URL)
    await db.init_db()
    
    print("✅ База данных успешно инициализирована!")
    print(f"📁 Файл базы данных: {Config.DATABASE_URL}")
    
    # Можно добавить тестовые данные для разработки
    if Config.DEBUG:
        print("🧪 Режим отладки: добавляем тестовые данные...")
        await create_test_data(db)

async def create_test_data(db: Database):
    """Создание тестовых данных для разработки"""
    try:
        # Создаем тестового пользователя
        test_user_id = 123456789
        await db.create_or_update_user(
            user_id=test_user_id,
            username="testuser",
            first_name="Тест",
            name="Тестовый Пользователь",
            age=25,
            city="Москва",
            bio="Это тестовая анкета для проверки функциональности бота",
            gender="male",
            looking_for="female",
            is_active=True
        )
        
        print(f"✅ Создан тестовый пользователь с ID: {test_user_id}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")

if __name__ == "__main__":
    asyncio.run(init_database())
