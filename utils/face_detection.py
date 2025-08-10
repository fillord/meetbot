import io
import asyncio
import aiohttp
from PIL import Image
import cv2
import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Загружаем Haar каскад для детекции лиц
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    OPENCV_AVAILABLE = True
except Exception as e:
    logger.error(f"OpenCV not available: {e}")
    OPENCV_AVAILABLE = False

async def download_photo(bot, file_id: str) -> Optional[bytes]:
    """Скачивает фото по file_id"""
    try:
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        
        # Получаем URL для скачивания
        bot_token = bot.token
        download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"Failed to download photo: HTTP {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error downloading photo: {e}")
        return None

def detect_faces_opencv(image_bytes: bytes) -> Tuple[bool, int]:
    """
    Детекция лиц с помощью OpenCV
    
    Returns:
        Tuple[bool, int]: (есть ли лица, количество лиц)
    """
    try:
        # Конвертируем bytes в numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.error("Failed to decode image")
            return False, 0
        
        # Конвертируем в градации серого для детекции
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Детектируем лица
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        face_count = len(faces)
        has_faces = face_count > 0
        
        logger.info(f"Detected {face_count} faces using OpenCV")
        return has_faces, face_count
        
    except Exception as e:
        logger.error(f"Error in OpenCV face detection: {e}")
        return False, 0

def detect_faces_pil_basic(image_bytes: bytes) -> Tuple[bool, int]:
    """
    Базовая проверка изображения с помощью PIL
    Проверяет основные характеристики изображения
    
    Returns:
        Tuple[bool, int]: (подходящее ли изображение, примерная оценка)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Проверяем размер изображения
        width, height = image.size
        
        # Минимальные требования к размеру
        if width < 100 or height < 100:
            logger.info("Image too small")
            return False, 0
        
        # Проверяем формат
        if image.format not in ['JPEG', 'PNG', 'WEBP']:
            logger.info(f"Unsupported format: {image.format}")
            return False, 0
        
        # Проверяем соотношение сторон (не слишком вытянутое)
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 3:
            logger.info(f"Aspect ratio too extreme: {aspect_ratio}")
            return False, 0
        
        # Базовая проверка пройдена
        logger.info("Basic image validation passed")
        return True, 1
        
    except Exception as e:
        logger.error(f"Error in PIL basic validation: {e}")
        return False, 0

async def detect_faces_in_photo(bot, file_id: str) -> Tuple[bool, str]:
    """
    Основная функция для детекции лиц в фото
    
    Args:
        bot: Bot instance
        file_id: Telegram file ID
        
    Returns:
        Tuple[bool, str]: (результат проверки, сообщение об ошибке/успехе)
    """
    try:
        # Скачиваем фото
        image_bytes = await download_photo(bot, file_id)
        if not image_bytes:
            return False, "❌ Не удалось загрузить фото"
        
        # Проверяем размер файла (максимум 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            return False, "❌ Фото слишком большое (максимум 10MB)"
        
        # Пробуем OpenCV детекцию лиц
        if OPENCV_AVAILABLE:
            has_faces, face_count = detect_faces_opencv(image_bytes)
            
            if has_faces:
                if face_count == 1:
                    return True, "✅ Обнаружено лицо на фото"
                else:
                    return False, f"❌ На фото должно быть только одно лицо (обнаружено: {face_count})"
            else:
                return False, "❌ На фото не обнаружено лицо. Загрузи фото где четко видно твое лицо"
        
        # Если OpenCV недоступен, используем базовую проверку
        else:
            logger.warning("OpenCV not available, using basic image validation")
            is_valid, _ = detect_faces_pil_basic(image_bytes)
            
            if is_valid:
                return True, "✅ Фото принято (базовая проверка)"
            else:
                return False, "❌ Фото не подходит. Убедись что это качественное фото"
    
    except Exception as e:
        logger.error(f"Error in face detection: {e}")
        return False, "❌ Ошибка при обработке фото"

async def validate_profile_photo(bot, file_id: str, is_main_photo: bool = True) -> Tuple[bool, str]:
    """
    Валидация фото для профиля
    
    Args:
        bot: Bot instance  
        file_id: Telegram file ID
        is_main_photo: Является ли главным фото (для главного фото требования строже)
        
    Returns:
        Tuple[bool, str]: (результат валидации, сообщение)
    """
    # Для главного фото требуем обязательную детекцию лица
    if is_main_photo:
        return await detect_faces_in_photo(bot, file_id)
    
    # Для дополнительных фото можем быть менее строгими
    has_face, message = await detect_faces_in_photo(bot, file_id)
    
    if has_face:
        return True, message
    else:
        # Для дополнительных фото допускаем, но предупреждаем
        try:
            image_bytes = await download_photo(bot, file_id)
            if image_bytes:
                is_valid, _ = detect_faces_pil_basic(image_bytes)
                if is_valid:
                    return True, "⚠️ Фото принято, но лучше загружать фото с лицом"
        except:
            pass
        
        return False, message
