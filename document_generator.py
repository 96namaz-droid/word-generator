"""
Фасад для совместимости со старым API.
"""
from __future__ import annotations

from logger import app_logger
from generator_factory import GeneratorFactory


class DocumentGenerator:
    """Старый интерфейс, делегирующий новую архитектуру."""

    def create_document(
        self,
        data: dict,
        protocol_type: str | None = None,
        output_path: str | None = None,
    ) -> str:
        try:
            protocol = (protocol_type or data.get("protocol_type") or "vertical").lower()
            app_logger.info(f"=== DOCUMENT_GENERATOR.create_document ===")
            app_logger.info(f"Тип протокола: {protocol}")
            app_logger.info(f"Данные получены: keys={list(data.keys())}")
            
            app_logger.info("Создание генератора через Factory...")
            generator = GeneratorFactory.create(protocol, data)
            app_logger.info(f"Генератор создан: {type(generator).__name__}")
            
            app_logger.info("Вызов validate() генератора...")
            generator.validate()
            app_logger.info("Валидация генератора пройдена ✓")
            
            app_logger.info("Вызов generate_doc()...")
            filepath = generator.generate_doc(output_path)
            app_logger.info(f"=== ДОКУМЕНТ УСПЕШНО СОЗДАН ===")
            app_logger.info(f"Путь к файлу: {filepath}")
            
            # Проверяем существование файла
            from pathlib import Path
            file_path_obj = Path(filepath)
            if file_path_obj.exists():
                app_logger.info(f"Файл существует, размер: {file_path_obj.stat().st_size} байт")
            else:
                app_logger.error(f"ОШИБКА: Файл не найден после создания: {filepath}")
            
            return filepath
        except Exception as e:
            import traceback
            error_msg = f"ОШИБКА В create_document: {str(e)}\n{traceback.format_exc()}"
            app_logger.error(error_msg)
            raise


