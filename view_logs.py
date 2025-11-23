"""
Скрипт для просмотра логов в реальном времени
"""
import os
import time
from pathlib import Path
import config

def tail_log(file_path, num_lines=50):
    """Показывает последние N строк лога"""
    if not file_path.exists():
        print(f"Лог файл не найден: {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return lines[-num_lines:]

def follow_log(file_path):
    """Следит за логом в реальном времени (как tail -f)"""
    if not file_path.exists():
        print(f"Лог файл не найден: {file_path}")
        return
    
    print(f"Отслеживание лога: {file_path}")
    print("=" * 80)
    print("Нажмите Ctrl+C для выхода")
    print("=" * 80)
    print()
    
    # Показываем последние 20 строк
    lines = tail_log(file_path, 20)
    for line in lines:
        print(line.rstrip())
    
    # Отслеживаем новые строки
    with open(file_path, 'r', encoding='utf-8') as f:
        # Переходим в конец файла
        f.seek(0, 2)
        
        try:
            while True:
                line = f.readline()
                if line:
                    print(line.rstrip())
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nОстановка отслеживания...")

if __name__ == "__main__":
    config.ensure_directories()
    log_file = config.LOG_FILE
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "-f":
        # Режим отслеживания в реальном времени
        follow_log(log_file)
    else:
        # Показываем последние строки
        print(f"Последние 50 строк лога:\n")
        print("=" * 80)
        lines = tail_log(log_file, 50)
        for line in lines:
            print(line.rstrip())
        print("\n" + "=" * 80)
        print("\nДля отслеживания в реальном времени используйте:")
        print("  python view_logs.py -f")
