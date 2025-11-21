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
        protocol = (protocol_type or data.get("protocol_type") or "vertical").lower()
        app_logger.info(f"Запрошена генерация протокола типа: {protocol}")
        generator = GeneratorFactory.create(protocol, data)
        generator.validate()
        filepath = generator.generate_doc(output_path)
        app_logger.info(f"Документ создан: {filepath}")
        return filepath


