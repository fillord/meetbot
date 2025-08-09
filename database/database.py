import aiosqlite
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .models import User, UserPhoto, Swipe, Match, Chat, Message

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    name TEXT,
                    age INTEGER,
                    city TEXT,
                    bio TEXT,
                    gender TEXT,
                    looking_for TEXT,
                    latitude REAL,
                    longitude REAL,
                    is_active BOOLEAN DEFAULT 1,
                    is_premium BOOLEAN DEFAULT 0,
                    show_distance BOOLEAN DEFAULT 1,
                    show_age BOOLEAN DEFAULT 1,
                    show_location BOOLEAN DEFAULT 1,
                    notifications_enabled BOOLEAN DEFAULT 1,
                    search_radius INTEGER DEFAULT 50,
                    min_age INTEGER DEFAULT 18,
                    max_age INTEGER DEFAULT 35,
                    max_distance INTEGER DEFAULT 50,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    profile_views INTEGER DEFAULT 0,
                    likes_sent INTEGER DEFAULT 0,
                    likes_received INTEGER DEFAULT 0,
                    matches_count INTEGER DEFAULT 0
                )
            ''')
            
            # Таблица фотографий
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_photos (
                    photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    file_id TEXT NOT NULL,
                    file_unique_id TEXT NOT NULL,
                    order_num INTEGER DEFAULT 0,
                    is_main BOOLEAN DEFAULT 0,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица свайпов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS swipes (
                    swipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER,
                    to_user_id INTEGER,
                    is_like BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (to_user_id) REFERENCES users (user_id),
                    UNIQUE(from_user_id, to_user_id)
                )
            ''')
            
            # Таблица матчей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER,
                    user2_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user1_id) REFERENCES users (user_id),
                    FOREIGN KEY (user2_id) REFERENCES users (user_id),
                    UNIQUE(user1_id, user2_id)
                )
            ''')
            
            # Таблица чатов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_message_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (match_id) REFERENCES matches (match_id)
                )
            ''')
            
            # Таблица сообщений
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    from_user_id INTEGER,
                    message_text TEXT,
                    message_type TEXT DEFAULT 'text',
                    file_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0,
                    FOREIGN KEY (chat_id) REFERENCES chats (chat_id),
                    FOREIGN KEY (from_user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Миграция: добавляем новые поля для существующих пользователей
            try:
                await db.execute('ALTER TABLE users ADD COLUMN show_age BOOLEAN DEFAULT 1')
            except:
                pass  # Поле уже существует
            
            try:
                await db.execute('ALTER TABLE users ADD COLUMN show_location BOOLEAN DEFAULT 1')
            except:
                pass  # Поле уже существует
            
            try:
                await db.execute('ALTER TABLE users ADD COLUMN notifications_enabled BOOLEAN DEFAULT 1')
            except:
                pass  # Поле уже существует
            
            try:
                await db.execute('ALTER TABLE users ADD COLUMN search_radius INTEGER DEFAULT 50')
            except:
                pass  # Поле уже существует
            
            # Индексы для оптимизации
            await db.execute('CREATE INDEX IF NOT EXISTS idx_users_gender_age ON users(gender, age)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_users_location ON users(latitude, longitude)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_swipes_from_user ON swipes(from_user_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_swipes_to_user ON swipes(to_user_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id)')
            
            await db.commit()
            logger.info("База данных инициализирована")
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            if row:
                return User(**dict(row))
            return None
    
    async def create_or_update_user(self, user_id: int, **kwargs) -> User:
        """Создать или обновить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, существует ли пользователь
            existing_user = await self.get_user(user_id)
            
            if existing_user:
                # Обновляем существующего пользователя
                update_fields = []
                values = []
                for key, value in kwargs.items():
                    if hasattr(existing_user, key):
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                
                if update_fields:
                    update_fields.append("updated_at = ?")
                    values.append(datetime.now())
                    values.append(user_id)
                    
                    query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
                    await db.execute(query, values)
                    await db.commit()
                
                return await self.get_user(user_id)
            else:
                # Создаем нового пользователя
                kwargs.update({
                    'user_id': user_id,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'last_active': datetime.now()
                })
                
                fields = list(kwargs.keys())
                placeholders = ', '.join(['?' for _ in fields])
                query = f"INSERT INTO users ({', '.join(fields)}) VALUES ({placeholders})"
                
                await db.execute(query, list(kwargs.values()))
                await db.commit()
                
                return await self.get_user(user_id)
    
    async def update_last_active(self, user_id: int):
        """Обновить время последней активности пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE users SET last_active = ? WHERE user_id = ?',
                (datetime.now(), user_id)
            )
            await db.commit()
    
    async def get_users_for_swipe(self, user_id: int, limit: int = 10, exclude_user_id: int = None) -> List[User]:
        """Получить пользователей для свайпа с учетом геолокации (радиус 100км)"""
        user = await self.get_user(user_id)
        if not user:
            return []
        
        logger.info(f"Search for user {user_id}: gender={user.gender}, looking_for={user.looking_for}, age={user.age}")
        
        # Определяем возрастные ограничения
        min_age = getattr(user, 'min_age', 18) or 18
        max_age = getattr(user, 'max_age', 100) or 100
        
        logger.info(f"Age range: {min_age}-{max_age}")
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Если у пользователя есть координаты, используем геопоиск
            if user.latitude and user.longitude:
                logger.info(f"Using geo search with coordinates: lat={user.latitude}, lon={user.longitude}")
                
                if user.looking_for == 'both':
                    logger.info("Looking for both genders")
                    # Ищем всех пользователей независимо от пола
                    exclude_condition = ""
                    if exclude_user_id:
                        exclude_condition = f"AND user_id != {exclude_user_id}"
                    
                    query = f'''
                        SELECT * FROM (
                            SELECT *, 
                                   (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
                                    cos(radians(longitude) - radians(?)) + 
                                    sin(radians(?)) * sin(radians(latitude)))) AS distance
                            FROM users 
                            WHERE user_id != ? 
                            {exclude_condition}
                            AND is_active = 1
                            AND age BETWEEN ? AND ?
                            AND latitude IS NOT NULL 
                            AND longitude IS NOT NULL
                            AND user_id NOT IN (
                                SELECT to_user_id FROM swipes WHERE from_user_id = ?
                            )
                        ) subquery
                        WHERE distance <= 100
                        ORDER BY distance ASC, last_active DESC
                        LIMIT ?
                    '''
                    
                    logger.info(f"Executing query with params: lat={user.latitude}, lon={user.longitude}, user_id={user_id}, min_age={min_age}, max_age={max_age}, limit={limit}")
                    
                    cursor = await db.execute(query, (
                        user.latitude, user.longitude, user.latitude,  # для расчета расстояния
                        user_id,
                        min_age,
                        max_age,
                        user_id,
                        limit
                    ))
                else:
                    # Ищем пользователей конкретного пола
                    exclude_condition = f"AND user_id != {exclude_user_id}" if exclude_user_id else ""
                    query = f'''
                        SELECT * FROM (
                            SELECT *, 
                                   (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
                                    cos(radians(longitude) - radians(?)) + 
                                    sin(radians(?)) * sin(radians(latitude)))) AS distance
                            FROM users 
                            WHERE user_id != ? 
                            {exclude_condition}
                            AND is_active = 1
                            AND age BETWEEN ? AND ?
                            AND gender = ?
                            AND latitude IS NOT NULL 
                            AND longitude IS NOT NULL
                            AND user_id NOT IN (
                                SELECT to_user_id FROM swipes WHERE from_user_id = ?
                            )
                        ) subquery
                        WHERE distance <= 100
                        ORDER BY distance ASC, last_active DESC
                        LIMIT ?
                    '''
                    
                    cursor = await db.execute(query, (
                        user.latitude, user.longitude, user.latitude,  # для расчета расстояния
                        user_id,
                        min_age,
                        max_age,
                        user.looking_for,  # Исправлено: ищем тот пол, который хочет пользователь
                        user_id,
                        limit
                    ))
            else:
                # Если нет координат, используем обычный поиск
                if user.looking_for == 'both':
                    # Ищем всех пользователей независимо от пола
                    exclude_condition = f"AND user_id != {exclude_user_id}" if exclude_user_id else ""
                    query = f'''
                        SELECT * FROM users 
                        WHERE user_id != ? 
                        {exclude_condition}
                        AND is_active = 1
                        AND age BETWEEN ? AND ?
                        AND user_id NOT IN (
                            SELECT to_user_id FROM swipes WHERE from_user_id = ?
                        )
                        ORDER BY last_active DESC
                        LIMIT ?
                    '''
                    
                    cursor = await db.execute(query, (
                        user_id,
                        min_age,
                        max_age,
                        user_id,
                        limit
                    ))
                else:
                    # Ищем пользователей конкретного пола
                    exclude_condition = f"AND user_id != {exclude_user_id}" if exclude_user_id else ""
                    query = f'''
                        SELECT * FROM users 
                        WHERE user_id != ? 
                        {exclude_condition}
                        AND is_active = 1
                        AND age BETWEEN ? AND ?
                        AND gender = ?
                        AND user_id NOT IN (
                            SELECT to_user_id FROM swipes WHERE from_user_id = ?
                        )
                        ORDER BY last_active DESC
                        LIMIT ?
                    '''
                    
                    cursor = await db.execute(query, (
                        user_id,
                        min_age,
                        max_age,
                        user.looking_for,  # Исправлено: ищем тот пол, который хочет пользователь
                        user_id,
                        limit
                    ))
            
            rows = await cursor.fetchall()
            logger.info(f"Found {len(rows)} rows in database query")
            users = []
            for row in rows:
                row_dict = dict(row)
                logger.info(f"Processing user: {row_dict.get('user_id')} - {row_dict.get('name')}, distance: {row_dict.get('distance', 'N/A')}")
                # Удаляем поле distance из результата, если оно есть
                if 'distance' in row_dict:
                    del row_dict['distance']
                users.append(User(**row_dict))
            logger.info(f"Returning {len(users)} users for swipe")
            return users
    
    async def get_all_users_debug(self) -> List[User]:
        """Получить всех пользователей для отладки"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM users')
            rows = await cursor.fetchall()
            users = []
            for row in rows:
                users.append(User(**dict(row)))
            return users
    
    async def create_swipe(self, from_user_id: int, to_user_id: int, is_like: bool) -> bool:
        """Создать свайп и проверить на матч"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем свайп
            await db.execute(
                'INSERT OR IGNORE INTO swipes (from_user_id, to_user_id, is_like) VALUES (?, ?, ?)',
                (from_user_id, to_user_id, is_like)
            )
            
            # Обновляем статистику
            await db.execute(
                'UPDATE users SET likes_sent = likes_sent + 1 WHERE user_id = ?',
                (from_user_id,)
            )
            
            if is_like:
                await db.execute(
                    'UPDATE users SET likes_received = likes_received + 1 WHERE user_id = ?',
                    (to_user_id,)
                )
            
            # Проверяем на взаимную симпатию
            if is_like:
                cursor = await db.execute(
                    'SELECT 1 FROM swipes WHERE from_user_id = ? AND to_user_id = ? AND is_like = 1',
                    (to_user_id, from_user_id)
                )
                mutual_like = await cursor.fetchone()
                
                if mutual_like:
                    # Создаем матч
                    await db.execute(
                        'INSERT OR IGNORE INTO matches (user1_id, user2_id) VALUES (?, ?)',
                        (min(from_user_id, to_user_id), max(from_user_id, to_user_id))
                    )
                    
                    # Обновляем счетчик матчей
                    await db.execute(
                        'UPDATE users SET matches_count = matches_count + 1 WHERE user_id IN (?, ?)',
                        (from_user_id, to_user_id)
                    )
                    
                    await db.commit()
                    return True
            
            await db.commit()
            return False
    
    async def get_unread_likes_count(self, user_id: int) -> int:
        """Получить количество непросмотренных лайков"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                '''SELECT COUNT(*) FROM swipes 
                   WHERE to_user_id = ? AND is_like = 1 
                   AND from_user_id NOT IN (
                       SELECT to_user_id FROM swipes WHERE from_user_id = ? AND is_like = 1
                   )''',
                (user_id, user_id)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def send_like_notification(self, to_user_id: int, bot):
        """Отправить уведомление о лайке пользователю"""
        try:
            # Проверяем, включены ли уведомления у пользователя
            user = await self.get_user(to_user_id)
            if not user or not user.notifications_enabled:
                return False
            
            # Получаем количество непросмотренных лайков
            likes_count = await self.get_unread_likes_count(to_user_id)
            
            if likes_count == 0:
                return False
            
            # Формируем текст уведомления
            if likes_count == 1:
                text = "❤️ <b>Кто-то поставил тебе лайк!</b>\n\nПосмотреть можно в разделе «Лайки» 👀"
            else:
                # Склоняем число
                if likes_count == 2:
                    text = f"❤️ <b>{likes_count} человека поставили тебе лайк!</b>\n\nПосмотреть можно в разделе «Лайки» 👀"
                elif likes_count in [3, 4]:
                    text = f"❤️ <b>{likes_count} человека поставили тебе лайк!</b>\n\nПосмотреть можно в разделе «Лайки» 👀"
                else:
                    text = f"❤️ <b>{likes_count} человек поставили тебе лайк!</b>\n\nПосмотреть можно в разделе «Лайки» 👀"
            
            # Отправляем уведомление
            await bot.send_message(
                chat_id=to_user_id,
                text=text,
                parse_mode="HTML"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send like notification to user {to_user_id}: {e}")
            return False
    
    async def get_user_photos(self, user_id: int) -> List[UserPhoto]:
        """Получить фотографии пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM user_photos WHERE user_id = ? ORDER BY is_main DESC, order_num, uploaded_at',
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [UserPhoto(**dict(row)) for row in rows]
    
    async def add_user_photo(self, user_id: int, file_id: str, file_unique_id: str, is_main: bool = False) -> UserPhoto:
        """Добавить фотографию пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            # Если это главная фотография, убираем флаг у других
            if is_main:
                await db.execute(
                    'UPDATE user_photos SET is_main = 0 WHERE user_id = ?',
                    (user_id,)
                )
            
            # Получаем следующий порядковый номер
            cursor = await db.execute(
                'SELECT MAX(order_num) FROM user_photos WHERE user_id = ?',
                (user_id,)
            )
            max_order = await cursor.fetchone()
            next_order = (max_order[0] or 0) + 1
            
            # Добавляем фотографию
            cursor = await db.execute(
                'INSERT INTO user_photos (user_id, file_id, file_unique_id, order_num, is_main) VALUES (?, ?, ?, ?, ?)',
                (user_id, file_id, file_unique_id, next_order, is_main)
            )
            
            photo_id = cursor.lastrowid
            await db.commit()
            
            return UserPhoto(
                photo_id=photo_id,
                user_id=user_id,
                file_id=file_id,
                file_unique_id=file_unique_id,
                order_num=next_order,
                is_main=is_main,
                uploaded_at=datetime.now()
            )
    
    async def delete_user_photo(self, user_id: int, photo_id: int) -> bool:
        """Удалить фото пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, принадлежит ли фото пользователю
                cursor = await db.execute(
                    'SELECT order_num FROM user_photos WHERE photo_id = ? AND user_id = ?',
                    (photo_id, user_id)
                )
                photo = await cursor.fetchone()
                
                if not photo:
                    return False
                
                deleted_order = photo[0]
                
                # Удаляем фото
                await db.execute(
                    'DELETE FROM user_photos WHERE photo_id = ? AND user_id = ?',
                    (photo_id, user_id)
                )
                
                # Обновляем порядок оставшихся фото
                await db.execute(
                    'UPDATE user_photos SET order_num = order_num - 1 WHERE user_id = ? AND order_num > ?',
                    (user_id, deleted_order)
                )
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting photo: {e}")
            return False
    
    async def set_main_photo(self, user_id: int, photo_id: int) -> bool:
        """Установить главное фото"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Проверяем, принадлежит ли фото пользователю
                cursor = await db.execute(
                    'SELECT photo_id FROM user_photos WHERE photo_id = ? AND user_id = ?',
                    (photo_id, user_id)
                )
                photo = await cursor.fetchone()
                
                if not photo:
                    return False
                
                # Сбрасываем флаг is_main у всех фото пользователя
                await db.execute(
                    'UPDATE user_photos SET is_main = 0 WHERE user_id = ?',
                    (user_id,)
                )
                
                # Устанавливаем выбранное фото как главное и порядок = 0 (будет первым)
                await db.execute(
                    'UPDATE user_photos SET is_main = 1, order_num = 0 WHERE photo_id = ?',
                    (photo_id,)
                )
                
                # Получаем все остальные фото и переназначаем им порядок начиная с 1
                cursor = await db.execute(
                    'SELECT photo_id FROM user_photos WHERE user_id = ? AND photo_id != ? ORDER BY uploaded_at',
                    (user_id, photo_id)
                )
                other_photos = await cursor.fetchall()
                
                for i, (other_photo_id,) in enumerate(other_photos, 1):
                    await db.execute(
                        'UPDATE user_photos SET order_num = ? WHERE photo_id = ?',
                        (i, other_photo_id)
                    )
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting main photo: {e}")
            return False
    
    async def get_user_matches(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить матчи пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = '''
                SELECT m.*, 
                       u.name, u.age, u.city,
                       p.file_id as main_photo
                FROM matches m
                JOIN users u ON (u.user_id = CASE WHEN m.user1_id = ? THEN m.user2_id ELSE m.user1_id END)
                LEFT JOIN user_photos p ON p.user_id = u.user_id AND p.is_main = 1
                WHERE (m.user1_id = ? OR m.user2_id = ?) AND m.is_active = 1
                ORDER BY m.created_at DESC
            '''
            
            cursor = await db.execute(query, (user_id, user_id, user_id))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_incoming_likes(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить пользователей, которые лайкнули данного пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = '''
                SELECT u.user_id, u.name, u.age, u.city, u.bio, u.gender,
                       p.file_id as main_photo, s.created_at as liked_at
                FROM swipes s
                JOIN users u ON u.user_id = s.from_user_id
                LEFT JOIN user_photos p ON p.user_id = u.user_id AND p.is_main = 1
                WHERE s.to_user_id = ? 
                AND s.is_like = 1
                AND s.from_user_id NOT IN (
                    SELECT to_user_id FROM swipes 
                    WHERE from_user_id = ? AND is_like IS NOT NULL
                )
                ORDER BY s.created_at DESC
            '''
            
            cursor = await db.execute(query, (user_id, user_id))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def respond_to_like(self, from_user_id: int, to_user_id: int, is_like: bool) -> bool:
        """Ответить на лайк (создать свайп в ответ и проверить на матч)"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем ответный свайп
            await db.execute(
                'INSERT OR IGNORE INTO swipes (from_user_id, to_user_id, is_like) VALUES (?, ?, ?)',
                (from_user_id, to_user_id, is_like)
            )
            await db.commit()
            
            # Обновляем статистику отправителя
            await db.execute(
                'UPDATE users SET likes_sent = likes_sent + 1 WHERE user_id = ?',
                (from_user_id,)
            )
            
            # Если это лайк, обновляем статистику получателя
            if is_like:
                await db.execute(
                    'UPDATE users SET likes_received = likes_received + 1 WHERE user_id = ?',
                    (to_user_id,)
                )
                
                # Проверяем на взаимную симпатию (исходный лайк уже есть)
                cursor = await db.execute(
                    'SELECT 1 FROM swipes WHERE from_user_id = ? AND to_user_id = ? AND is_like = 1',
                    (to_user_id, from_user_id)
                )
                mutual_like = await cursor.fetchone()
                
                if mutual_like:
                    # Создаем матч
                    await db.execute(
                        'INSERT OR IGNORE INTO matches (user1_id, user2_id) VALUES (?, ?)',
                        (min(from_user_id, to_user_id), max(from_user_id, to_user_id))
                    )
                    
                    # Обновляем счетчик матчей
                    await db.execute(
                        'UPDATE users SET matches_count = matches_count + 1 WHERE user_id IN (?, ?)',
                        (from_user_id, to_user_id)
                    )
                    await db.commit()
                    return True  # Матч создан
            
            await db.commit()
            return False  # Матч не создан

    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получить расширенную статистику пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Базовая статистика пользователя
            cursor = await db.execute(
                '''SELECT profile_views, likes_sent, likes_received, matches_count, 
                          created_at, last_active FROM users WHERE user_id = ?''',
                (user_id,)
            )
            user_stats = await cursor.fetchone()
            
            if not user_stats:
                return {}
            
            # Количество сегодняшних лайков
            cursor = await db.execute(
                '''SELECT COUNT(*) as today_likes FROM swipes 
                   WHERE from_user_id = ? AND is_like = 1 
                   AND date(created_at) = date('now')''',
                (user_id,)
            )
            today_likes = (await cursor.fetchone())['today_likes']
            
            # Количество входящих лайков за последнюю неделю
            cursor = await db.execute(
                '''SELECT COUNT(*) as week_incoming FROM swipes 
                   WHERE to_user_id = ? AND is_like = 1 
                   AND created_at >= datetime('now', '-7 days')''',
                (user_id,)
            )
            week_incoming = (await cursor.fetchone())['week_incoming']
            
            # Общее количество фотографий
            cursor = await db.execute(
                '''SELECT COUNT(*) as photo_count FROM user_photos 
                   WHERE user_id = ?''',
                (user_id,)
            )
            photo_count = (await cursor.fetchone())['photo_count']
            
            # Количество активных матчей (упрощённый подсчёт)
            cursor = await db.execute(
                '''SELECT COUNT(*) as active_matches 
                   FROM matches m
                   WHERE m.user1_id = ? OR m.user2_id = ?''',
                (user_id, user_id)
            )
            active_matches = (await cursor.fetchone())['active_matches']
            
            # Успешность лайков (процент матчей от отправленных лайков)
            success_rate = 0
            if user_stats['likes_sent'] > 0:
                success_rate = round((user_stats['matches_count'] / user_stats['likes_sent']) * 100, 1)
            
            return {
                'profile_views': user_stats['profile_views'],
                'likes_sent': user_stats['likes_sent'],
                'likes_received': user_stats['likes_received'],
                'matches_count': user_stats['matches_count'],
                'today_likes': today_likes,
                'week_incoming': week_incoming,
                'photo_count': photo_count,
                'active_matches': active_matches,
                'success_rate': success_rate,
                'created_at': user_stats['created_at'],
                'last_active': user_stats['last_active']
            }

    async def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить топ пользователей по различным критериям"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Топ по популярности (больше всего лайков получено)
            cursor = await db.execute(
                '''SELECT name, likes_received, matches_count, profile_views
                   FROM users 
                   WHERE name IS NOT NULL AND likes_received > 0
                   ORDER BY likes_received DESC
                   LIMIT ?''',
                (limit,)
            )
            top_popular = await cursor.fetchall()
            
            # Топ по активности (больше всего лайков отправлено)
            cursor = await db.execute(
                '''SELECT name, likes_sent, matches_count, profile_views
                   FROM users 
                   WHERE name IS NOT NULL AND likes_sent > 0
                   ORDER BY likes_sent DESC
                   LIMIT ?''',
                (limit,)
            )
            top_active = await cursor.fetchall()
            
            # Топ по успешности (лучший процент матчей)
            cursor = await db.execute(
                '''SELECT name, likes_sent, matches_count, profile_views,
                          ROUND((CAST(matches_count AS FLOAT) / CAST(likes_sent AS FLOAT)) * 100, 1) as success_rate
                   FROM users 
                   WHERE name IS NOT NULL AND likes_sent >= 10
                   ORDER BY success_rate DESC
                   LIMIT ?''',
                (limit,)
            )
            top_successful = await cursor.fetchall()
            
            return {
                'popular': [dict(row) for row in top_popular],
                'active': [dict(row) for row in top_active],
                'successful': [dict(row) for row in top_successful]
            }

    async def get_profile_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Получить рекомендации по улучшению профиля"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Получаем данные пользователя
            cursor = await db.execute(
                '''SELECT name, age, bio, city, profile_views, likes_received, 
                          likes_sent, matches_count FROM users WHERE user_id = ?''',
                (user_id,)
            )
            user = await cursor.fetchone()
            
            if not user:
                return {}
            
            # Количество фотографий
            cursor = await db.execute(
                'SELECT COUNT(*) as photo_count FROM user_photos WHERE user_id = ?',
                (user_id,)
            )
            photo_count = (await cursor.fetchone())['photo_count']
            
            # Средние показатели других пользователей
            cursor = await db.execute(
                '''SELECT AVG(profile_views) as avg_views, 
                          AVG(likes_received) as avg_likes,
                          AVG(matches_count) as avg_matches
                   FROM users WHERE user_id != ? AND name IS NOT NULL''',
                (user_id,)
            )
            averages = await cursor.fetchone()
            
            recommendations = []
            
            # Анализ фотографий
            if photo_count == 0:
                recommendations.append("📸 Добавь хотя бы одну фотографию! Анкеты с фото получают в 10 раз больше лайков")
            elif photo_count < 3:
                recommendations.append(f"📸 У тебя {photo_count} фото. Добавь еще {3-photo_count}, чтобы выглядеть интереснее")
            
            # Анализ описания
            if not user['bio']:
                recommendations.append("✍️ Добавь описание о себе! Расскажи о своих увлечениях и интересах")
            elif len(user['bio']) < 50:
                recommendations.append("✍️ Расширь свое описание - расскажи больше о себе")
            
            # Анализ активности
            if user['profile_views'] < averages['avg_views']:
                recommendations.append("👀 Твоя анкета просматривается реже среднего. Попробуй обновить фото или описание")
            
            if user['likes_sent'] < 10:
                recommendations.append("💌 Будь активнее! Отправляй больше лайков, чтобы найти совпадения")
            
            # Анализ успешности
            success_rate = 0
            if user['likes_sent'] > 0:
                success_rate = (user['matches_count'] / user['likes_sent']) * 100
            
            if success_rate < 5 and user['likes_sent'] > 20:
                recommendations.append("🎯 Низкий процент совпадений. Попробуй улучшить фото или описание")
            
            # Анализ географии
            if not user['city']:
                recommendations.append("📍 Укажи город - это поможет найти людей рядом")
            
            return {
                'photo_count': photo_count,
                'bio_length': len(user['bio']) if user['bio'] else 0,
                'profile_views': user['profile_views'],
                'success_rate': round(success_rate, 1),
                'recommendations': recommendations,
                'avg_views': round(averages['avg_views'], 1) if averages['avg_views'] else 0,
                'avg_likes': round(averages['avg_likes'], 1) if averages['avg_likes'] else 0
            }

    async def get_users_in_radius(self, user_id: int, lat: float, lon: float, radius_km: int) -> List[Dict[str, Any]]:
        """Получить пользователей в радиусе от указанных координат"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = '''
                SELECT user_id, name, age, city, bio, latitude, longitude,
                       (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
                        cos(radians(longitude) - radians(?)) + 
                        sin(radians(?)) * sin(radians(latitude)))) AS distance
                FROM users 
                WHERE user_id != ? AND name IS NOT NULL AND latitude IS NOT NULL 
                AND longitude IS NOT NULL
                HAVING distance <= ?
                ORDER BY distance
            '''
            
            cursor = await db.execute(query, (lat, lon, lat, user_id, radius_km))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_recently_active_users(self, minutes: int = 30) -> List[Dict[str, Any]]:
        """Получить недавно активных пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = '''
                SELECT name, age, city, bio, last_active
                FROM users 
                WHERE name IS NOT NULL 
                AND last_active >= datetime('now', '-{} minutes')
                ORDER BY last_active DESC
            '''.format(minutes)
            
            cursor = await db.execute(query)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def search_users_by_city(self, city: str) -> List[Dict[str, Any]]:
        """Поиск пользователей по городу"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = '''
                SELECT name, age, city, bio
                FROM users 
                WHERE name IS NOT NULL AND city LIKE ?
                ORDER BY last_active DESC
            '''
            
            cursor = await db.execute(query, (f'%{city}%',))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def search_users_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Поиск пользователей по имени"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = '''
                SELECT name, age, city, bio
                FROM users 
                WHERE name IS NOT NULL AND name LIKE ?
                ORDER BY last_active DESC
            '''
            
            cursor = await db.execute(query, (f'%{name}%',))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_user_profile(self, user_id: int):
        """Полное удаление профиля пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Удаляем в правильном порядке (из-за внешних ключей)
                
                # 1. Удаляем сообщения чатов (через chat_id и from_user_id)
                await db.execute('''
                    DELETE FROM messages 
                    WHERE from_user_id = ? 
                    OR chat_id IN (
                        SELECT c.chat_id FROM chats c
                        JOIN matches m ON c.match_id = m.match_id
                        WHERE m.user1_id = ? OR m.user2_id = ?
                    )
                ''', (user_id, user_id, user_id))
                
                # 2. Удаляем чаты (через связь с matches)
                await db.execute('''
                    DELETE FROM chats 
                    WHERE match_id IN (
                        SELECT match_id FROM matches 
                        WHERE user1_id = ? OR user2_id = ?
                    )
                ''', (user_id, user_id))
                
                # 3. Удаляем матчи
                await db.execute('DELETE FROM matches WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
                
                # 4. Удаляем свайпы
                await db.execute('DELETE FROM swipes WHERE from_user_id = ? OR to_user_id = ?', (user_id, user_id))
                
                # 5. Удаляем фотографии
                await db.execute('DELETE FROM user_photos WHERE user_id = ?', (user_id,))
                
                # 6. Сбрасываем данные профиля пользователя (оставляем базовую запись)
                await db.execute('''
                    UPDATE users SET 
                        name = NULL,
                        age = NULL,
                        city = NULL,
                        bio = NULL,
                        gender = NULL,
                        looking_for = NULL,
                        latitude = NULL,
                        longitude = NULL,
                        is_active = 0,
                        show_distance = 1,
                        show_age = 1,
                        show_location = 1,
                        search_radius = 50,
                        min_age = 18,
                        max_age = 35,
                        max_distance = 50,
                        profile_views = 0,
                        likes_sent = 0,
                        likes_received = 0,
                        matches_count = 0,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                await db.commit()
                logger.info(f"User profile {user_id} deleted successfully")
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Error deleting user profile {user_id}: {e}")
                raise
