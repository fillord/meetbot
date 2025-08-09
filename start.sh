#!/bin/bash

# Скрипт для быстрого запуска бота

echo "🚀 Запуск Meet Bot..."

# Проверяем наличие виртуального окружения
if [ ! -d ".venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Выполните: python -m venv .venv"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте .env.example в .env и заполните токены"
    exit 1
fi

# Проверяем наличие базы данных
if [ ! -f "meet_bot.db" ]; then
    echo "🗄️ Инициализируем базу данных..."
    .venv/bin/python init_db.py
fi

# Активируем виртуальное окружение и запускаем бота
source .venv/bin/activate
echo "✅ Виртуальное окружение активировано"

echo "🎯 Запускаем бота..."
python bot.py
