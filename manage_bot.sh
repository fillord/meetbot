#!/bin/bash

# Скрипт управления Meet Bot

case "$1" in
    start)
        echo "Запуск Meet Bot..."
        sudo systemctl start meet-bot.service
        echo "Бот запущен!"
        ;;
    stop)
        echo "Остановка Meet Bot..."
        sudo systemctl stop meet-bot.service
        echo "Бот остановлен!"
        ;;
    restart)
        echo "Перезапуск Meet Bot..."
        sudo systemctl restart meet-bot.service
        echo "Бот перезапущен!"
        ;;
    status)
        echo "Статус Meet Bot:"
        sudo systemctl status meet-bot.service
        ;;
    logs)
        echo "Логи Meet Bot (нажмите Ctrl+C для выхода):"
        sudo journalctl -u meet-bot.service -f
        ;;
    logs-tail)
        echo "Последние 50 строк логов:"
        sudo journalctl -u meet-bot.service -n 50 --no-pager
        ;;
    enable)
        echo "Включение автозапуска Meet Bot..."
        sudo systemctl enable meet-bot.service
        echo "Автозапуск включен!"
        ;;
    disable)
        echo "Отключение автозапуска Meet Bot..."
        sudo systemctl disable meet-bot.service
        echo "Автозапуск отключен!"
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs|logs-tail|enable|disable}"
        echo ""
        echo "Команды:"
        echo "  start      - Запустить бота"
        echo "  stop       - Остановить бота"
        echo "  restart    - Перезапустить бота"
        echo "  status     - Показать статус бота"
        echo "  logs       - Показать логи в реальном времени"
        echo "  logs-tail  - Показать последние 50 строк логов"
        echo "  enable     - Включить автозапуск"
        echo "  disable    - Отключить автозапуск"
        exit 1
        ;;
esac

exit 0
