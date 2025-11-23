"""
Модуль валидации вводимых данных
"""
import re
from datetime import datetime


class DataValidator:
    """Класс для валидации данных"""
    
    @staticmethod
    def validate_date(date_str):
        """
        Валидация даты
        
        Args:
            date_str (str): Строка с датой
        
        Returns:
            tuple: (bool, str) - (валидность, сообщение об ошибке)
        """
        if not date_str:
            return False, "Дата не может быть пустой"
        
        # Проверка формата даты
        date_formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True, ""
            except ValueError:
                continue
        
        return False, "Неверный формат даты. Используйте ДД.ММ.ГГГГ"
    
    @staticmethod
    def validate_customer(customer):
        """
        Валидация заказчика
        
        Args:
            customer (str): Имя заказчика
        
        Returns:
            tuple: (bool, str)
        """
        if not customer or not customer.strip():
            return False, "Заказчик не может быть пустым"
        
        if len(customer) < 3:
            return False, "Имя заказчика слишком короткое"
        
        return True, ""
    
    @staticmethod
    def validate_text_field(text, field_name, min_length=1):
        """
        Валидация текстового поля
        
        Args:
            text (str): Текст для проверки
            field_name (str): Название поля
            min_length (int): Минимальная длина
        
        Returns:
            tuple: (bool, str)
        """
        if not text or not text.strip():
            return False, f"{field_name} не может быть пустым"
        
        if len(text.strip()) < min_length:
            return False, f"{field_name} слишком короткое"
        
        return True, ""
    
    @staticmethod
    def validate_number(value, field_name, min_value=0, max_value=None):
        """
        Валидация числового значения
        
        Args:
            value: Значение для проверки
            field_name (str): Название поля
            min_value (float): Минимальное значение
            max_value (float): Максимальное значение
        
        Returns:
            tuple: (bool, str)
        """
        try:
            num = float(value)
            
            if num < min_value:
                return False, f"{field_name} не может быть меньше {min_value}"
            
            if max_value is not None and num > max_value:
                return False, f"{field_name} не может быть больше {max_value}"
            
            return True, ""
            
        except (ValueError, TypeError):
            return False, f"{field_name} должно быть числом"
    
    @staticmethod
    def validate_table_data(table_data):
        """
        Валидация данных таблицы
        
        Args:
            table_data (list): Данные таблицы
        
        Returns:
            tuple: (bool, str)
        """
        if not table_data or len(table_data) == 0:
            return False, "Таблица не может быть пустой"
        
        if len(table_data) < 2:
            return False, "Таблица должна содержать хотя бы заголовок и одну строку данных"
        
        # Проверка одинаковой длины строк
        first_row_len = len(table_data[0])
        for i, row in enumerate(table_data[1:], start=1):
            if len(row) != first_row_len:
                return False, f"Строка {i} имеет неправильное количество колонок"
        
        return True, ""
    
    @staticmethod
    def validate_all_data(data):
        """
        Комплексная валидация всех данных
        
        Args:
            data (dict): Словарь с данными
        
        Returns:
            tuple: (bool, list) - (валидность, список ошибок)
        """
        from logger import app_logger
        errors = []
        
        app_logger.info(f"[VALIDATOR] Начало валидации, тип протокола: {data.get('protocol_type', 'не указан')}")
        
        # Валидация даты
        date_val = data.get('date', '')
        app_logger.info(f"[VALIDATOR] Проверка даты: '{date_val}'")
        valid, msg = DataValidator.validate_date(date_val)
        if not valid:
            errors.append(msg)
            app_logger.warning(f"[VALIDATOR] Ошибка даты: {msg}")
        
        # Валидация заказчика
        customer_val = data.get('customer', '')
        app_logger.info(f"[VALIDATOR] Проверка заказчика: '{customer_val}'")
        valid, msg = DataValidator.validate_customer(customer_val)
        if not valid:
            errors.append(msg)
            app_logger.warning(f"[VALIDATOR] Ошибка заказчика: {msg}")
        
        # Валидация адреса/наименования объекта (объединённое поле)
        address_val = data.get('object_full_address', '')
        app_logger.info(f"[VALIDATOR] Проверка адреса: длина={len(address_val)}")
        valid, msg = DataValidator.validate_text_field(
            address_val,
            'Адрес/наименование испытываемого объекта',
            min_length=5
        )
        if not valid:
            errors.append(msg)
            app_logger.warning(f"[VALIDATOR] Ошибка адреса: {msg}")
        
        protocol_type = data.get('protocol_type', 'vertical')
        app_logger.info(f"[VALIDATOR] Валидация протокола типа: {protocol_type}")

        if protocol_type == 'vertical':
            app_logger.info(f"[VALIDATOR] Валидация вертикальных лестниц...")
            protocol_errors = DataValidator._validate_vertical_protocol(data)
            errors.extend(protocol_errors)
            app_logger.info(f"[VALIDATOR] Ошибок в протоколе: {len(protocol_errors)}")
        elif protocol_type == 'stair':
            app_logger.info(f"[VALIDATOR] Валидация маршевых лестниц...")
            protocol_errors = DataValidator._validate_stair_protocol(data)
            errors.extend(protocol_errors)
            app_logger.info(f"[VALIDATOR] Ошибок в протоколе: {len(protocol_errors)}")
        elif protocol_type == 'roof':
            app_logger.info(f"[VALIDATOR] Валидация ограждений кровли...")
            protocol_errors = DataValidator._validate_roof_protocol(data)
            errors.extend(protocol_errors)
            app_logger.info(f"[VALIDATOR] Ошибок в протоколе: {len(protocol_errors)}")
        else:
            error_msg = "Неизвестный тип протокола. Выберите корректное значение."
            errors.append(error_msg)
            app_logger.error(f"[VALIDATOR] {error_msg}")
        
        # Валидация температуры
        if data.get('temperature'):
            temp_val = data.get('temperature', '')
            app_logger.info(f"[VALIDATOR] Проверка температуры: '{temp_val}'")
            valid, msg = DataValidator.validate_number(
                temp_val,
                'Температура воздуха',
                min_value=-50,
                max_value=50
            )
            if not valid:
                errors.append(msg)
                app_logger.warning(f"[VALIDATOR] Ошибка температуры: {msg}")
        
        # Валидация скорости ветра
        if data.get('wind_speed'):
            wind_val = data.get('wind_speed', '')
            app_logger.info(f"[VALIDATOR] Проверка скорости ветра: '{wind_val}'")
            valid, msg = DataValidator.validate_number(
                wind_val,
                'Скорость ветра',
                min_value=0,
                max_value=100
            )
            if not valid:
                errors.append(msg)
                app_logger.warning(f"[VALIDATOR] Ошибка скорости ветра: {msg}")
        
        result_valid = len(errors) == 0
        app_logger.info(f"[VALIDATOR] Итог валидации: valid={result_valid}, ошибок={len(errors)}")
        if errors:
            app_logger.warning(f"[VALIDATOR] Список ошибок: {errors}")
        
        return result_valid, errors

    # --- Протокольные валидаторы ----------------------------------------------

    @staticmethod
    def _validate_vertical_protocol(data):
        errors = []
        ladders = data.get('ladders', [])
        if not ladders or len(ladders) == 0:
            errors.append('❌ Ошибка заполнения: Добавьте хотя бы одну лестницу')
            return errors

        for i, ladder in enumerate(ladders, 1):
            ladder_errors = []

            required_fields = [
                ('height', 'Высота', 0.1, 1000),
                ('width', 'Ширина', 0.1, 1000),
                ('steps_count', 'Количество ступеней', 1, 1000),
                ('mount_points', 'Количество точек крепления', 1, 1000),
                ('step_distance', 'Расстояние между ступенями', 0.01, 10),
            ]

            for field, title, min_val, max_val in required_fields:
                value = str(ladder.get(field, '')).strip()
                if not value:
                    ladder_errors.append(title)
                else:
                    valid, msg = DataValidator.validate_number(
                        ladder.get(field, ''),
                        f'{title} лестницы №{i}',
                        min_value=min_val,
                        max_value=max_val
                    )
                    if not valid:
                        errors.append(msg)

            optional_numeric_fields = [
                ('platform_length', 'Длина площадки', 0.1, 100),
                ('platform_width', 'Ширина площадки', 0.1, 100),
                ('fence_height', 'Высота ограждения', 0.1, 10),
                ('ground_distance', 'Расстояние от земли', 0, 100),
                ('wall_distance', 'Расстояние от стены', 0, 100),
            ]

            for field, title, min_val, max_val in optional_numeric_fields:
                value = str(ladder.get(field, '')).strip()
                if value:
                    valid, msg = DataValidator.validate_number(
                        ladder.get(field, ''),
                        f'{title} лестницы №{i}',
                        min_value=min_val,
                        max_value=max_val
                    )
                    if not valid:
                        errors.append(msg)

            if ladder_errors:
                error_fields = ', '.join(ladder_errors)
                error_msg = f'❌ Ошибка заполнения лестницы №{i}: Не заполнены обязательные поля: {error_fields}'
                errors.append(error_msg)

        return errors

    @staticmethod
    def _validate_stair_protocol(data):
        errors = []
        marches = data.get('marches', [])
        
        if not marches or len(marches) == 0:
            errors.append('❌ Ошибка заполнения: Добавьте хотя бы один марш и площадку')
            return errors
        
        for i, march in enumerate(marches, 1):
            march_errors = []
            has_march = march.get('has_march', True)
            has_platform = march.get('has_platform', True)
            
            # Валидация полей марша
            if has_march:
                march_fields = [
                    ('march_width', 'Ширина марша', 0.5, 10.0),
                    ('march_length', 'Длина марша', 0.5, 50.0),
                    ('step_width', 'Ширина ступени', 0.15, 1.0),
                    ('step_distance', 'Расстояние между ступенями', 0.15, 0.5),
                    ('steps_count', 'Количество ступеней', 1, 100),
                    ('march_fence_height', 'Высота ограждений марша', 0.5, 2.5),
                ]
                
                for field, title, min_val, max_val in march_fields:
                    value = str(march.get(field, '')).strip()
                    if not value:
                        march_errors.append(title)
                    else:
                        valid, msg = DataValidator.validate_number(
                            march.get(field, ''),
                            f'{title} (элемент №{i})',
                            min_value=min_val,
                            max_value=max_val
                        )
                        if not valid:
                            errors.append(msg)
            
            # Валидация полей площадки
            if has_platform:
                platform_fields = [
                    ('platform_length', 'Длина площадки', 0.5, 10.0),
                    ('platform_width', 'Ширина площадки', 0.5, 10.0),
                    ('platform_fence_height', 'Высота ограждений площадки', 0.5, 2.5),
                ]
                
                for field, title, min_val, max_val in platform_fields:
                    value = str(march.get(field, '')).strip()
                    if not value:
                        march_errors.append(title)
                    else:
                        valid, msg = DataValidator.validate_number(
                            march.get(field, ''),
                            f'{title} (элемент №{i})',
                            min_value=min_val,
                            max_value=max_val
                        )
                        if not valid:
                            errors.append(msg)
            
            # Опциональные поля площадки
            if has_platform:
                optional_fields = [
                    ('platform_ground_distance', 'Расстояние от площадки до земли', 0, 100),
                ]
                for field, title, min_val, max_val in optional_fields:
                    value = str(march.get(field, '')).strip()
                    if value:  # Проверяем только если заполнено
                        valid, msg = DataValidator.validate_number(
                            march.get(field, ''),
                            f'{title} (элемент №{i})',
                            min_value=min_val,
                            max_value=max_val
                        )
                        if not valid:
                            errors.append(msg)
            
            if march_errors:
                error_fields = ', '.join(march_errors)
                error_msg = f'❌ Ошибка заполнения элемента №{i}: Не заполнены обязательные поля: {error_fields}'
                errors.append(error_msg)

        # Валидация количества точек крепления (обязательное поле)
        mount_points = data.get('mount_points', '').strip()
        if not mount_points:
            errors.append('Количество точек крепления не может быть пустым')
        else:
            valid, msg = DataValidator.validate_number(
                mount_points,
                'Количество точек крепления',
                min_value=1,
                max_value=1000
            )
            if not valid:
                errors.append(msg)

        # Поле названия лестницы необязательное (если пусто, будет использован дефолт)
        # surface_condition тоже необязательное
        return errors

    @staticmethod
    def _validate_roof_protocol(data):
        errors = []
        numeric_fields = [
            ('length', 'Длина участка', 1, 1000),
            ('height', 'Высота ограждения', 0.6, 3.0),
            ('mount_points', 'Количество точек крепления', 2, 1000),
        ]
        for field, title, min_val, max_val in numeric_fields:
            value = str(data.get(field, '')).strip()
            if not value:
                errors.append(f"{title} не может быть пустым")
            else:
                valid, msg = DataValidator.validate_number(
                    data.get(field, ''),
                    title,
                    min_value=min_val,
                    max_value=max_val
                )
                if not valid:
                    errors.append(msg)

        # Валидация высоты от парапета (если заполнена)
        parapet_height_str = str(data.get('parapet_height', '')).strip()
        if parapet_height_str:
            valid, msg = DataValidator.validate_number(
                parapet_height_str,
                'Высота ограждения от парапета',
                min_value=0.1,
                max_value=10.0
            )
            if not valid:
                errors.append(msg)
            else:
                # Проверка, что высота от парапета >= высоте ограждения
                try:
                    parapet_height = float(parapet_height_str.replace(',', '.'))
                    height_str = str(data.get('height', '')).strip()
                    if height_str:
                        height = float(height_str.replace(',', '.'))
                        if parapet_height < height:
                            errors.append(
                                f"Высота ограждения от парапета ({parapet_height} м) не может быть меньше "
                                f"высоты ограждения ({height} м)"
                            )
                except (ValueError, TypeError):
                    pass  # Уже обработано выше

        return errors

