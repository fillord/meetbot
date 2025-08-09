#!/usr/bin/env python3
"""
Скрипт для запуска бота в продакшене с restart на ошибках
"""

import asyncio
import logging
import sys
import subprocess
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def run_bot():
    """Запуск бота с обработкой ошибок"""
    max_restarts = 5
    restart_count = 0
    
    while restart_count < max_restarts:
        try:
            logger.info(f"Запуск бота (попытка {restart_count + 1})")
            
            # Запускаем основной скрипт бота
            from bot import main
            await main()
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
            break
            
        except Exception as e:
            restart_count += 1
            logger.error(f"Ошибка в боте: {e}")
            
            if restart_count < max_restarts:
                logger.info(f"Перезапуск через 5 секунд... ({restart_count}/{max_restarts})")
                await asyncio.sleep(5)
            else:
                logger.error("Превышено максимальное количество перезапусков")
                break

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Остановлено пользователем")
