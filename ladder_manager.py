"""
Модуль для управления списком лестниц
"""
import tkinter as tk
from tkinter import ttk, messagebox
from logger import app_logger


class LadderWidget(tk.Frame):
    """Виджет для ввода данных одной вертикальной лестницы"""
    
    def __init__(self, parent, ladder_num, on_delete_callback):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=1, padx=5, pady=5)
        
        self.ladder_num = ladder_num
        self.on_delete = on_delete_callback
        self.ladder_type = 'vertical'
        
        # Заголовок с номером и кнопкой удаления
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', pady=(0, 5))
        
        self.header_label = ttk.Label(
            header_frame,
            text=f"Вертикальная лестница №{ladder_num}",
            font=('Arial', 10, 'bold')
        )
        self.header_label.pack(side='left')
        
        if ladder_num > 1:  # Первую лестницу нельзя удалить
            ttk.Button(header_frame, text="✖ Удалить", width=10,
                      command=self._delete_self).pack(side='right')
        
        # Фрейм с полями
        self.fields_frame = ttk.Frame(self)
        self.fields_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.fields_frame, text="Название:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.name_entry = ttk.Entry(self.fields_frame, width=60)
        self.name_entry.grid(row=0, column=1, columnspan=3, sticky='ew', pady=2)
        
        self.entries = {}
        self._create_vertical_fields()

        # Принудительно оставляем только вертикальные лестницы
        self._enforce_vertical_only()
        
        self.fields_frame.columnconfigure(1, weight=1)
        self.fields_frame.columnconfigure(3, weight=1)
        
        # Визуальный осмотр
        self.damage_found_var = tk.BooleanVar(value=False)
        self.mount_violation_var = tk.BooleanVar(value=False)
        self.weld_violation_var = tk.BooleanVar(value=False)
        self.paint_compliant_var = tk.BooleanVar(value=True)
        
        inspection_frame = ttk.LabelFrame(self, text="Визуальный осмотр", padding=5)
        inspection_frame.pack(fill='x', pady=5)
        
        ttk.Checkbutton(inspection_frame, text="Внешние повреждения", 
                       variable=self.damage_found_var).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(inspection_frame, text="Нарушение крепления к стене", 
                       variable=self.mount_violation_var).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(inspection_frame, text="Нарушение сварных швов", 
                       variable=self.weld_violation_var).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(inspection_frame, text="Защитное покрытие соответствует ГОСТ 9.302", 
                       variable=self.paint_compliant_var).grid(row=1, column=1, sticky='w', padx=5, pady=2)

    def _enforce_vertical_only(self):
        """Скрывает все альтернативные типы лестниц, оставляя только вертикальные."""
        self.ladder_type = 'vertical'

        # Ограничиваем список доступных типов, если он существует
        if hasattr(self, 'type_names_display'):
            vertical_caption = self.type_names_display.get('vertical', 'Вертикальная')
            self.type_names_display = {'vertical': vertical_caption}

        # Удаляем кнопки переключения типа кроме вертикальной
        if hasattr(self, 'type_buttons'):
            for type_key, button in list(self.type_buttons.items()):
                if type_key != 'vertical':
                    button.destroy()
                    self.type_buttons.pop(type_key, None)

        # Удаляем вкладки/фреймы прочих типов
        if hasattr(self, 'type_tabs'):
            for type_key, tab_frame in list(self.type_tabs.items()):
                if type_key != 'vertical':
                    tab_frame.destroy()
                    self.type_tabs.pop(type_key, None)

        # Если есть метод переключения типов - фиксируем его на вертикальном
        if hasattr(self, '_switch_to_type'):
            original_switch = self._switch_to_type

            def _locked_switch(new_type):
                original_switch('vertical')

            self._switch_to_type = _locked_switch

            # На всякий случай активируем вертикальную вкладку
            original_switch('vertical')
    
    def _create_vertical_fields(self):
        """Создаёт набор полей для вертикальной лестницы"""
        row = 1
        
        ttk.Label(self.fields_frame, text="Высота (м)*:").grid(row=row, column=0, sticky='w', padx=(0, 5), pady=4)
        self.entries['height'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['height'].grid(row=row, column=1, sticky='w', pady=4, padx=(0, 20))
        
        ttk.Label(self.fields_frame, text="Ширина (м)*:").grid(row=row, column=2, sticky='w', padx=(10, 5), pady=4)
        self.entries['width'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['width'].grid(row=row, column=3, sticky='w', pady=4, padx=(0, 5))
        row += 1
        
        ttk.Label(self.fields_frame, text="Кол-во ступеней (шт.)*:").grid(row=row, column=0, sticky='w', padx=(0, 5), pady=4)
        self.entries['steps_count'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['steps_count'].grid(row=row, column=1, sticky='w', pady=4, padx=(0, 20))
        
        ttk.Label(self.fields_frame, text="Точки крепления (шт.)*:").grid(row=row, column=2, sticky='w', padx=(10, 5), pady=4)
        self.entries['mount_points'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['mount_points'].grid(row=row, column=3, sticky='w', pady=4, padx=(0, 5))
        row += 1
        
        ttk.Label(self.fields_frame, text="Площадка длина (м):").grid(row=row, column=0, sticky='w', padx=(0, 5), pady=4)
        self.entries['platform_length'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['platform_length'].grid(row=row, column=1, sticky='w', pady=4, padx=(0, 20))
        
        ttk.Label(self.fields_frame, text="Площадка ширина (м):").grid(row=row, column=2, sticky='w', padx=(10, 5), pady=4)
        self.entries['platform_width'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['platform_width'].grid(row=row, column=3, sticky='w', pady=4, padx=(0, 5))
        row += 1
        
        ttk.Label(self.fields_frame, text="Высота огражд. (м):").grid(row=row, column=0, sticky='w', padx=(0, 5), pady=4)
        self.entries['fence_height'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['fence_height'].grid(row=row, column=1, sticky='w', pady=4, padx=(0, 20))
        
        ttk.Label(self.fields_frame, text="Расст. от стены (м):").grid(row=row, column=2, sticky='w', padx=(10, 5), pady=4)
        self.entries['wall_distance'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['wall_distance'].grid(row=row, column=3, sticky='w', pady=4, padx=(0, 5))
        row += 1
        
        ttk.Label(self.fields_frame, text="Расст. от земли (м):").grid(row=row, column=0, sticky='w', padx=(0, 5), pady=4)
        self.entries['ground_distance'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['ground_distance'].grid(row=row, column=1, sticky='w', pady=4, padx=(0, 20))
        
        ttk.Label(self.fields_frame, text="Между ступенями (м)*:").grid(row=row, column=2, sticky='w', padx=(10, 5), pady=4)
        self.entries['step_distance'] = ttk.Entry(self.fields_frame, width=10)
        self.entries['step_distance'].grid(row=row, column=3, sticky='w', pady=4, padx=(0, 5))
    
    def _delete_self(self):
        """Удаляет этот виджет"""
        if self.on_delete:
            self.on_delete(self)
    
    def get_data(self):
        """Возвращает данные лестницы"""
        data = {
            'number': self.ladder_num,
            'name': self.name_entry.get(),
            'ladder_type': 'vertical',
            'damage_found': self.damage_found_var.get(),
            'mount_violation_found': self.mount_violation_var.get(),
            'weld_violation_found': self.weld_violation_var.get(),
            'paint_compliant': self.paint_compliant_var.get(),
        }
        
        for key, entry in self.entries.items():
            data[key] = entry.get()
        
        return data
    
    def set_data(self, data):
        """Устанавливает данные лестницы"""
        source_type = data.get('ladder_type', 'vertical')
        if source_type != 'vertical':
            app_logger.warning(
                f"Лестница №{self.ladder_num}: получен устаревший тип '{source_type}', данные будут интерпретированы как вертикальные"
            )
        
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get('name', ''))
        
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, data.get(key, ''))
        
        self.damage_found_var.set(data.get('damage_found', False))
        self.mount_violation_var.set(data.get('mount_violation_found', False))
        self.weld_violation_var.set(data.get('weld_violation_found', False))
        self.paint_compliant_var.set(data.get('paint_compliant', True))
    
    def clear(self):
        """Очищает все поля"""
        self.name_entry.delete(0, tk.END)
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        self.damage_found_var.set(False)
        self.mount_violation_var.set(False)
        self.weld_violation_var.set(False)
        self.paint_compliant_var.set(True)


class LaddersManager(tk.Frame):
    """Менеджер списка лестниц"""
    
    def __init__(self, parent, ladder_type_var=None):
        super().__init__(parent)
        
        self.ladders = []
        self.ladder_counter = 0
        
        # Кнопка добавления (сверху)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="➕ Добавить лестницу", 
                  command=self.add_ladder).pack(side='left', padx=5)
        
        self.count_label = ttk.Label(btn_frame, text="Всего лестниц: 0")
        self.count_label.pack(side='left', padx=10)
        
        # Контейнер для лестниц с прокруткой
        self.canvas = tk.Canvas(self, bg='#2b2b2b', highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Обновление ширины окна в canvas при изменении размера
        def configure_canvas(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.canvas.bind("<Configure>", configure_canvas)
        
        # Прокрутка колёсиком мыши
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        # Добавляем первую лестницу
        self.add_ladder()
    
    def _on_mousewheel(self, event):
        """Обработка прокрутки колёсиком мыши"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def add_ladder(self):
        """Добавляет новую лестницу"""
        self.ladder_counter += 1
        
        ladder = LadderWidget(self.scrollable_frame, self.ladder_counter, self._remove_ladder)
        ladder.pack(fill='x', pady=5, padx=5)

        # Гарантируем, что каждая лестница остаётся вертикальной
        if hasattr(ladder, '_enforce_vertical_only'):
            ladder._enforce_vertical_only()
        
        self.ladders.append(ladder)
        self._update_count()
        
        app_logger.info(f"Добавлена вертикальная лестница №{self.ladder_counter}")
    
    def _remove_ladder(self, ladder_widget):
        """Удаляет лестницу"""
        if len(self.ladders) <= 1:
            messagebox.showwarning("Предупреждение", "Должна быть минимум одна лестница")
            return
        
        result = messagebox.askyesno(
            "Подтверждение", 
            f"Удалить лестницу №{ladder_widget.ladder_num}?"
        )
        
        if result:
            ladder_widget.destroy()
            self.ladders.remove(ladder_widget)
            self._update_count()
            app_logger.info(f"Удалена лестница №{ladder_widget.ladder_num}")
    
    def _update_count(self):
        """Обновляет счётчик лестниц"""
        self.count_label.config(text=f"Всего лестниц: {len(self.ladders)}")
    
    def get_all_ladders_data(self):
        """Возвращает данные всех лестниц"""
        return [ladder.get_data() for ladder in self.ladders]
    
    def set_ladders_data(self, ladders_list):
        """Устанавливает данные лестниц из списка"""
        # Удаляем все существующие
        for ladder in self.ladders[:]:
            ladder.destroy()
        self.ladders.clear()
        self.ladder_counter = 0
        
        # Добавляем новые
        if not ladders_list:
            self.add_ladder()  # Минимум одна
        else:
            for data in ladders_list:
                self.ladder_counter += 1
                ladder = LadderWidget(self.scrollable_frame, self.ladder_counter, self._remove_ladder)
                ladder.pack(fill='x', pady=5, padx=5)
                if hasattr(ladder, '_enforce_vertical_only'):
                    ladder._enforce_vertical_only()
                ladder.set_data(data)
                self.ladders.append(ladder)
        
        self._update_count()
    
    def clear_all(self):
        """Очищает все лестницы"""
        # Оставляем только одну пустую
        for ladder in self.ladders[:]:
            ladder.destroy()
        self.ladders.clear()
        self.ladder_counter = 0
        
        self.add_ladder()

