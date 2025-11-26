"""
Скрипт для автоматической генерации протокола через веб-API
"""
import requests
import json
import time
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Данные для протокола
PROTOCOL_DATA = {
    "protocol_type": "stair",
    "date": datetime.now().strftime("%d.%m.%Y"),
    "customer": "Тестовый заказчик",
    "object_full_address": "Тестовый объект",
    "test_time": "дневное время",
    "temperature": "",
    "wind_speed": "",
    "ladder_name": "",
    "mount_points": "8",
    "marches": [
        {
            "number": 1,
            "has_march": True,
            "has_platform": True,
            "march_width": "0.7",  # ширина лестницы
            "march_length": "4.77",  # высота лестницы (используем как длину марша)
            "step_width": "0.7",  # ширина ступени = ширина лестницы
            "step_distance": "0.30",  # между ступенями
            "steps_count": "12",  # количество ступеней
            "march_fence_height": "1.0",  # высота ограждений марша (стандартное значение)
            "platform_length": "0.6",  # длина площадки
            "platform_width": "0.8",  # ширина площадки
            "platform_fence_height": "1.0",  # высота ограждений площадки
            "platform_ground_distance": "0"  # расстояние от площадки до земли
        }
    ],
    "damage_found": False,
    "mount_violation_found": False,
    "weld_violation_found": False,
    "paint_compliant": True,
    "project_compliant": False,
    "project_number": ""
}

API_URL = "http://localhost:8000"


def wait_for_server(max_attempts=30):
    """Ждет пока сервер запустится"""
    print("Ожидание запуска сервера...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{API_URL}/", timeout=2)
            if response.status_code == 200:
                print("[OK] Сервер запущен")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    return False


def generate_protocol():
    """Генерирует протокол через API"""
    print("\n=== Генерация протокола ===")
    print(f"Тип: {PROTOCOL_DATA['protocol_type']}")
    print(f"Дата: {PROTOCOL_DATA['date']}")
    print(f"Количество точек крепления: {PROTOCOL_DATA['mount_points']}")
    print(f"Маршей: {len(PROTOCOL_DATA['marches'])}")
    
    # Валидация
    print("\nВалидация данных...")
    try:
        validate_response = requests.post(
            f"{API_URL}/api/validate",
            json=PROTOCOL_DATA,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if validate_response.status_code != 200:
            print(f"[ERROR] Ошибка валидации: {validate_response.status_code}")
            print(validate_response.text)
            return None
        
        validate_result = validate_response.json()
        if not validate_result.get("valid", False):
            print(f"[ERROR] Валидация не пройдена:")
            for error in validate_result.get("errors", []):
                print(f"  - {error}")
            return None
        
        print("[OK] Валидация пройдена")
    except Exception as e:
        print(f"⚠ Ошибка валидации (продолжаем): {e}")
    
    # Генерация
    print("\nГенерация документа...")
    try:
        generate_response = requests.post(
            f"{API_URL}/api/generate",
            json=PROTOCOL_DATA,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if generate_response.status_code != 200:
            print(f"[ERROR] Ошибка генерации: {generate_response.status_code}")
            try:
                error_data = generate_response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(generate_response.text)
            return None
        
        # Сохранение файла
        content_disposition = generate_response.headers.get("Content-Disposition", "")
        filename = "report.docx"
        
        # Парсинг имени файла из заголовка
        if "filename*=" in content_disposition:
            match = re.search(r"filename\*=([^']+)''(.+?)(?:;|$)", content_disposition, re.I)
            if match:
                try:
                    filename = requests.utils.unquote(match.group(2))
                except:
                    pass
        elif "filename=" in content_disposition:
            match = re.search(r'filename=([^;]+)', content_disposition, re.I)
            if match:
                filename = match.group(1).strip('"\'')
        
        # Определяем путь для сохранения
        reports_dir = Path(__file__).parent / "work_data" / "отчёты"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = reports_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(generate_response.content)
        
        print(f"[OK] Документ сохранен: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"[ERROR] Ошибка генерации: {e}")
        import traceback
        traceback.print_exc()
        return None


def open_file(filepath):
    """Открывает файл в системе"""
    if not filepath or not filepath.exists():
        return
    
    print(f"\nОткрытие файла: {filepath}")
    try:
        os.startfile(str(filepath))
        print("[OK] Файл открыт")
    except Exception as e:
        print(f"⚠ Не удалось открыть файл автоматически: {e}")
        print(f"   Откройте вручную: {filepath}")


if __name__ == "__main__":
    print("=" * 60)
    print("Автоматическая генерация протокола")
    print("=" * 60)
    
    if not wait_for_server():
        print("[ERROR] Сервер не запустился. Убедитесь, что start_web.py запущен.")
        exit(1)
    
    filepath = generate_protocol()
    
    if filepath:
        open_file(filepath)
        print("\n[OK] Готово!")
    else:
        print("\n[ERROR] Ошибка генерации протокола")
        exit(1)

