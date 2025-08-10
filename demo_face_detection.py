#!/usr/bin/env python3
"""
Демонстрация детекции лиц для тестирования
"""

import asyncio
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.face_detection import detect_faces_opencv, detect_faces_pil_basic, OPENCV_AVAILABLE
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_with_local_image(image_path: str):
    """Тест с локальным изображением"""
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        logger.info(f"📸 Тестирую изображение: {image_path}")
        logger.info(f"📊 Размер файла: {len(image_bytes)} байт")
        
        if OPENCV_AVAILABLE:
            has_faces, face_count = detect_faces_opencv(image_bytes)
            logger.info(f"🔍 OpenCV: найдено {face_count} лиц")
            
            if has_faces:
                if face_count == 1:
                    logger.info("✅ Идеально! Одно лицо обнаружено")
                else:
                    logger.info(f"⚠️ Слишком много лиц: {face_count}")
            else:
                logger.info("❌ Лица не обнаружены")
        else:
            logger.error("❌ OpenCV недоступен")
        
        # Базовая проверка
        is_valid, score = detect_faces_pil_basic(image_bytes)
        logger.info(f"📋 Базовая проверка: {'✅ Пройдена' if is_valid else '❌ Не пройдена'}")
        
    except FileNotFoundError:
        logger.error(f"❌ Файл не найден: {image_path}")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

def demo_requirements():
    """Показать требования к фото"""
    print("📋 Требования к фотографиям в Meet Bot:")
    print("   ✅ Четко видное лицо")
    print("   ✅ Один человек на фото") 
    print("   ✅ Хорошее освещение")
    print("   ✅ Размер файла до 10MB")
    print("   ✅ Форматы: JPEG, PNG, WEBP")
    print("   ✅ Минимальный размер: 100x100px")
    print("   ✅ Соотношение сторон не более 3:1")
    print()

if __name__ == "__main__":
    print("🔍 Демонстрация детекции лиц Meet Bot")
    print("=" * 50)
    
    demo_requirements()
    
    if len(sys.argv) > 1:
        # Тест с указанным файлом
        image_path = sys.argv[1]
        test_with_local_image(image_path)
    else:
        print("💡 Использование:")
        print(f"   {sys.argv[0]} <путь_к_изображению>")
        print()
        print("📝 Примеры:")
        print(f"   {sys.argv[0]} photo.jpg")
        print(f"   {sys.argv[0]} /path/to/selfie.png")
        print()
        
        # Проверим доступность OpenCV
        if OPENCV_AVAILABLE:
            print("✅ OpenCV доступен - детекция лиц активна")
        else:
            print("⚠️ OpenCV недоступен - используется базовая проверка")
        
        # Покажем статус системы
        try:
            import cv2
            print(f"📦 Версия OpenCV: {cv2.__version__}")
        except:
            print("❌ OpenCV не установлен")
            
        try:
            from PIL import Image
            print(f"📦 Pillow доступен")
        except:
            print("❌ Pillow не установлен")
