"""
Конфигурация приложения для генерации Word-документов
"""
import os
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).parent

# Рабочие папки
WORK_DIR = BASE_DIR / "work_data"
CONTRACTS_DIR = WORK_DIR / "договоры"
REPORTS_DIR = WORK_DIR / "отчёты"
LOGS_DIR = WORK_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Внешняя папка с договорами (можно изменить)
# Для продакшена на сервере используем локальную папку
if os.getenv('PRODUCTION') == 'true':
    EXTERNAL_CONTRACTS_DIR = CONTRACTS_DIR
else:
    EXTERNAL_CONTRACTS_DIR = Path(r"D:\договора 2025")

# Файлы
LOG_FILE = LOGS_DIR / "app.log"
HISTORY_FILE = WORK_DIR / "history.json"

def get_logo_file():
    """Получить путь к файлу логотипа"""
    # Ищем логотип - поддерживаем разные форматы
    for ext in ['logo.png', 'logo.jpg', 'logo.jpeg']:
        potential_logo = ASSETS_DIR / ext
        if potential_logo.exists():
            return potential_logo
    return ASSETS_DIR / "logo.png"  # По умолчанию

LOGO_FILE = get_logo_file()

# Настройки UI
WINDOW_TITLE = "Генератор Word-отчётов"
WINDOW_SIZE = "1200x900"

# Список заказчиков (можно расширить)
DEFAULT_CUSTOMERS = [
    "ООО 'Строй-Инвест'",
    "ООО 'Технопром'",
    "ЗАО 'Альфа-Строй'",
    "ИП Иванов И.И.",
]

# Реквизиты исполнителя
COMPANY_NAME = "ИП ГАТАУЛЛИН АЗАМАТ ШАМИЛОВИЧ"
COMPANY_ADDRESS_LINE1 = "Свердловская область, г. Березовский,"
COMPANY_ADDRESS_LINE2 = "ул. Кирова, д. 63, оф. 314"
COMPANY_PHONE = "тел: 8 912 623 35 23; 8 912 60 888 06"
COMPANY_EMAIL = "эл. почта: 2728941@list.ru"
COMPANY_WEBSITE = "сайт: region-ekb.ru"

def ensure_directories():
    """Создает необходимые директории если их нет"""
    for directory in [WORK_DIR, CONTRACTS_DIR, REPORTS_DIR, LOGS_DIR, ASSETS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

