import re
from typing import Optional, Tuple
from config import Config

def validate_age(age_input) -> Tuple[bool, Optional[int], str]:
    """
    Валидация возраста
    Возвращает: (is_valid, age, error_message)
    """
    try:
        # Преобразуем в строку, если получили число
        if isinstance(age_input, int):
            age = age_input
        else:
            age = int(str(age_input).strip())
        
        if age < Config.MIN_AGE:
            return False, None, f"Минимальный возраст: {Config.MIN_AGE} лет"
        
        if age > Config.MAX_AGE:
            return False, None, f"Максимальный возраст: {Config.MAX_AGE} лет"
        
        return True, age, ""
        
    except ValueError:
        return False, None, "Возраст должен быть числом"

def validate_name(name: str) -> Tuple[bool, Optional[str], str]:
    """
    Валидация имени
    Возвращает: (is_valid, cleaned_name, error_message)
    """
    if not name or not name.strip():
        return False, None, "Имя не может быть пустым"
    
    cleaned_name = name.strip()
    
    # Проверка длины
    if len(cleaned_name) < 2:
        return False, None, "Имя слишком короткое (минимум 2 символа)"
    
    if len(cleaned_name) > 50:
        return False, None, "Имя слишком длинное (максимум 50 символов)"
    
    # Проверка на допустимые символы (буквы, пробелы, дефисы)
    if not re.match(r'^[а-яёА-ЯЁa-zA-Z\s\-]+$', cleaned_name):
        return False, None, "Имя может содержать только буквы, пробелы и дефисы"
    
    # Проверка на цифры и спецсимволы
    if re.search(r'[0-9@#$%^&*()+={}[\]|\\:";\'<>?,./]', cleaned_name):
        return False, None, "Имя не должно содержать цифры и специальные символы"
    
    return True, cleaned_name, ""

def validate_bio(bio: str) -> Tuple[bool, Optional[str], str]:
    """
    Валидация описания анкеты
    Возвращает: (is_valid, cleaned_bio, error_message)
    """
    if not bio or not bio.strip():
        return False, None, "Описание не может быть пустым"
    
    cleaned_bio = bio.strip()
    
    # Проверка длины
    if len(cleaned_bio) < 10:
        return False, None, "Описание слишком короткое (минимум 10 символов)"
    
    if len(cleaned_bio) > Config.MAX_BIO_LENGTH:
        return False, None, f"Описание слишком длинное (максимум {Config.MAX_BIO_LENGTH} символов)"
    
    # Проверка на контактные данные
    contact_patterns = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Телефонные номера
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'@[A-Za-z0-9_]+',  # Упоминания в соцсетях
        r'(vk\.com|instagram\.com|t\.me|telegram\.me)',  # Ссылки на соцсети
        r'https?://[^\s]+',  # Любые ссылки
    ]
    
    for pattern in contact_patterns:
        if re.search(pattern, cleaned_bio, re.IGNORECASE):
            return False, None, "Описание не должно содержать контактные данные и ссылки"
    
    # Проверка на мат и неприличности (базовый список)
    inappropriate_words = [
        'блять', 'сука', 'пизда', 'хуй', 'ебать', 'говно', 'дерьмо',
        'секс', 'трах', 'ебля'  # можно расширить
    ]
    
    bio_lower = cleaned_bio.lower()
    for word in inappropriate_words:
        if word in bio_lower:
            return False, None, "Описание содержит неприемлемый контент"
    
    return True, cleaned_bio, ""

def validate_city(city: str) -> Tuple[bool, Optional[str], str]:
    """
    Валидация города
    Возвращает: (is_valid, cleaned_city, error_message)
    """
    if not city or not city.strip():
        return False, None, "Город не может быть пустым"
    
    cleaned_city = city.strip()
    
    # Проверка длины
    if len(cleaned_city) < 2:
        return False, None, "Название города слишком короткое"
    
    if len(cleaned_city) > 100:
        return False, None, "Название города слишком длинное"
    
    # Проверка на допустимые символы
    if not re.match(r'^[а-яёА-ЯЁa-zA-Z\s\-\.]+$', cleaned_city):
        return False, None, "Название города может содержать только буквы, пробелы, дефисы и точки"
    
    return True, cleaned_city, ""

def validate_gender(gender: str) -> Tuple[bool, Optional[str], str]:
    """
    Валидация пола
    Возвращает: (is_valid, gender, error_message)
    """
    valid_genders = ['male', 'female']
    
    if gender not in valid_genders:
        return False, None, "Некорректное значение пола"
    
    return True, gender, ""

def validate_looking_for(looking_for: str) -> Tuple[bool, Optional[str], str]:
    """
    Валидация предпочтений в поиске
    Возвращает: (is_valid, looking_for, error_message)
    """
    valid_preferences = ['male', 'female', 'both']
    
    if looking_for not in valid_preferences:
        return False, None, "Некорректное значение предпочтений"
    
    return True, looking_for, ""

def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """
    Валидация координат
    Возвращает: (is_valid, error_message)
    """
    if not (-90 <= latitude <= 90):
        return False, "Некорректная широта"
    
    if not (-180 <= longitude <= 180):
        return False, "Некорректная долгота"
    
    return True, ""

def validate_search_radius(radius: int) -> Tuple[bool, Optional[int], str]:
    """
    Валидация радиуса поиска
    Возвращает: (is_valid, radius, error_message)
    """
    if radius < 1:
        return False, None, "Радиус поиска должен быть больше 0"
    
    if radius > Config.MAX_SEARCH_RADIUS:
        return False, None, f"Максимальный радиус поиска: {Config.MAX_SEARCH_RADIUS} км"
    
    return True, radius, ""

def validate_age_range(min_age: int, max_age: int) -> Tuple[bool, str]:
    """
    Валидация возрастного диапазона
    Возвращает: (is_valid, error_message)
    """
    if min_age < Config.MIN_AGE:
        return False, f"Минимальный возраст: {Config.MIN_AGE} лет"
    
    if max_age > Config.MAX_AGE:
        return False, f"Максимальный возраст: {Config.MAX_AGE} лет"
    
    if min_age >= max_age:
        return False, "Минимальный возраст должен быть меньше максимального"
    
    if max_age - min_age > 50:
        return False, "Слишком большой возрастной диапазон (максимум 50 лет)"
    
    return True, ""

def sanitize_text(text: str) -> str:
    """
    Очистка текста от потенциально опасных символов
    """
    if not text:
        return ""
    
    # Удаляем HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    
    # Удаляем символы, которые могут использоваться для инъекций
    text = re.sub(r'[<>"\']', '', text)
    
    return text.strip()

def is_valid_file_id(file_id: str) -> bool:
    """
    Проверка валидности file_id от Telegram
    """
    if not file_id or not isinstance(file_id, str):
        return False
    
    # Telegram file_id имеет определенный формат
    if len(file_id) < 10 or len(file_id) > 200:
        return False
    
    # Должен содержать только допустимые символы
    if not re.match(r'^[A-Za-z0-9_-]+$', file_id):
        return False
    
    return True
