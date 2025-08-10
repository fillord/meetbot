#!/usr/bin/env python3
"""
Тест детекции лиц для Meet Bot
"""

import asyncio
import aiohttp
from utils.face_detection import detect_faces_opencv, detect_faces_pil_basic
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_face_detection():
    """Тест функции детекции лиц"""
    
    # URL примера фото для тестирования (можно использовать любое доступное фото в интернете)
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/256px-Vd-Orig.png"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_image_url) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    logger.info(f"Downloaded test image: {len(image_bytes)} bytes")
                    
                    # Тест OpenCV детекции
                    try:
                        has_faces_cv, face_count_cv = detect_faces_opencv(image_bytes)
                        logger.info(f"OpenCV result: faces={has_faces_cv}, count={face_count_cv}")
                    except Exception as e:
                        logger.error(f"OpenCV test failed: {e}")
                    
                    # Тест базовой валидации PIL
                    try:
                        is_valid_pil, score_pil = detect_faces_pil_basic(image_bytes)
                        logger.info(f"PIL validation result: valid={is_valid_pil}, score={score_pil}")
                    except Exception as e:
                        logger.error(f"PIL test failed: {e}")
                        
                else:
                    logger.error(f"Failed to download test image: HTTP {response.status}")
                    
    except Exception as e:
        logger.error(f"Test failed: {e}")

def test_opencv_availability():
    """Проверка доступности OpenCV"""
    try:
        import cv2
        import numpy as np
        logger.info("OpenCV and NumPy are available")
        
        # Попробуем загрузить каскад
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            logger.error("Failed to load Haar cascade")
        else:
            logger.info("Haar cascade loaded successfully")
            
    except ImportError as e:
        logger.error(f"OpenCV not available: {e}")
    except Exception as e:
        logger.error(f"OpenCV test error: {e}")

if __name__ == "__main__":
    print("🔍 Testing face detection functionality...")
    
    # Тест доступности OpenCV
    test_opencv_availability()
    
    # Тест детекции лиц
    asyncio.run(test_face_detection())
    
    print("✅ Test completed!")
