"""
Главный файл запуска приложения
Генератор Word-отчётов
"""
import sys
import traceback
from gui import run_application
from logger import app_logger


def main():
    """Точка входа в приложение"""
    try:
        app_logger.info("="*50)
        app_logger.info("Запуск приложения Генератор Word-отчётов")
        app_logger.info("="*50)
        
        run_application()
        
        app_logger.info("Приложение завершено")
        
    except Exception as e:
        error_msg = f"Критическая ошибка:\n{str(e)}\n{traceback.format_exc()}"
        app_logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

