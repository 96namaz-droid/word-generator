"""
Запуск улучшенной версии с вкладками
"""
import sys
import traceback
from gui_improved import run_improved_application
from logger import app_logger


def main():
    """Точка входа в улучшенное приложение"""
    try:
        app_logger.info("="*50)
        app_logger.info("Запуск улучшенной версии генератора")
        app_logger.info("="*50)
        
        print("="*60)
        print("📄 ГЕНЕРАТОР ОТЧЁТОВ (Улучшенная версия)")
        print("="*60)
        print()
        print("✨ Новые возможности:")
        print("  • Интерфейс с вкладками")
        print("  • Меню и горячие клавиши")
        print("  • Компактная компоновка")
        print("  • Быстрый запуск веб-версии")
        print()
        print("="*60)
        print()
        
        run_improved_application()
        
        app_logger.info("Приложение завершено")
        
    except Exception as e:
        error_msg = f"Критическая ошибка:\n{str(e)}\n{traceback.format_exc()}"
        app_logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

