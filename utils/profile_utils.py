"""Утилиты для работы с профилем"""
import math

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Вычисляет расстояние между двумя точками в километрах"""
    # Радиус Земли в километрах
    R = 6371.0
    
    # Переводим градусы в радианы
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Разности координат
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Формула гаверсинуса
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Расстояние в километрах
    distance = R * c
    return distance

def is_profile_complete(user) -> bool:
    """Проверяет, заполнен ли профиль пользователя полностью"""
    import logging
    logger = logging.getLogger(__name__)
    
    if not user:
        logger.info("Profile check: user is None")
        return False
    
    # Обязательные поля для полного профиля (включая bio)
    required_fields = [
        ("name", user.name),
        ("age", user.age),
        ("gender", user.gender),
        ("looking_for", user.looking_for),
        ("city", user.city),
        ("bio", user.bio)  # Теперь описание тоже обязательное
    ]
    
    missing_fields = []
    for field_name, field_value in required_fields:
        if field_value is None or str(field_value).strip() == "":
            missing_fields.append(field_name)
    
    is_complete = len(missing_fields) == 0
    logger.info(f"Profile completeness check: complete={is_complete}, missing_fields={missing_fields}")
    
    return is_complete

def get_missing_profile_fields(user) -> list:
    """Возвращает список незаполненных полей профиля"""
    if not user:
        return ["name", "age", "gender", "looking_for", "city", "bio"]
    
    missing = []
    
    if not user.name or str(user.name).strip() == "":
        missing.append("name")
    if not user.age:
        missing.append("age")
    if not user.gender or str(user.gender).strip() == "":
        missing.append("gender")
    if not user.looking_for or str(user.looking_for).strip() == "":
        missing.append("looking_for")
    if not user.city or str(user.city).strip() == "":
        missing.append("city")
    if not user.bio or str(user.bio).strip() == "":
        missing.append("bio")
    
    return missing
