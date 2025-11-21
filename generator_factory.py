"""
Фабрика генераторов протоколов
"""
from generators.vertical_ladder import VerticalLadderGenerator
from generators.stair_ladder import StairLadderGenerator
from generators.roof_fence import RoofFenceGenerator


class GeneratorFactory:
    """Создает генератор по типу протокола"""

    @staticmethod
    def create(protocol_type: str, data: dict):
        protocol_type = (protocol_type or '').lower()
        if protocol_type == "vertical":
            return VerticalLadderGenerator(data)
        if protocol_type == "stair":
            return StairLadderGenerator(data)
        if protocol_type == "roof":
            return RoofFenceGenerator(data)
        raise ValueError(f"Unknown protocol type: {protocol_type}")


