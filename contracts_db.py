"""
Модуль для управления базой данных договоров
"""
import json
from pathlib import Path
from datetime import datetime
from logger import app_logger
import config


class ContractsDatabase:
    """Класс для управления базой договоров"""
    
    def __init__(self):
        config.ensure_directories()
        self.db_file = config.WORK_DIR / "contracts_db.json"
        self.data = self._load_db()
    
    def _load_db(self):
        """Загружает базу из файла"""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"contracts": [], "last_updated": None}
        except Exception as e:
            app_logger.error(f"Ошибка при загрузке базы договоров: {e}")
            return {"contracts": [], "last_updated": None}
    
    def _save_db(self):
        """Сохраняет базу в файл"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            app_logger.info("База договоров сохранена")
        except Exception as e:
            app_logger.error(f"Ошибка при сохранении базы договоров: {e}")
    
    def update_contracts(self, contracts_list):
        """
        Обновляет базу договоров
        
        Args:
            contracts_list (list): Список данных договоров
        """
        self.data["contracts"] = contracts_list
        self.data["last_updated"] = datetime.now().isoformat()
        self._save_db()
        app_logger.info(f"База обновлена, договоров: {len(contracts_list)}")
    
    def get_all_customers(self):
        """Возвращает список всех уникальных заказчиков"""
        customers = []
        for contract in self.data.get("contracts", []):
            customer = contract.get("customer")
            if customer and customer not in customers:
                customers.append(customer)
        return sorted(customers)
    
    def find_by_customer(self, customer_name):
        """
        Ищет договоры по названию заказчика
        
        Args:
            customer_name (str): Название заказчика
        
        Returns:
            list: Список договоров этого заказчика
        """
        results = []
        for contract in self.data.get("contracts", []):
            if contract.get("customer", "").lower() == customer_name.lower():
                results.append(contract)
        return results
    
    def find_similar_customer(self, partial_name):
        """
        Ищет заказчиков по частичному совпадению
        
        Args:
            partial_name (str): Часть названия
        
        Returns:
            list: Список похожих заказчиков
        """
        results = []
        partial_lower = partial_name.lower()
        for contract in self.data.get("contracts", []):
            customer = contract.get("customer", "")
            if partial_lower in customer.lower() and customer not in results:
                results.append(customer)
        return results
    
    def get_latest_contract_for_customer(self, customer_name):
        """
        Возвращает последний договор для заказчика
        
        Args:
            customer_name (str): Название заказчика
        
        Returns:
            dict or None: Данные договора
        """
        contracts = self.find_by_customer(customer_name)
        if contracts:
            # Возвращаем последний (предполагаем что они уже отсортированы)
            return contracts[-1]
        return None
    
    def get_stats(self):
        """Возвращает статистику по базе"""
        return {
            "total_contracts": len(self.data.get("contracts", [])),
            "unique_customers": len(self.get_all_customers()),
            "last_updated": self.data.get("last_updated")
        }

