"""
Генератор протокола испытания ограждений кровли
"""
from __future__ import annotations

from generators.base_generator import BaseProtocolGenerator


class RoofFenceGenerator(BaseProtocolGenerator):
    """Генерация документа для ограждений кровли"""

    REQUIRED_FIELDS = (
        'date',
        'customer',
        'object_full_address',
        'length',
        'height',
        'mount_points',
    )

    def validate(self) -> None:
        self._require_fields(self.REQUIRED_FIELDS)
        numeric_fields = (
            ('length', 1.0, 500.0),
            ('height', 0.6, 2.5),
            ('mount_points', 2, 500),
        )
        for field, min_value, max_value in numeric_fields:
            value = self._to_float(self.data.get(field))
            if value < min_value or value > max_value:
                raise ValueError(
                    f"Поле '{field}' должно быть в диапазоне {min_value}–{max_value}"
                )

    def generate_doc(self, output_path=None) -> str:
        self._set_document()
        self._add_company_header()
        self._add_title(
            "Протокол испытания ограждений кровли",
            f"от {self.data.get('date', '')}".strip()
        )
        self._add_overview()
        self._add_geometry_section()
        self._add_mounting_section()
        self._add_load_table()
        self._add_conclusion()
        self._add_signatures()

        filename = self._generate_filename("Протокол_ограждения")
        output = self._resolve_output_path(output_path, filename)
        self.document.save(str(output))
        return str(output)

    # --- Разделы документа -----------------------------------------------------

    def _add_overview(self) -> None:
        self._add_key_value('Заказчик', self.data.get('customer', ''))
        self._add_key_value(
            'Адрес/наименование объекта',
            self.data.get('object_full_address', '')
        )
        self.document.add_paragraph()

    def _add_geometry_section(self) -> None:
        heading = self.document.add_heading('Характеристики ограждения', level=1)
        self._format_paragraph(heading)

        parapet_height = self.data.get('parapet_height', '')
        rows = [
            ('Длина участка', f"{self.data.get('length')} м"),
            ('Высота ограждения', f"{self.data.get('height')} м"),
            ('Количество опор', f"{self.data.get('mount_points')} шт."),
        ]
        if parapet_height:
            rows.append(('Высота ограждения от парапета', f"{parapet_height} м"))
        self._add_table(('Параметр', 'Значение'), rows)

        note = (
            "Элементы ограждения выполнены секциями длиной 2–3 м, "
            "соединения секций выполнены накладками с болтовым креплением. "
            "Сварные швы очищены и защищены антикоррозионным покрытием."
        )
        paragraph = self.document.add_paragraph(note)
        self._format_paragraph(paragraph)
        self.document.add_paragraph()

    def _add_mounting_section(self) -> None:
        heading = self.document.add_heading('Схема крепления и условия испытаний', level=1)
        self._format_paragraph(heading)

        mount_pitch = self.data.get('mount_pitch', 'не более 1.2 м')
        text = (
            f"Крепление ограждений выполняется к закладным деталям парапета с шагом {mount_pitch}. "
            f"Контрольные нагрузки приложены на высоте 0.6 м и 1.1 м от уровня кровли согласно ГОСТ Р 53254-2009."
        )
        paragraph = self.document.add_paragraph(text)
        self._format_paragraph(paragraph)
        self.document.add_paragraph()

    def _add_load_table(self) -> None:
        heading = self.document.add_heading('Результаты нагрузочных испытаний', level=1)
        self._format_paragraph(heading)

        length = self._to_float(self.data.get('length'))
        height = self._to_float(self.data.get('height'))
        mounts = max(2, int(self._to_float(self.data.get('mount_points'))))

        span_points = max(2, int(length / 1.5) + 1)
        top_load = round(0.54 + height * 0.1, 2)
        mid_load = round(0.3 + height * 0.05, 2)
        anchor_load = round((length * 0.4) / mounts, 2)

        rows = [
            ("1", "Продольные стойки", mounts, "Проверка жесткости узлов", "Без остаточных деформаций"),
            ("2", "Верхняя горизонталь", span_points, f"{top_load:.2f} кН ({top_load * 100:.0f} кгс)", "Выдержала"),
            ("3", "Средняя горизонталь", span_points, f"{mid_load:.2f} кН ({mid_load * 100:.0f} кгс)", "Выдержала"),
            ("4", "Анкерные крепления", mounts, f"{anchor_load:.2f} кН ({anchor_load * 100:.0f} кгс)", "Выдержали"),
        ]
        self._add_table(
            ("№ п/п", "Испытываемый элемент", "Кол-во точек", "Нагрузка", "Результат"),
            rows
        )

    def _add_conclusion(self) -> None:
        heading = self.document.add_heading('Выводы', level=1)
        self._format_paragraph(heading)

        text = (
            "Ограждения кровли выдержали контрольные нагрузки в течение 2 минут "
            "в каждой точке приложения силы. Остаточные деформации и разрушения узлов "
            "не обнаружены. Конструкции соответствуют требованиям ГОСТ Р 53254-2009 и "
            "допускаются к дальнейшей эксплуатации."
        )
        paragraph = self.document.add_paragraph(text)
        self._format_paragraph(paragraph)
        self.document.add_paragraph()

    # --- Helpers ---------------------------------------------------------------

    @staticmethod
    def _to_float(value, default=0.0) -> float:
        try:
            return float(str(value).replace(',', '.'))
        except (TypeError, ValueError, AttributeError):
            return default


