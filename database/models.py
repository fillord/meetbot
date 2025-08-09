from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    """Модель пользователя"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Данные анкеты
    name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None  # 'male', 'female'
    looking_for: Optional[str] = None  # 'male', 'female', 'both'
    
    # Геолокация
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Настройки
    is_active: bool = True
    is_premium: bool = False
    show_distance: bool = True
    show_age: bool = True
    show_location: bool = True
    notifications_enabled: bool = True
    search_radius: int = 50
    min_age: int = 18
    max_age: int = 35
    max_distance: int = 50
    
    # Служебные поля
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Статистика
    profile_views: int = 0
    likes_sent: int = 0
    likes_received: int = 0
    matches_count: int = 0

@dataclass
class UserPhoto:
    """Модель фотографии пользователя"""
    photo_id: int
    user_id: int
    file_id: str
    file_unique_id: str
    order_num: int = 0
    is_main: bool = False
    uploaded_at: datetime = field(default_factory=datetime.now)

@dataclass
class Swipe:
    """Модель свайпа (лайк/дизлайк)"""
    swipe_id: int
    from_user_id: int
    to_user_id: int
    is_like: bool
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Match:
    """Модель матча (взаимная симпатия)"""
    match_id: int
    user1_id: int
    user2_id: int
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class Chat:
    """Модель чата"""
    chat_id: int
    match_id: int
    created_at: datetime = field(default_factory=datetime.now)
    last_message_at: Optional[datetime] = None
    is_active: bool = True

@dataclass
class Message:
    """Модель сообщения в чате"""
    message_id: int
    chat_id: int
    from_user_id: int
    message_text: Optional[str] = None
    message_type: str = 'text'  # 'text', 'photo', 'sticker', etc.
    file_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_read: bool = False
