"""
Модуль управления историей введенных параметров
"""
import json
from datetime import datetime
from pathlib import Path
from logger import app_logger
import config


class HistoryManager:
    """Класс для управления историей"""
    
    def __init__(self):
        config.ensure_directories()
        self.history_file = config.HISTORY_FILE
        self.history = self._load_history()
    
    def _load_history(self):
        """Загружает историю из файла"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            app_logger.error(f"Ошибка при загрузке истории: {e}")
            return []
    
    def _save_history(self):
        """Сохраняет историю в файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            app_logger.error(f"Ошибка при сохранении истории: {e}")
    
    def add_entry(self, data):
        """
        Добавляет запись в историю
        
        Args:
            data (dict): Данные для сохранения
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.history.append(entry)
        
        # Ограничение размера истории (последние 100 записей)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self._save_history()
        app_logger.info("Запись добавлена в историю")
    
    def get_history(self, limit=10):
        """
        Возвращает последние записи истории
        
        Args:
            limit (int): Количество записей
        
        Returns:
            list: Список записей
        """
        return self.history[-limit:]
    
    def get_recent_customers(self, limit=5):
        """Возвращает список последних использованных заказчиков"""
        customers = []
        for entry in reversed(self.history):
            customer = entry.get('data', {}).get('customer')
            if customer and customer not in customers:
                customers.append(customer)
            if len(customers) >= limit:
                break
        return customers
    
    def clear_history(self):
        """Очищает всю историю"""
        self.history = []
        self._save_history()
        app_logger.info("История очищена")

