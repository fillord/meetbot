# Meet Bot - Автозапуск и управление

## Статус автозапуска
✅ **Автозапуск настроен и включен!**

Bot будет автоматически запускаться при старте системы и перезапускаться в случае сбоя.

## Управление ботом

### Быстрые команды
```bash
# Используя alias (после перелогина или source ~/.bashrc)
meetbot start    # Запустить бота
meetbot stop     # Остановить бота
meetbot restart  # Перезапустить бота
meetbot status   # Показать статус
meetbot logs     # Показать логи в реальном времени
```

### Полные команды
```bash
# Управление через скрипт
./manage_bot.sh start      # Запустить бота
./manage_bot.sh stop       # Остановить бота
./manage_bot.sh restart    # Перезапустить бота
./manage_bot.sh status     # Показать статус бота
./manage_bot.sh logs       # Показать логи в реальном времени
./manage_bot.sh logs-tail  # Показать последние 50 строк логов
./manage_bot.sh enable     # Включить автозапуск
./manage_bot.sh disable    # Отключить автозапуск
```

### Systemd команды
```bash
# Прямое управление через systemd
sudo systemctl start meet-bot.service     # Запустить
sudo systemctl stop meet-bot.service      # Остановить
sudo systemctl restart meet-bot.service   # Перезапустить
sudo systemctl status meet-bot.service    # Статус
sudo systemctl enable meet-bot.service    # Включить автозапуск
sudo systemctl disable meet-bot.service   # Отключить автозапуск

# Просмотр логов
sudo journalctl -u meet-bot.service -f    # Логи в реальном времени
sudo journalctl -u meet-bot.service -n 50 # Последние 50 строк
```

## Расположение файлов

- **Service файл**: `/etc/systemd/system/meet-bot.service`
- **Скрипт управления**: `/home/yola/tg_bots/meet_bot/manage_bot.sh`
- **Рабочая директория**: `/home/yola/tg_bots/meet_bot`
- **Логи**: `journalctl -u meet-bot.service`

## Настройки service

- **Пользователь**: yola
- **Автоперезапуск**: Включен (через 5 секунд после сбоя)
- **Логирование**: Через systemd journal
- **Безопасность**: NoNewPrivileges, PrivateTmp, ProtectSystem

## Проверка работы автозапуска

После перезагрузки сервера бот должен автоматически запуститься.
Для проверки выполните:

```bash
sudo reboot
# После перезагрузки:
./manage_bot.sh status
```

## Устранение неисправностей

### Бот не запускается
```bash
# Проверить статус
./manage_bot.sh status

# Посмотреть логи ошибок
./manage_bot.sh logs-tail

# Перезапустить
./manage_bot.sh restart
```

### Проблемы с правами
```bash
# Проверить владельца файлов
ls -la /home/yola/tg_bots/meet_bot/

# При необходимости исправить права
sudo chown -R yola:yola /home/yola/tg_bots/meet_bot/
```

### Обновление кода
```bash
# Остановить бота
./manage_bot.sh stop

# Обновить код (git pull или другие изменения)
# ...

# Запустить бота
./manage_bot.sh start
```
