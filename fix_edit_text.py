#!/usr/bin/env python3
"""
Скрипт для замены небезопасных edit_text на safe_edit_message
"""
import re
import os

def fix_edit_text_in_file(file_path):
    """Исправляет edit_text в указанном файле"""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Подсчёт замен
    original_content = content
    
    # 1. Заменяем простые случаи edit_text
    pattern1 = r'await callback\.message\.edit_text\(\s*([^,\n]+),\s*parse_mode="HTML",\s*reply_markup=([^)]+)\s*\)'
    replacement1 = r'await safe_edit_message(\n        callback.message,\n        text=\1,\n        reply_markup=\2\n    )'
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE | re.DOTALL)
    
    # 2. Заменяем edit_text без parse_mode
    pattern2 = r'await callback\.message\.edit_text\(\s*([^,\n]+),\s*reply_markup=([^)]+)\s*\)'
    replacement2 = r'await safe_edit_message(\n        callback.message,\n        text=\1,\n        reply_markup=\2\n    )'
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE | re.DOTALL)
    
    # 3. Заменяем многострочные edit_text
    pattern3 = r'await callback\.message\.edit_text\(\s*"([^"]*(?:\n[^"]*)*)",\s*parse_mode="HTML",\s*reply_markup=([^)]+)\s*\)'
    replacement3 = r'await safe_edit_message(\n        callback.message,\n        text="\1",\n        reply_markup=\2\n    )'
    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE | re.DOTALL)
    
    # Проверяем, были ли изменения
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Файл {file_path} обновлён")
        return True
    else:
        print(f"ℹ️ В файле {file_path} нет изменений")
        return False

if __name__ == "__main__":
    files_to_fix = [
        "/home/yola/tg_bots/meet_bot/handlers/additional_handlers.py"
    ]
    
    for file_path in files_to_fix:
        fix_edit_text_in_file(file_path)
