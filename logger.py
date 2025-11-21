"""
Модуль логирования операций
"""
import logging
from datetime import datetime
from config import LOG_FILE, ensure_directories

class AppLogger:
    """Логгер приложения"""
    
    def __init__(self):
        ensure_directories()
        
        # Настройка логгера
        self.logger = logging.getLogger("WordGenerator")
        self.logger.setLevel(logging.INFO)
        
        # Форматирование
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Файловый handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Консольный handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Информационное сообщение"""
        self.logger.info(message)
    
    def warning(self, message):
        """Предупреждение"""
        self.logger.warning(message)
    
    def error(self, message):
        """Ошибка"""
        self.logger.error(message)
    
    def debug(self, message):
        """Отладочное сообщение"""
        self.logger.debug(message)

# Глобальный экземпляр логгера
app_logger = AppLogger()

