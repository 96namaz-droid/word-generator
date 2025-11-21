"""
Модуль для управления списком маршей и площадок для маршевых лестниц
"""
import tkinter as tk
from tkinter import ttk, messagebox
from logger import app_logger


class MarchWidget(tk.Frame):
    """Виджет для ввода данных одного марша с площадкой"""
    
    def __init__(self, parent, march_num, on_delete_callback):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=1, padx=5, pady=5)
        
        self.march_num = march_num
        self.on_delete = on_delete_callback
        self.has_march = True
        self.has_platform = True
        
        # Заголовок с номером и кнопкой удаления
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', pady=(0, 5))
        
        self.header_label = ttk.Label(
            header_frame,
            text=f"Элемент №{march_num}",
            font=('Arial', 10, 'bold')
        )
        self.header_label.pack(side='left')
        
        if march_num > 1:  # Первый элемент нельзя удалить полностью
            ttk.Button(header_frame, text="✖ Удалить всё", width=12,
                      command=self._delete_self).pack(side='right', padx=2)
        
        # Фрейм с полями
        self.fields_frame = ttk.Frame(self)
        self.fields_frame.pack(fill='x', pady=5)
        
        self.entries = {}
        self.march_widgets = []  # Список виджетов секции марша
        self.platform_widgets = []  # Список виджетов секции площадки
        self._create_fields()
        
        self.fields_frame.columnconfigure(1, weight=1)
        self.fields_frame.columnconfigure(3, weight=1)
    
    def _create_fields(self):
        """Создаёт набор полей для марша и площадки"""
        row = 0
        
        # Марш
        march_header_frame = ttk.Frame(self.fields_frame)
        march_header_frame.grid(row=row, column=0, columnspan=4, sticky='ew', pady=(0, 5))
        march_label = ttk.Label(march_header_frame, text="Марш:", font=('Arial', 9, 'bold'))
        march_label.pack(side='left')
        self.march_delete_btn = ttk.Button(march_header_frame, text="✖ Удалить марш", width=12,
                                           command=self._delete_march)
        self.march_delete_btn.pack(side='right')
        self.march_widgets.append(march_header_frame)
        row += 1
        
        # Поля марша
        march_fields = [
            ('march_width', 'Ширина марша (м)*:', row, 0),
            ('march_length', 'Длина марша (м)*:', row, 2),
        ]
        for key, label_text, r, col_offset in march_fields:
            label = ttk.Label(self.fields_frame, text=label_text)
            label.grid(row=r, column=col_offset, sticky='w', padx=(0 if col_offset == 0 else 10, 5), pady=4)
            entry = ttk.Entry(self.fields_frame, width=10)
            entry.grid(row=r, column=col_offset + 1, sticky='w', pady=4, padx=(0, 20 if col_offset == 0 else 5))
            self.entries[key] = entry
            self.march_widgets.extend([label, entry])
        row += 1
        
        march_fields2 = [
            ('step_width', 'Ширина ступени (м)*:', row, 0),
            ('step_distance', 'Расстояние между ступенями (м)*:', row, 2),
        ]
        for key, label_text, r, col_offset in march_fields2:
            label = ttk.Label(self.fields_frame, text=label_text)
            label.grid(row=r, column=col_offset, sticky='w', padx=(0 if col_offset == 0 else 10, 5), pady=4)
            entry = ttk.Entry(self.fields_frame, width=10)
            entry.grid(row=r, column=col_offset + 1, sticky='w', pady=4, padx=(0, 20 if col_offset == 0 else 5))
            self.entries[key] = entry
            self.march_widgets.extend([label, entry])
        row += 1
        
        march_fields3 = [
            ('steps_count', 'Количество ступеней*:', row, 0),
            ('march_fence_height', 'Высота ограждений марша (м)*:', row, 2),
        ]
        for key, label_text, r, col_offset in march_fields3:
            label = ttk.Label(self.fields_frame, text=label_text)
            label.grid(row=r, column=col_offset, sticky='w', padx=(0 if col_offset == 0 else 10, 5), pady=4)
            entry = ttk.Entry(self.fields_frame, width=10)
            entry.grid(row=r, column=col_offset + 1, sticky='w', pady=4, padx=(0, 20 if col_offset == 0 else 5))
            self.entries[key] = entry
            self.march_widgets.extend([label, entry])
        row += 1
        
        # Площадка
        platform_header_frame = ttk.Frame(self.fields_frame)
        platform_header_frame.grid(row=row, column=0, columnspan=4, sticky='ew', pady=(10, 5))
        platform_label = ttk.Label(platform_header_frame, text="Площадка:", font=('Arial', 9, 'bold'))
        platform_label.pack(side='left')
        self.platform_delete_btn = ttk.Button(platform_header_frame, text="✖ Удалить площадку", width=14,
                                              command=self._delete_platform)
        self.platform_delete_btn.pack(side='right')
        self.platform_widgets.append(platform_header_frame)
        row += 1
        
        # Поля площадки
        platform_fields1 = [
            ('platform_length', 'Длина площадки (м)*:', row, 0),
            ('platform_width', 'Ширина площадки (м)*:', row, 2),
        ]
        for key, label_text, r, col_offset in platform_fields1:
            label = ttk.Label(self.fields_frame, text=label_text)
            label.grid(row=r, column=col_offset, sticky='w', padx=(0 if col_offset == 0 else 10, 5), pady=4)
            entry = ttk.Entry(self.fields_frame, width=10)
            entry.grid(row=r, column=col_offset + 1, sticky='w', pady=4, padx=(0, 20 if col_offset == 0 else 5))
            self.entries[key] = entry
            self.platform_widgets.extend([label, entry])
        row += 1
        
        platform_fields2 = [
            ('platform_fence_height', 'Высота ограждений площадки (м)*:', row, 0),
            ('platform_ground_distance', 'Расстояние от площадки до земли (м):', row, 2),
        ]
        for key, label_text, r, col_offset in platform_fields2:
            label = ttk.Label(self.fields_frame, text=label_text)
            label.grid(row=r, column=col_offset, sticky='w', padx=(0 if col_offset == 0 else 10, 5), pady=4)
            entry = ttk.Entry(self.fields_frame, width=10)
            entry.grid(row=r, column=col_offset + 1, sticky='w', pady=4, padx=(0, 20 if col_offset == 0 else 5))
            self.entries[key] = entry
            self.platform_widgets.extend([label, entry])
        row += 1
    
    def _delete_self(self):
        """Удаляет этот виджет"""
        if self.on_delete:
            self.on_delete(self)
    
    def _delete_march(self):
        """Удаляет данные марша"""
        if not self.has_march:
            return
        
        result = messagebox.askyesno(
            "Подтверждение",
            f"Удалить данные марша №{self.march_num}?"
        )
        
        if result:
            # Очищаем поля марша
            march_keys = ['march_width', 'march_length', 'step_width', 'step_distance', 
                         'steps_count', 'march_fence_height']
            for key in march_keys:
                if key in self.entries:
                    self.entries[key].delete(0, tk.END)
            
            # Скрываем виджеты марша
            for widget in self.march_widgets:
                widget.grid_remove()
            
            self.has_march = False
            self.march_delete_btn.config(text="➕ Восстановить марш", command=self._restore_march)
            self._update_header()
            app_logger.info(f"Удален марш №{self.march_num}")
    
    def _restore_march(self):
        """Восстанавливает секцию марша"""
        if self.has_march:
            return
        
        # Показываем виджеты марша
        for widget in self.march_widgets:
            widget.grid()
        
        self.has_march = True
        self.march_delete_btn.config(text="✖ Удалить марш", command=self._delete_march)
        self._update_header()
        app_logger.info(f"Восстановлен марш №{self.march_num}")
    
    def _delete_platform(self):
        """Удаляет данные площадки"""
        if not self.has_platform:
            return
        
        result = messagebox.askyesno(
            "Подтверждение",
            f"Удалить данные площадки №{self.march_num}?"
        )
        
        if result:
            # Очищаем поля площадки
            platform_keys = ['platform_length', 'platform_width', 'platform_fence_height', 
                            'platform_ground_distance']
            for key in platform_keys:
                if key in self.entries:
                    self.entries[key].delete(0, tk.END)
            
            # Скрываем виджеты площадки
            for widget in self.platform_widgets:
                widget.grid_remove()
            
            self.has_platform = False
            self.platform_delete_btn.config(text="➕ Восстановить площадку", command=self._restore_platform)
            self._update_header()
            app_logger.info(f"Удалена площадка №{self.march_num}")
    
    def _restore_platform(self):
        """Восстанавливает секцию площадки"""
        if self.has_platform:
            return
        
        # Показываем виджеты площадки
        for widget in self.platform_widgets:
            widget.grid()
        
        self.has_platform = True
        self.platform_delete_btn.config(text="✖ Удалить площадку", command=self._delete_platform)
        self._update_header()
        app_logger.info(f"Восстановлена площадка №{self.march_num}")
    
    def _update_header(self):
        """Обновляет заголовок в зависимости от наличия марша и площадки"""
        parts = []
        if self.has_march:
            parts.append("Марш")
        if self.has_platform:
            parts.append("Площадка")
        
        if parts:
            self.header_label.config(text=f"{', '.join(parts)} №{self.march_num}")
        else:
            self.header_label.config(text=f"Элемент №{self.march_num} (пустой)")
    
    def get_data(self):
        """Возвращает данные марша и площадки"""
        data = {
            'number': self.march_num,
            'has_march': self.has_march,
            'has_platform': self.has_platform,
        }
        
        for key, entry in self.entries.items():
            data[key] = entry.get()
        
        return data
    
    def set_data(self, data):
        """Устанавливает данные марша и площадки"""
        # Восстанавливаем состояние марша и площадки
        self.has_march = data.get('has_march', True)
        self.has_platform = data.get('has_platform', True)
        
        # Показываем/скрываем виджеты в зависимости от состояния
        if self.has_march:
            for widget in self.march_widgets:
                widget.grid()
            self.march_delete_btn.config(text="✖ Удалить марш", command=self._delete_march)
        else:
            for widget in self.march_widgets:
                widget.grid_remove()
            self.march_delete_btn.config(text="➕ Восстановить марш", command=self._restore_march)
        
        if self.has_platform:
            for widget in self.platform_widgets:
                widget.grid()
            self.platform_delete_btn.config(text="✖ Удалить площадку", command=self._delete_platform)
        else:
            for widget in self.platform_widgets:
                widget.grid_remove()
            self.platform_delete_btn.config(text="➕ Восстановить площадку", command=self._restore_platform)
        
        # Заполняем поля
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, data.get(key, ''))
        
        self._update_header()
    
    def clear(self):
        """Очищает все поля и восстанавливает секции"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # Восстанавливаем секции марша и площадки
        if not self.has_march:
            self._restore_march()
        if not self.has_platform:
            self._restore_platform()


class MarchesManager(tk.Frame):
    """Менеджер списка маршей и площадок"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.marches = []
        self.march_counter = 0
        
        # Кнопка добавления (сверху)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="➕ Добавить марш и площадку", 
                  command=self.add_march).pack(side='left', padx=5)
        
        self.count_label = ttk.Label(btn_frame, text="Всего маршей: 0")
        self.count_label.pack(side='left', padx=10)
        
        # Контейнер для маршей с прокруткой
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
        
        # Добавляем первый марш
        self.add_march()
    
    def _on_mousewheel(self, event):
        """Обработка прокрутки колёсиком мыши"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def add_march(self):
        """Добавляет новый марш с площадкой"""
        self.march_counter += 1
        
        march = MarchWidget(self.scrollable_frame, self.march_counter, self._remove_march)
        march.pack(fill='x', pady=5, padx=5)
        
        self.marches.append(march)
        self._update_count()
        
        app_logger.info(f"Добавлен марш+площадка №{self.march_counter}")
    
    def _remove_march(self, march_widget):
        """Удаляет марш"""
        if len(self.marches) <= 1:
            messagebox.showwarning("Предупреждение", "Должен быть минимум один марш")
            return
        
        result = messagebox.askyesno(
            "Подтверждение", 
            f"Удалить марш и площадку №{march_widget.march_num}?"
        )
        
        if result:
            march_widget.destroy()
            self.marches.remove(march_widget)
            self._update_count()
            app_logger.info(f"Удален марш+площадка №{march_widget.march_num}")
    
    def _update_count(self):
        """Обновляет счётчик маршей"""
        self.count_label.config(text=f"Всего маршей: {len(self.marches)}")
    
    def get_all_marches_data(self):
        """Возвращает данные всех маршей"""
        return [march.get_data() for march in self.marches]
    
    def set_marches_data(self, marches_list):
        """Устанавливает данные маршей из списка"""
        # Удаляем все существующие
        for march in self.marches[:]:
            march.destroy()
        self.marches.clear()
        self.march_counter = 0
        
        # Добавляем новые
        if not marches_list:
            self.add_march()  # Минимум один
        else:
            for data in marches_list:
                self.march_counter += 1
                march = MarchWidget(self.scrollable_frame, self.march_counter, self._remove_march)
                march.pack(fill='x', pady=5, padx=5)
                march.set_data(data)
                self.marches.append(march)
        
        self._update_count()
    
    def clear_all(self):
        """Очищает все марши"""
        # Оставляем только один пустой
        for march in self.marches[:]:
            march.destroy()
        self.marches.clear()
        self.march_counter = 0
        
        self.add_march()

