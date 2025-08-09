#!/usr/bin/env python3
"""
Административные утилиты для управления ботом
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from config import Config

class AdminTools:
    def __init__(self):
        self.db = Database(Config.DATABASE_URL)
    
    async def get_stats(self):
        """Получить статистику бота"""
        print("📊 Статистика бота Meet Bot")
        print("=" * 40)
        
        # Подключаемся к БД напрямую для статистики
        import aiosqlite
        async with aiosqlite.connect(Config.DATABASE_URL) as db:
            # Общее количество пользователей
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await cursor.fetchone())[0]
            
            # Активные пользователи (заходили за последние 7 дней)
            week_ago = datetime.now() - timedelta(days=7)
            cursor = await db.execute(
                "SELECT COUNT(*) FROM users WHERE last_active > ?", 
                (week_ago,)
            )
            active_users = (await cursor.fetchone())[0]
            
            # Пользователи с заполненными анкетами
            cursor = await db.execute(
                "SELECT COUNT(*) FROM users WHERE name IS NOT NULL AND age IS NOT NULL"
            )
            profiles_filled = (await cursor.fetchone())[0]
            
            # Общее количество свайпов
            cursor = await db.execute("SELECT COUNT(*) FROM swipes")
            total_swipes = (await cursor.fetchone())[0]
            
            # Общее количество матчей
            cursor = await db.execute("SELECT COUNT(*) FROM matches WHERE is_active = 1")
            total_matches = (await cursor.fetchone())[0]
            
            # Фото в анкетах
            cursor = await db.execute("SELECT COUNT(*) FROM user_photos")
            total_photos = (await cursor.fetchone())[0]
            
            print(f"👥 Всего пользователей: {total_users}")
            print(f"✅ Активных за неделю: {active_users}")
            print(f"📝 Заполненных анкет: {profiles_filled}")
            print(f"👆 Всего свайпов: {total_swipes}")
            print(f"💖 Всего матчей: {total_matches}")
            print(f"📸 Всего фотографий: {total_photos}")
            
            if total_swipes > 0:
                match_rate = (total_matches * 2 / total_swipes) * 100  # *2 т.к. на матч нужно 2 свайпа
                print(f"💯 Процент матчей: {match_rate:.2f}%")
    
    async def list_recent_users(self, limit=10):
        """Показать недавних пользователей"""
        print(f"\n👥 Последние {limit} пользователей:")
        print("-" * 60)
        
        import aiosqlite
        async with aiosqlite.connect(Config.DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT user_id, username, first_name, name, age, city, created_at 
                   FROM users ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )
            
            users = await cursor.fetchall()
            for user in users:
                username = user['username'] or 'Нет username'
                name = user['name'] or user['first_name'] or 'Без имени'
                age = user['age'] or '?'
                city = user['city'] or 'Город не указан'
                created = user['created_at']
                
                print(f"ID: {user['user_id']} | @{username} | {name}, {age} | {city} | {created}")
    
    async def cleanup_old_data(self, days=30):
        """Очистка старых данных"""
        print(f"\n🧹 Очистка данных старше {days} дней...")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        import aiosqlite
        async with aiosqlite.connect(Config.DATABASE_URL) as db:
            # Удаляем старые свайпы неактивных пользователей
            cursor = await db.execute(
                """DELETE FROM swipes WHERE created_at < ? 
                   AND from_user_id IN (
                       SELECT user_id FROM users WHERE last_active < ?
                   )""",
                (cutoff_date, cutoff_date)
            )
            deleted_swipes = cursor.rowcount
            
            await db.commit()
            print(f"✅ Удалено старых свайпов: {deleted_swipes}")
    
    async def find_user(self, query):
        """Поиск пользователя по ID, username или имени"""
        print(f"\n🔍 Поиск пользователя: {query}")
        print("-" * 40)
        
        import aiosqlite
        async with aiosqlite.connect(Config.DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            
            # Пробуем найти по ID
            if query.isdigit():
                cursor = await db.execute(
                    "SELECT * FROM users WHERE user_id = ?",
                    (int(query),)
                )
            else:
                # Поиск по username или имени
                cursor = await db.execute(
                    """SELECT * FROM users 
                       WHERE username LIKE ? OR name LIKE ? OR first_name LIKE ?""",
                    (f"%{query}%", f"%{query}%", f"%{query}%")
                )
            
            users = await cursor.fetchall()
            
            if not users:
                print("❌ Пользователь не найден")
                return
            
            for user in users:
                print(f"ID: {user['user_id']}")
                print(f"Username: @{user['username'] or 'нет'}")
                print(f"Имя: {user['first_name']} ({user['name']})")
                print(f"Возраст: {user['age']} лет")
                print(f"Город: {user['city']}")
                print(f"Пол: {user['gender']}")
                print(f"Описание: {user['bio'][:100] if user['bio'] else 'Нет'}...")
                print(f"Активен: {user['is_active']}")
                print(f"Последний раз: {user['last_active']}")
                print("-" * 40)

async def main():
    """Главная функция админ-утилит"""
    admin = AdminTools()
    
    if len(sys.argv) < 2:
        print("🔧 Админ-утилиты Meet Bot")
        print("\nИспользование:")
        print("  python admin_utils.py stats          - Показать статистику")
        print("  python admin_utils.py users [N]      - Показать N последних пользователей")
        print("  python admin_utils.py cleanup [days] - Очистить данные старше N дней")
        print("  python admin_utils.py find <query>   - Найти пользователя")
        return
    
    command = sys.argv[1]
    
    if command == "stats":
        await admin.get_stats()
    
    elif command == "users":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        await admin.get_stats()
        await admin.list_recent_users(limit)
    
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        await admin.cleanup_old_data(days)
    
    elif command == "find":
        if len(sys.argv) < 3:
            print("❌ Укажите запрос для поиска")
            return
        query = sys.argv[2]
        await admin.find_user(query)
    
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    asyncio.run(main())
