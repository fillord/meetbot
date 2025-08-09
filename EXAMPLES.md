# Примеры использования Meet Bot

## 🎯 Быстрый старт

1. **Первый запуск:**
```bash
# Установка зависимостей
pip install -r requirements.txt

# Инициализация БД
python init_db.py

# Запуск бота
python bot.py
```

2. **Получение токена бота:**
- Откройте @BotFather в Telegram
- Отправьте `/newbot`
- Выберите имя бота (например, "My Dating Bot")
- Выберите username (например, `my_dating_bot`)
- Скопируйте токен в `.env` файл

3. **Настройка OpenAI (опционально):**
- Зарегистрируйтесь на platform.openai.com
- Создайте API ключ
- Добавьте в `.env`: `OPENAI_API_KEY=ваш_ключ`

## 📱 Использование бота

### Создание анкеты:
1. Напишите боту `/start`
2. Выберите свой пол
3. Укажите, кого ищете
4. Введите имя, возраст, город
5. Напишите описание о себе
6. Загрузите фотографию

### Поиск людей:
1. Нажмите "👀 Смотреть анкеты"
2. Просматривайте анкеты
3. Ставьте ❤️ или 👎
4. При взаимной симпатии появится матч!

### Улучшение анкеты:
1. Откройте "📝 Моя анкета"
2. Нажмите "🤖 Улучшить с AI"
3. Бот автоматически улучшит описание

## 🔧 Администрирование

### Статистика:
```bash
python admin_utils.py stats
```

### Поиск пользователей:
```bash
# По username
python admin_utils.py find @username

# По имени
python admin_utils.py find "Анна"

# По ID
python admin_utils.py find 123456789
```

### Очистка данных:
```bash
# Удалить данные старше 30 дней
python admin_utils.py cleanup 30
```

## 🚀 Продакшен

### Systemd service:
```bash
# Создайте файл /etc/systemd/system/meet-bot.service
sudo nano /etc/systemd/system/meet-bot.service

# Добавьте содержимое из README
# Затем:
sudo systemctl enable meet-bot
sudo systemctl start meet-bot
```

### Мониторинг логов:
```bash
# В реальном времени
tail -f bot.log

# Последние ошибки
grep ERROR bot.log
```

### Бэкап базы данных:
```bash
# Создание бэкапа
cp meet_bot.db backup_$(date +%Y%m%d_%H%M%S).db

# Автоматический бэкап (добавьте в crontab)
0 2 * * * cp /path/to/meet_bot.db /backups/meet_bot_$(date +\%Y\%m\%d).db
```

## 💡 Полезные команды

### Разработка:
```bash
# Запуск с автоперезагрузкой при изменениях
python -m watchdog.observers.polling bot.py

# Проверка синтаксиса
python -m py_compile bot.py

# Форматирование кода
black *.py
```

### Тестирование:
```bash
# Проверка подключения к Telegram API
python -c "from aiogram import Bot; import asyncio; bot=Bot('YOUR_TOKEN'); print(asyncio.run(bot.get_me()))"

# Тест базы данных
python -c "from database import Database; import asyncio; db=Database('test.db'); asyncio.run(db.init_db()); print('OK')"
```

## 🔒 Безопасность

### Рекомендации:
1. Никогда не коммитьте `.env` файл
2. Используйте сильные пароли для админов
3. Регулярно обновляйте зависимости
4. Настройте фаервол на сервере
5. Используйте HTTPS для веб-хуков (если есть)

### Мониторинг подозрительной активности:
```bash
# Пользователи с большим количеством свайпов
echo "SELECT user_id, COUNT(*) as swipes FROM swipes GROUP BY user_id ORDER BY swipes DESC LIMIT 10;" | sqlite3 meet_bot.db

# Недавние регистрации
echo "SELECT user_id, username, created_at FROM users WHERE created_at > datetime('now', '-1 day');" | sqlite3 meet_bot.db
```

## 🎨 Кастомизация

### Изменение текстов:
- Отредактируйте файлы в папке `handlers/`
- Все тексты используют эмодзи для лучшего UX
- Поддерживается HTML разметка

### Добавление новых функций:
1. Создайте новый handler в `handlers/`
2. Добавьте в `handlers/__init__.py`
3. Зарегистрируйте роутер в главном файле

### Изменение лимитов:
- Отредактируйте `config.py`
- Или используйте переменные окружения в `.env`
