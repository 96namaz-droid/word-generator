"""
Графический интерфейс приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime
import os
import subprocess
import sys

from document_generator import DocumentGenerator
from history_manager import HistoryManager
from validator import DataValidator
from contract_parser import ContractParser
from contracts_db import ContractsDatabase
from ladder_manager import LaddersManager
from march_manager import MarchesManager
from weather_service import WeatherService
from logger import app_logger
import config


class DynamicTable(tk.Frame):
    """Виджет динамической таблицы"""
    
    def __init__(self, parent, initial_rows=5, initial_cols=4):
        super().__init__(parent)
        
        self.rows = initial_rows
        self.cols = initial_cols
        self.cells = []
        
        # Контейнер для таблицы с прокруткой
        self.canvas = tk.Canvas(self, bg='#2b2b2b', height=300, highlightthickness=0)
        self.scrollbar_y = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # Размещение элементов
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scrollbar_y.grid(row=0, column=1, sticky='ns')
        self.scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Кнопки управления
        self.controls_frame = ttk.Frame(self)
        self.controls_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(self.controls_frame, text="➕ Добавить строку", 
                  command=self.add_row).pack(side='left', padx=5)
        ttk.Button(self.controls_frame, text="➖ Удалить строку", 
                  command=self.remove_row).pack(side='left', padx=5)
        ttk.Button(self.controls_frame, text="➕ Добавить колонку", 
                  command=self.add_column).pack(side='left', padx=5)
        ttk.Button(self.controls_frame, text="➖ Удалить колонку", 
                  command=self.remove_column).pack(side='left', padx=5)
        
        # Создание начальной таблицы
        self._create_table()
    
    def _create_table(self):
        """Создает таблицу"""
        # Очистка существующих ячеек
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.cells = []
        
        for i in range(self.rows):
            row_cells = []
            for j in range(self.cols):
                cell = ttk.Entry(self.scrollable_frame, width=15)
                cell.grid(row=i, column=j, padx=2, pady=2, sticky='ew')
                
                # Заполнение заголовков
                if i == 0:
                    cell.insert(0, f"Колонка {j+1}")
                
                row_cells.append(cell)
            self.cells.append(row_cells)
    
    def add_row(self):
        """Добавляет новую строку"""
        self.rows += 1
        row_cells = []
        for j in range(self.cols):
            cell = ttk.Entry(self.scrollable_frame, width=15)
            cell.grid(row=self.rows-1, column=j, padx=2, pady=2, sticky='ew')
            row_cells.append(cell)
        self.cells.append(row_cells)
        app_logger.info("Добавлена строка в таблицу")
    
    def remove_row(self):
        """Удаляет последнюю строку"""
        if self.rows > 2:  # Минимум заголовок + 1 строка
            for cell in self.cells[-1]:
                cell.destroy()
            self.cells.pop()
            self.rows -= 1
            app_logger.info("Удалена строка из таблицы")
        else:
            messagebox.showwarning("Предупреждение", 
                                 "Нельзя удалить все строки. Минимум: заголовок + 1 строка данных")
    
    def add_column(self):
        """Добавляет новую колонку"""
        self.cols += 1
        for i, row in enumerate(self.cells):
            cell = ttk.Entry(self.scrollable_frame, width=15)
            cell.grid(row=i, column=self.cols-1, padx=2, pady=2, sticky='ew')
            if i == 0:
                cell.insert(0, f"Колонка {self.cols}")
            row.append(cell)
        app_logger.info("Добавлена колонка в таблицу")
    
    def remove_column(self):
        """Удаляет последнюю колонку"""
        if self.cols > 2:  # Минимум 2 колонки
            for row in self.cells:
                row[-1].destroy()
                row.pop()
            self.cols -= 1
            app_logger.info("Удалена колонка из таблицы")
        else:
            messagebox.showwarning("Предупреждение", 
                                 "Нельзя удалить все колонки. Минимум: 2 колонки")
    
    def get_data(self):
        """Возвращает данные таблицы"""
        data = []
        for row in self.cells:
            row_data = [cell.get() for cell in row]
            data.append(row_data)
        return data
    
    def set_data(self, data):
        """Устанавливает данные таблицы"""
        if not data:
            return
        
        # Подгонка размеров таблицы
        target_rows = len(data)
        target_cols = len(data[0]) if data else 2
        
        # Пересоздание таблицы с нужными размерами
        self.rows = target_rows
        self.cols = target_cols
        self._create_table()
        
        # Заполнение данными
        for i, row_data in enumerate(data):
            for j, value in enumerate(row_data):
                if i < len(self.cells) and j < len(self.cells[i]):
                    self.cells[i][j].delete(0, tk.END)
                    self.cells[i][j].insert(0, str(value))


class MainApplication(tk.Tk):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        self.title(config.WINDOW_TITLE)
        self.geometry(config.WINDOW_SIZE)
        
        # Инициализация компонентов
        self.generator = DocumentGenerator()
        self.history_manager = HistoryManager()
        self.validator = DataValidator()
        self.contracts_db = ContractsDatabase()
        self.weather_service = WeatherService()

        # Протокольные формы
        self.protocol_type_var = tk.StringVar(value="vertical")
        self.protocol_frames: dict[str, list[tk.Widget]] = {
            "vertical": [],
            "stair": [],
            "roof": [],
        }
        self._frame_pack_options: dict[tk.Widget, dict] = {}
        self.stair_fields: dict[str, tk.StringVar] = {}
        self.marches_manager: MarchesManager | None = None
        self.roof_fields: dict[str, tk.StringVar] = {}
        self.protocol_selector_combo: ttk.Combobox | None = None
        self.protocol_choices = [
            ("vertical", "Вертикальная пожарная лестница"),
            ("stair", "Маршевая лестница"),
            ("roof", "Ограждение кровли"),
        ]
        self.protocol_label_by_key = {key: label for key, label in self.protocol_choices}
        self.protocol_key_by_label = {label: key for key, label in self.protocol_choices}
        self.protocol_selector_var = tk.StringVar(value=self.protocol_label_by_key["vertical"])
        
        # Настройка UI
        self._setup_ui()
        
        # Загрузка последних данных
        self._load_recent_data()
        
        # Автоматическое обновление базы договоров при старте
        self._auto_update_contracts_database()
        
        app_logger.info("Приложение запущено")
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        # Применяем темную тему
        self._apply_dark_theme()
        
        # Главный контейнер с прокруткой
        main_canvas = tk.Canvas(self, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        self.scrollable_main = ttk.Frame(main_canvas)
        
        self.scrollable_main.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_main, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Стили
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'), foreground='#ffffff', background='#2b2b2b')
        style.configure('Section.TLabel', font=('Arial', 10, 'bold'), foreground='#ffffff', background='#2b2b2b')
        
        # Создаем все секции
        self._create_sections()
    
    def _apply_dark_theme(self):
        """Применяет темную тему к приложению"""
        style = ttk.Style()
        
        # Темный фон
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        select_bg = '#404040'
        select_fg = '#ffffff'
        
        # Настройка основного окна
        self.configure(bg=bg_color)
        
        # Настройка стилей ttk
        style.theme_use('clam')  # Используем clam тему как базу
        
        # Настройка общих цветов
        style.configure('.', background=bg_color, foreground=fg_color, fieldbackground='#3c3c3c')
        
        # Frame
        style.configure('TFrame', background=bg_color)
        
        # Label
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        
        # LabelFrame
        style.configure('TLabelframe', background=bg_color, foreground=fg_color, bordercolor='#555555')
        style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color)
        
        # Entry
        style.configure('TEntry', fieldbackground='#3c3c3c', foreground=fg_color, insertcolor=fg_color, bordercolor='#555555')
        style.map('TEntry', 
                 fieldbackground=[('readonly', '#2b2b2b'), ('disabled', '#2b2b2b')],
                 foreground=[('readonly', '#888888'), ('disabled', '#666666')])
        
        # Button
        style.configure('TButton', background='#404040', foreground=fg_color, bordercolor='#555555', 
                       focuscolor='none', lightcolor='#555555', darkcolor='#222222')
        style.map('TButton',
                 background=[('active', '#505050'), ('pressed', '#303030')],
                 foreground=[('active', fg_color)])
        
        # Checkbutton
        style.configure('TCheckbutton', background=bg_color, foreground=fg_color)
        style.map('TCheckbutton',
                 background=[('active', bg_color)],
                 foreground=[('active', fg_color)])
        
        # Combobox
        style.configure('TCombobox', fieldbackground='#3c3c3c', background='#404040', 
                       foreground=fg_color, arrowcolor=fg_color, bordercolor='#555555')
        style.map('TCombobox',
                 fieldbackground=[('readonly', '#3c3c3c')],
                 selectbackground=[('readonly', select_bg)],
                 selectforeground=[('readonly', select_fg)])
        
        # Scrollbar
        style.configure('Vertical.TScrollbar', background='#404040', troughcolor='#2b2b2b',
                       bordercolor='#555555', arrowcolor=fg_color)
        style.map('Vertical.TScrollbar',
                 background=[('active', '#505050')])
        
        style.configure('Horizontal.TScrollbar', background='#404040', troughcolor='#2b2b2b',
                       bordercolor='#555555', arrowcolor=fg_color)
        style.map('Horizontal.TScrollbar',
                 background=[('active', '#505050')])

    # --- Управление протокольными секциями ------------------------------------

    def _remember_protocol_frame(self, protocol: str, frame: tk.Widget, **pack_kwargs) -> None:
        """Сохраняет фрейм, чтобы можно было скрывать/показывать по типу протокола."""
        self.protocol_frames.setdefault(protocol, []).append(frame)
        if pack_kwargs:
            self._frame_pack_options[frame] = pack_kwargs

    def _update_protocol_sections_visibility(self):
        """Показывает только те секции, которые относятся к выбранному типу протокола."""
        current = self.protocol_type_var.get()
        for frames in self.protocol_frames.values():
            for frame in frames:
                frame.pack_forget()
        for frame in self.protocol_frames.get(current, []):
            self._show_frame(frame)

    def _show_frame(self, frame: tk.Widget):
        opts = self._frame_pack_options.get(frame)
        if not opts:
            return
        if frame.winfo_manager() != 'pack':
            frame.pack(**opts)
        
    def _create_sections(self):
        """Создает все секции интерфейса"""
        # Заголовок
        ttk.Label(self.scrollable_main, text="Генератор Word-отчётов", 
                 style='Title.TLabel').pack(pady=10)
        
        # Выбор типа протокола
        self._create_protocol_selector()
        
        # Основная информация
        self._create_main_info_section()

        # Поля для разных типов протокола
        self._create_stair_section()
        self._create_roof_section()
        
        # Список лестниц
        ladders_frame = self._create_ladders_section()
        
        # Условия проведения испытаний
        self._create_test_conditions_section()
        
        # Визуальный осмотр лестниц
        self._create_visual_inspection_section()
        # Обновляем метку после создания секции
        self._update_visual_inspection_label()
        
        # Соответствие нормам
        compliance_frame = self._create_compliance_section()
        
        # Информация о таблице результатов
        table_info_frame = self._create_table_info_section()
        
        # Кнопки действий
        self._create_action_buttons()
        
        # Статус-бар
        self.status_label = ttk.Label(self, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Регистрация вертикальных секций для управления видимостью
        if ladders_frame:
            self._remember_protocol_frame("vertical", ladders_frame, fill='x', padx=10, pady=5)
        if compliance_frame:
            self._remember_protocol_frame("vertical", compliance_frame, fill='x', padx=10, pady=5)
        if table_info_frame:
            self._remember_protocol_frame("vertical", table_info_frame, fill='x', padx=10, pady=5)

        self._update_protocol_sections_visibility()

    def _create_protocol_selector(self):
        """Секция выбора типа протокола"""
        frame = ttk.LabelFrame(self.scrollable_main, text="Тип протокола", padding=10)
        frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame, text="Выберите тип:").grid(row=0, column=0, sticky='w', pady=5)
        values = [label for _, label in self.protocol_choices]
        self.protocol_selector_combo = ttk.Combobox(
            frame,
            textvariable=self.protocol_selector_var,
            values=values,
            state='readonly',
            width=40,
        )
        self.protocol_selector_combo.grid(row=0, column=1, sticky='w', pady=5, padx=5)
        self.protocol_selector_combo.current(0)
        self.protocol_selector_combo.bind('<<ComboboxSelected>>', self._on_protocol_selector_change)

        ttk.Label(
            frame,
            text="У каждого типа протокола — свои поля ввода и своя логика генерации.",
            font=('Arial', 9),
            foreground='#bbbbbb'
        ).grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))

        frame.columnconfigure(1, weight=1)
    
    def _create_main_info_section(self):
        """Создает секцию основной информации"""
        frame = ttk.LabelFrame(self.scrollable_main, text="Основная информация", padding=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        # Дата
        ttk.Label(frame, text="Дата:").grid(row=0, column=0, sticky='w', pady=5)
        self.date_entry = DateEntry(frame, width=20, date_pattern='dd.mm.yyyy', locale='ru_RU')
        self.date_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Заказчик
        ttk.Label(frame, text="Заказчик:").grid(row=1, column=0, sticky='w', pady=5)
        
        # Комбинированный виджет (combobox + кнопка)
        customer_frame = ttk.Frame(frame)
        customer_frame.grid(row=1, column=1, sticky='ew', pady=5)
        
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=40)
        self.customer_combo.pack(side='left', fill='x', expand=True)
        self.customer_combo['values'] = config.DEFAULT_CUSTOMERS
        self.customer_combo.bind('<<ComboboxSelected>>', self._on_customer_selected)
        
        ttk.Button(customer_frame, text="📂", width=3, 
                  command=self._load_contract).pack(side='left', padx=2)
        ttk.Button(customer_frame, text="🔄", width=3, 
                  command=self._update_contracts_database).pack(side='left', padx=2)
        
        # Адрес/наименование объекта (объединённое поле)
        ttk.Label(frame, text="Адрес/наименование испытываемого объекта:").grid(row=2, column=0, sticky='w', pady=5)
        
        # Используем Text виджет для многострочного ввода
        object_text_frame = ttk.Frame(frame)
        object_text_frame.grid(row=2, column=1, sticky='ew', pady=5)
        
        self.object_full_address_text = tk.Text(object_text_frame, height=3, width=50, wrap=tk.WORD, font=('Arial', 9),
                                                bg='#3c3c3c', fg='#ffffff', insertbackground='#ffffff', 
                                                selectbackground='#404040', selectforeground='#ffffff')
        self.object_full_address_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbar для текстового поля
        scrollbar = ttk.Scrollbar(object_text_frame, command=self.object_full_address_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.object_full_address_text.config(yscrollcommand=scrollbar.set)
        
        frame.columnconfigure(1, weight=1)
    
    def _create_stair_section(self):
        """Форма для маршевых лестниц (скрыта по умолчанию)"""
        frame = ttk.LabelFrame(self.scrollable_main, text="Характеристики лестницы", padding=10)
        
        # Поле для названия лестницы (на всю ширину)
        ttk.Label(frame, text="Название лестницы:").grid(row=0, column=0, sticky='w', pady=3)
        var_name = tk.StringVar()
        entry_name = ttk.Entry(frame, textvariable=var_name, width=30)
        entry_name.grid(row=0, column=1, sticky='ew', pady=3, padx=5)
        self.stair_fields['ladder_name'] = var_name
        
        # Поле для количества точек крепления
        ttk.Label(frame, text="Количество точек крепления (шт.):").grid(row=1, column=0, sticky='w', pady=3)
        var_mount_points = tk.StringVar()
        entry_mount_points = ttk.Entry(frame, textvariable=var_mount_points, width=30)
        entry_mount_points.grid(row=1, column=1, sticky='ew', pady=3, padx=5)
        self.stair_fields['mount_points'] = var_mount_points
        
        frame.columnconfigure(1, weight=1)
        
        # Менеджер маршей и площадок
        marches_frame = ttk.LabelFrame(frame, text="Марши и площадки", padding=10)
        marches_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        marches_frame.columnconfigure(0, weight=1)
        
        self.marches_manager = MarchesManager(marches_frame)
        self.marches_manager.pack(fill='both', expand=True)

        self._remember_protocol_frame("stair", frame, fill='x', padx=10, pady=5)

    def _create_roof_section(self):
        """Форма для ограждений кровли (скрыта по умолчанию)"""
        frame = ttk.LabelFrame(self.scrollable_main, text="Ограждение кровли", padding=10)
        entries = [
            ("Наименование ограждений", "fence_name"),
            ("Длина участка (м)", "length"),
            ("Высота ограждения (м)", "height"),
            ("Количество точек крепления", "mount_points"),
            ("Шаг крепления (м)", "mount_pitch"),
            ("Высота ограждения от парапета (м)", "parapet_height"),
        ]
        frame.columnconfigure(1, weight=1)
        for idx, (label_text, key) in enumerate(entries):
            ttk.Label(frame, text=label_text).grid(row=idx, column=0, sticky='w', pady=3)
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var)
            entry.grid(row=idx, column=1, sticky='ew', pady=3, padx=5)
            self.roof_fields[key] = var

        # Убрано автозаполнение для mount_pitch

        self._remember_protocol_frame("roof", frame, fill='x', padx=10, pady=5)
    
    def _create_ladders_section(self):
        """Создает секцию со списком лестниц"""
        frame = ttk.LabelFrame(self.scrollable_main, text="Испытываемые лестницы/ограждения", padding=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        info_label = ttk.Label(frame, text="ℹ️ Все лестницы рассматриваются как вертикальные конструкции", 
                              font=('Arial', 8), foreground='#888888')
        info_label.pack(anchor='w', pady=(0, 5))
        
        self.ladders_manager = LaddersManager(frame, None)
        self.ladders_manager.pack(fill='both', expand=False)
        return frame
    
    def _create_test_conditions_section(self):
        """Создает секцию условий проведения испытаний"""
        frame = ttk.LabelFrame(self.scrollable_main, text="Условия проведения испытаний", padding=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        # Время проведения
        ttk.Label(frame, text="Время проведения:").grid(row=0, column=0, sticky='w', pady=5)
        self.test_time_var = tk.StringVar(value="дневное время")
        test_time_combo = ttk.Combobox(frame, textvariable=self.test_time_var, width=30, state='readonly')
        test_time_combo['values'] = ("дневное время", "ночное время")
        test_time_combo.grid(row=0, column=1, sticky='w', pady=5, padx=5)
        
        # Температура
        ttk.Label(frame, text="Температура воздуха (°C):").grid(row=1, column=0, sticky='w', pady=5)
        self.temperature_entry = ttk.Entry(frame, width=20)
        self.temperature_entry.grid(row=1, column=1, sticky='w', pady=5, padx=5)
        
        # Скорость ветра
        ttk.Label(frame, text="Скорость ветра (м/с):").grid(row=2, column=0, sticky='w', pady=5)
        self.wind_speed_entry = ttk.Entry(frame, width=20)
        self.wind_speed_entry.grid(row=2, column=1, sticky='w', pady=5, padx=5)
        
        # Кнопка автоматического получения погоды
        weather_btn_frame = ttk.Frame(frame)
        weather_btn_frame.grid(row=3, column=0, columnspan=2, sticky='w', pady=10, padx=5)
        
        ttk.Button(weather_btn_frame, text="🌤 Получить текущую погоду (Екатеринбург)", 
                  command=self._update_weather).pack(side='left', padx=5)
        
        self.weather_status_label = ttk.Label(weather_btn_frame, text="", font=('Arial', 8), 
                                              foreground='#888888')
        self.weather_status_label.pack(side='left', padx=10)
    
    def _create_visual_inspection_section(self):
        """Создает секцию визуального осмотра"""
        frame = ttk.LabelFrame(self.scrollable_main, text="Визуальный осмотр лестниц", padding=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        # Внешние повреждения
        damage_frame = ttk.Frame(frame)
        damage_frame.grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
        ttk.Label(damage_frame, text="Внешние повреждения конструкций:").pack(side='left', padx=(0, 10))
        self.damage_found_var = tk.BooleanVar()
        ttk.Checkbutton(damage_frame, text="Обнаружено", variable=self.damage_found_var,
                       command=lambda: self._toggle_inspection('damage')).pack(side='left', padx=5)
        
        # Нарушение крепления
        mount_frame = ttk.Frame(frame)
        mount_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=5)
        self.mount_violation_label = ttk.Label(mount_frame, text="Следы нарушения крепления к стене:")
        self.mount_violation_label.pack(side='left', padx=(0, 10))
        self.mount_violation_var = tk.BooleanVar()
        ttk.Checkbutton(mount_frame, text="Обнаружено", variable=self.mount_violation_var,
                       command=lambda: self._toggle_inspection('mount')).pack(side='left', padx=5)
        
        # Нарушение сварных швов
        weld_frame = ttk.Frame(frame)
        weld_frame.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        ttk.Label(weld_frame, text="Нарушение сварных швов:").pack(side='left', padx=(0, 10))
        self.weld_violation_var = tk.BooleanVar()
        ttk.Checkbutton(weld_frame, text="Обнаружено", variable=self.weld_violation_var,
                       command=lambda: self._toggle_inspection('weld')).pack(side='left', padx=5)
        
        # Защитное покрытие
        paint_frame = ttk.Frame(frame)
        paint_frame.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)
        ttk.Label(paint_frame, text="Защитное покрытие соответствует требованиями ГОСТ 9.302:").pack(side='left', padx=(0, 10))
        self.paint_compliant_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(paint_frame, text="Соответствует", variable=self.paint_compliant_var,
                       command=lambda: self._toggle_inspection('paint')).pack(side='left', padx=5)
    
    def _toggle_inspection(self, field):
        """Обработчик переключения чекбоксов визуального осмотра"""
        # Можно добавить дополнительную логику при необходимости
        pass
    
    def _update_visual_inspection_label(self):
        """Обновляет текст метки нарушения крепления в зависимости от типа протокола"""
        if hasattr(self, 'mount_violation_label'):
            protocol = self.protocol_type_var.get()
            if protocol == 'roof':
                self.mount_violation_label.config(text="Следы нарушения крепления:")
            else:
                self.mount_violation_label.config(text="Следы нарушения крепления к стене:")
    
    def _create_compliance_section(self):
        """Создает секцию соответствия нормам"""
        self.compliance_frame = ttk.LabelFrame(self.scrollable_main, text="Соответствие нормам", padding=10)
        self.compliance_frame.pack(fill='x', padx=10, pady=5)
        
        # Инициализируем хранилище данных по лестницам
        self.ladder_compliance_data = {}
        
        # Контейнер для динамического обновления
        self.compliance_content_frame = ttk.Frame(self.compliance_frame)
        self.compliance_content_frame.pack(fill='both', expand=True)
        
        # Кнопка обновления списка лестниц
        info_label = ttk.Label(self.compliance_frame, text="ℹ️ Список обновляется автоматически при генерации отчёта", 
                              font=('Arial', 8), foreground='#888888')
        info_label.pack(pady=2)
        
        ttk.Button(self.compliance_frame, text="🔄 Обновить список лестниц вручную", 
                  command=self._update_compliance_ladders).pack(pady=5)
        
        # Соответствие проекту (общее для всех)
        project_frame = ttk.Frame(self.compliance_frame)
        project_frame.pack(fill='x', pady=5)
        self.project_compliant_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(project_frame, text="Соответствует проекту", 
                       variable=self.project_compliant_var,
                       command=self._toggle_project_field).pack(side='left', padx=5)
        
        # Поле для номера проекта
        project_entry_frame = ttk.Frame(self.compliance_frame)
        project_entry_frame.pack(fill='x', pady=5)
        ttk.Label(project_entry_frame, text="Номер проекта:").pack(side='left', padx=(0, 5))
        self.project_number_entry = ttk.Entry(project_entry_frame, width=40)
        self.project_number_entry.pack(side='left', padx=5)
        self.project_number_entry.config(state='disabled')  # По умолчанию отключено
        return self.compliance_frame
    
    def _update_compliance_ladders(self):
        """Обновляет список лестниц в соответствии нормам"""
        # Сохраняем старые значения перед обновлением
        old_compliance_data = {}
        for ladder_num, ldata in self.ladder_compliance_data.items():
            old_compliance_data[ladder_num] = {
                'compliant': ldata['compliance_var'].get(),
                'violations': {key: var.get() for key, var in ldata['violation_vars'].items()}
            }
        
        app_logger.info(f"Сохранены старые данные соответствия: {old_compliance_data}")
        
        # Очищаем старое содержимое
        for widget in self.compliance_content_frame.winfo_children():
            widget.destroy()
        
        self.ladder_compliance_data = {}
        
        # Получаем актуальные данные лестниц
        ladders_data = self.ladders_manager.get_all_ladders_data()
        
        app_logger.info(f"Обновление списка лестниц для соответствия: найдено {len(ladders_data)} лестниц")
        
        if not ladders_data:
            ttk.Label(self.compliance_content_frame, text="Нет лестниц для проверки").pack(pady=10)
            return
        
        # Создаем чекбоксы для каждой лестницы
        for ladder in ladders_data:
            ladder_num = ladder.get('number', 1)
            ladder_name = ladder.get('name', f'Лестница №{ladder_num}')
            # Фрейм для одной лестницы
            ladder_frame = ttk.LabelFrame(self.compliance_content_frame, 
                                         text=f"Лестница №{ladder_num}: {ladder_name if ladder_name else 'Без названия'}", 
                                         padding=5)
            ladder_frame.pack(fill='x', pady=5)
            
            # Чекбокс соответствия ГОСТ для этой лестницы
            compliance_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(ladder_frame, text="Соответствует ГОСТ Р 54253-2009",
                           variable=compliance_var,
                           command=lambda num=ladder_num: self._toggle_ladder_violations(num)).pack(anchor='w', padx=5, pady=2)
            
            # Фрейм для несоответствий этой лестницы (изначально скрыт)
            violations_frame = ttk.LabelFrame(ladder_frame, text="Что не соответствует:", padding=5)
            violations_frame.pack(fill='x', padx=(20, 0), pady=5)
            violations_frame.pack_forget()  # Скрываем по умолчанию
            
            violation_vars = {}
            violations = [
                ('ladder_width', 'Ширина лестницы'),
                ('step_distance', 'Расстояние между ступенями'),
                ('wall_distance', 'Расстояние от стены'),
                ('ground_distance', 'Расстояние от земли'),
                ('platform_length', 'Длина площадки'),
                ('platform_width', 'Ширина площадки'),
                ('fence_height', 'Высота ограждения площадки'),
                ('ladder_fence', 'Ограждение лестницы'),
                ('mount_distance', 'Расстояние между упорами'),
                ('paint_coating', 'Защитное покрытие')
            ]
            
            row = 0
            col = 0
            for key, label in violations:
                var = tk.BooleanVar(value=False)
                violation_vars[key] = var
                cb = ttk.Checkbutton(violations_frame, text=label, variable=var)
                cb.grid(row=row, column=col, sticky='w', padx=5, pady=2)
                col += 1
                if col > 2:  # 3 колонки
                    col = 0
                    row += 1
            
            # Сохраняем данные этой лестницы
            self.ladder_compliance_data[ladder_num] = {
                'compliance_var': compliance_var,
                'violations_frame': violations_frame,
                'violation_vars': violation_vars,
                'name': ladder_name
            }
            app_logger.info(f"Создан чекбокс соответствия для лестницы №{ladder_num}: {ladder_name}")
            
            # Восстанавливаем старые значения если были
            if ladder_num in old_compliance_data:
                old_data = old_compliance_data[ladder_num]
                compliance_var.set(old_data['compliant'])
                for key, value in old_data['violations'].items():
                    if key in violation_vars:
                        violation_vars[key].set(value)
                # Показываем/скрываем фрейм несоответствий
                if not old_data['compliant']:
                    violations_frame.pack(fill='x', padx=(20, 0), pady=5)
                app_logger.info(f"Восстановлены старые значения для лестницы №{ladder_num}")
        
        app_logger.info(f"ИТОГО создано чекбоксов: {len(self.ladder_compliance_data)}")
        app_logger.info(f"Номера лестниц: {list(self.ladder_compliance_data.keys())}")
    
    def _toggle_ladder_violations(self, ladder_num):
        """Показывает/скрывает несоответствия для конкретной лестницы"""
        if ladder_num not in self.ladder_compliance_data:
            return
        
        data = self.ladder_compliance_data[ladder_num]
        
        if not data['compliance_var'].get():
            # Не соответствует - показываем
            data['violations_frame'].pack(fill='x', padx=(20, 0), pady=5)
        else:
            # Соответствует - скрываем и сбрасываем
            data['violations_frame'].pack_forget()
            for var in data['violation_vars'].values():
                var.set(False)
    
    def _toggle_project_field(self):
        """Включает/выключает поле номера проекта"""
        if self.project_compliant_var.get():
            self.project_number_entry.config(state='normal')
        else:
            self.project_number_entry.config(state='disabled')
            self.project_number_entry.delete(0, tk.END)
    
    def _update_weather(self):
        """Получает текущую погоду и заполняет поля"""
        try:
            self.weather_status_label.config(text="⏳ Получение данных...")
            self.update()
            
            app_logger.info("Запрос текущей погоды для Екатеринбурга...")
            weather = self.weather_service.get_current_weather()
            
            if weather:
                # Заполняем поля
                self.temperature_entry.delete(0, tk.END)
                self.temperature_entry.insert(0, str(weather['temperature']))
                
                self.wind_speed_entry.delete(0, tk.END)
                self.wind_speed_entry.insert(0, str(weather['wind_speed']))
                
                self.weather_status_label.config(text=f"✅ Обновлено: {weather['temperature']}°C, {weather['wind_speed']} м/с")
                app_logger.info(f"Погода успешно обновлена: {weather['temperature']}°C, {weather['wind_speed']} м/с")
            else:
                self.weather_status_label.config(text="❌ Не удалось получить данные")
                messagebox.showerror(
                    "Ошибка",
                    "Не удалось получить данные о погоде.\n"
                    "Проверьте подключение к интернету."
                )
                app_logger.error("Не удалось получить погоду")
                
        except Exception as e:
            self.weather_status_label.config(text="❌ Ошибка")
            messagebox.showerror("Ошибка", f"Ошибка при получении погоды:\n{str(e)}")
            app_logger.error(f"Ошибка при получении погоды: {e}")
    
    def _update_beam_load(self, event=None):
        """Заглушка для совместимости - расчеты теперь происходят автоматически при генерации документа"""
        pass
    
    def _create_table_info_section(self):
        """Создает информационную секцию о таблице результатов испытаний"""
        frame = ttk.LabelFrame(self.scrollable_main, text="ℹ️ Результаты испытаний (автоматически)", padding=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        info_text = "Таблица формируется автоматически: ступени, ограждения, балки. Тип определяется по max высоте лестниц."
        
        info_label = ttk.Label(frame, text=info_text, justify='left', font=('Arial', 9))
        info_label.pack(padx=5, pady=2, anchor='w')
        return frame
    
    def _create_action_buttons(self):
        """Создает кнопки действий"""
        frame = ttk.Frame(self.scrollable_main, padding=10)
        frame.pack(fill='x', padx=10, pady=10)
        
        # Кнопка генерации
        self.generate_btn = ttk.Button(
            frame, 
            text="📄 Сгенерировать отчёт",
            command=self._generate_report
        )
        self.generate_btn.pack(side='left', padx=5, ipadx=10, ipady=5)
        
        # Кнопка открытия папки
        ttk.Button(
            frame,
            text="📁 Открыть папку с документами",
            command=self._open_reports_folder
        ).pack(side='left', padx=5, ipadx=10, ipady=5)
        
        # Кнопка предпросмотра
        ttk.Button(
            frame,
            text="👁 Предпросмотр",
            command=self._preview_report
        ).pack(side='left', padx=5, ipadx=10, ipady=5)
        
        # Кнопка очистки
        ttk.Button(
            frame,
            text="🗑 Очистить форму",
            command=self._clear_form
        ).pack(side='left', padx=5, ipadx=10, ipady=5)
    
    def _on_customer_selected(self, event=None):
        """Обработчик выбора заказчика - автозаполнение данных"""
        customer = self.customer_var.get()
        if customer:
            app_logger.info(f"Выбран заказчик: {customer}")
            
            # Ищем договор в базе
            contract = self.contracts_db.get_latest_contract_for_customer(customer)
            
            if contract:
                # Автозаполнение данных из договора
                object_full = contract.get('object_full_address')
                
                if object_full and object_full.strip():
                    # Очищаем и заполняем текстовое поле
                    self.object_full_address_text.delete('1.0', tk.END)
                    self.object_full_address_text.insert('1.0', object_full)
                    
                    self._update_status(f"Адрес/наименование загружено из: {contract.get('file_name', 'договора')}")
                    app_logger.info(f"Автозаполнение из {contract.get('file_name')}: {object_full[:50]}...")
                else:
                    self._update_status(f"Договор найден, но данные не извлечены из п.1.2")
                    app_logger.warning(f"Договор {contract.get('file_name')} не содержит данных в п.1.2")
            else:
                # Если нет в базе - пытаемся загрузить из старой системы
                self._load_contract_for_customer(customer)
    
    def _on_protocol_selector_change(self, event=None):
        """Переключение типа протокола"""
        label = self.protocol_selector_var.get()
        protocol = self.protocol_key_by_label.get(label, "vertical")
        self.protocol_type_var.set(protocol)
        self._update_protocol_sections_visibility()
        self._update_visual_inspection_label()
    
    def _auto_update_contracts_database(self):
        """Автоматически обновляет базу договоров при запуске (без диалоговых окон)"""
        try:
            # Проверяем существование папки
            if not config.EXTERNAL_CONTRACTS_DIR.exists():
                app_logger.warning(f"Папка с договорами не найдена: {config.EXTERNAL_CONTRACTS_DIR}")
                return
            
            app_logger.info("Автоматическое обновление базы договоров...")
            
            # Парсим договоры
            parser = ContractParser(config.EXTERNAL_CONTRACTS_DIR)
            contracts_data = parser.scan_contracts_directory()
            
            if not contracts_data:
                app_logger.warning(f"В папке {config.EXTERNAL_CONTRACTS_DIR} не найдено договоров")
                return
            
            # Обновляем базу
            self.contracts_db.update_contracts(contracts_data)
            
            # Обновляем список заказчиков в combobox
            self._update_customer_list()
            
            stats = self.contracts_db.get_stats()
            app_logger.info(f"База договоров автоматически обновлена: {stats['total_contracts']} договоров, {stats['unique_customers']} заказчиков")
            
            # Обновляем статус-бар
            self._update_status(f"База обновлена: {stats['total_contracts']} договоров")
            
        except Exception as e:
            app_logger.error(f"Ошибка автоматического обновления базы договоров: {e}")
            # Не показываем диалоговое окно, только логируем
    
    def _update_contracts_database(self):
        """Обновляет базу договоров из внешней папки (ручное обновление с диалогами)"""
        try:
            # Проверяем существование папки
            if not config.EXTERNAL_CONTRACTS_DIR.exists():
                messagebox.showerror(
                    "Ошибка", 
                    f"Папка с договорами не найдена:\n{config.EXTERNAL_CONTRACTS_DIR}\n\n"
                    f"Укажите правильный путь в файле config.py"
                )
                return
            
            # Показываем прогресс
            self._update_status("Сканирование папки с договорами...")
            self.update()
            
            # Парсим договоры
            parser = ContractParser(config.EXTERNAL_CONTRACTS_DIR)
            contracts_data = parser.scan_contracts_directory()
            
            if not contracts_data:
                messagebox.showwarning(
                    "Предупреждение",
                    f"В папке {config.EXTERNAL_CONTRACTS_DIR}\n"
                    f"не найдено договоров или не удалось извлечь данные."
                )
                self._update_status("Договоры не найдены")
                return
            
            # Обновляем базу
            self.contracts_db.update_contracts(contracts_data)
            
            # Обновляем список заказчиков в combobox
            self._update_customer_list()
            
            stats = self.contracts_db.get_stats()
            
            messagebox.showinfo(
                "Успех",
                f"База договоров обновлена!\n\n"
                f"Обработано договоров: {stats['total_contracts']}\n"
                f"Уникальных заказчиков: {stats['unique_customers']}"
            )
            
            self._update_status(f"База обновлена: {stats['total_contracts']} договоров")
            app_logger.info(f"База договоров обновлена: {stats}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить базу:\n{str(e)}")
            app_logger.error(f"Ошибка обновления базы договоров: {e}")
            self._update_status("Ошибка обновления базы")
    
    def _load_contract(self):
        """Загружает договор вручную"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл договора",
            initialdir=config.CONTRACTS_DIR,
            filetypes=[("Word документы", "*.docx"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            # Здесь можно реализовать извлечение данных из договора
            messagebox.showinfo("Информация", f"Загружен договор: {os.path.basename(file_path)}")
            app_logger.info(f"Загружен договор: {file_path}")
    
    def _load_contract_for_customer(self, customer):
        """Загружает данные из договора для выбранного заказчика (старая система)"""
        # Эта функция оставлена для совместимости, теперь использует новую систему
        pass
    
    def _collect_data(self):
        """Собирает данные из формы"""
        protocol_type = self.protocol_type_var.get()
        data = {
            'protocol_type': protocol_type,
            'date': self.date_entry.get(),
            'customer': self.customer_var.get(),
            'object_full_address': self.object_full_address_text.get('1.0', tk.END).strip(),
            'test_time': self.test_time_var.get(),
            'temperature': self.temperature_entry.get(),
            'wind_speed': self.wind_speed_entry.get(),
            'project_compliant': self.project_compliant_var.get(),
            'project_number': self.project_number_entry.get(),
        }

        if protocol_type == 'vertical':
            ladders = self.ladders_manager.get_all_ladders_data()
            data['ladders'] = ladders
            data['ladders_compliance'] = {
                ladder_num: {
                    'compliant': ldata['compliance_var'].get(),
                    'violations': {key: var.get() for key, var in ldata['violation_vars'].items()},
                    'name': ldata['name']
                }
                for ladder_num, ldata in self.ladder_compliance_data.items()
            }
        else:
            data['ladders'] = []
            data['ladders_compliance'] = {}

        if protocol_type == 'stair':
            for key, var in self.stair_fields.items():
                data[key] = var.get().strip()
            # Добавляем данные маршей и площадок
            if self.marches_manager:
                data['marches'] = self.marches_manager.get_all_marches_data()
            # Добавляем данные визуального осмотра для маршевых лестниц
            data['damage_found'] = self.damage_found_var.get()
            data['mount_violation_found'] = self.mount_violation_var.get()
            data['weld_violation_found'] = self.weld_violation_var.get()
            data['paint_compliant'] = self.paint_compliant_var.get()
        elif protocol_type == 'roof':
            for key, var in self.roof_fields.items():
                data[key] = var.get().strip()
            # Добавляем данные визуального осмотра для ограждений кровли
            data['damage_found'] = self.damage_found_var.get()
            data['mount_violation_found'] = self.mount_violation_var.get()
            data['weld_violation_found'] = self.weld_violation_var.get()
            data['paint_compliant'] = self.paint_compliant_var.get()
        
        # Логирование собранных данных по соответствию
        ladders_compl = data.get('ladders_compliance', {})
        app_logger.info(f"===== СБОР ДАННЫХ =====")
        app_logger.info(f"Тип протокола: {protocol_type}")
        if protocol_type == 'vertical':
            app_logger.info(f"Количество записей в ladder_compliance_data: {len(self.ladder_compliance_data)}")
            app_logger.info(f"Собранные данные соответствия: {ladders_compl}")
            for num, ldata in ladders_compl.items():
                app_logger.info(f"  Лестница №{num}: compliant={ldata.get('compliant')}, violations={ldata.get('violations')}")
        
        return data
    
    def _generate_report(self):
        """Генерирует отчёт"""
        try:
            # Автоматически обновляем список лестниц в соответствии нормам
            if self.protocol_type_var.get() == 'vertical':
                self._update_compliance_ladders()
            
            # Принудительно обновляем GUI
            self.update_idletasks()
            
            # Сбор данных
            data = self._collect_data()
            
            # Проверка что данные соответствия загружены
            if self.protocol_type_var.get() == 'vertical' and not data.get('ladders_compliance'):
                messagebox.showwarning("Предупреждение", 
                    "Данные соответствия лестниц не загружены.\n"
                    "Список обновлен автоматически. Проверьте настройки соответствия ГОСТ для каждой лестницы.")
            
            # Валидация
            is_valid, errors = self.validator.validate_all_data(data)
            app_logger.info(f"Результат валидации: is_valid={is_valid}, errors={errors}")
            
            if not is_valid:
                error_message = "Обнаружены ошибки:\n\n" + "\n".join(f"• {err}" for err in errors)
                app_logger.warning(f"Валидация не пройдена. Показываю окно с ошибками...")
                
                # Принудительно обновляем GUI перед показом messagebox
                self.update()
                self.lift()  # Поднимаем окно на передний план
                self.focus_force()  # Принудительно даем фокус
                
                messagebox.showerror("Ошибка валидации", error_message)
                app_logger.warning(f"Окно с ошибками показано")
                return
            
            # Генерация документа
            self._update_status("Генерация документа...")
            self.generate_btn.config(state='disabled')
            self.update()
            
            filepath = self.generator.create_document(data)
            
            # Сохранение в историю
            self.history_manager.add_entry(data)
            
            # Обновление списка заказчиков
            self._update_customer_list()
            
            self._update_status("Документ успешно создан")
            self.generate_btn.config(state='normal')
            
            # Предложение открыть файл
            result = messagebox.askyesno(
                "Успех", 
                f"Документ успешно создан:\n{os.path.basename(filepath)}\n\nОткрыть файл?"
            )
            
            if result:
                os.startfile(filepath)
            
        except Exception as e:
            self.generate_btn.config(state='normal')
            error_msg = f"Ошибка при генерации документа: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            app_logger.error(error_msg)
            self._update_status("Ошибка генерации")
    
    def _preview_report(self):
        """Предпросмотр отчёта"""
        try:
            # Автоматически обновляем список лестниц в соответствии нормам
            if self.protocol_type_var.get() == 'vertical':
                self._update_compliance_ladders()
            
            data = self._collect_data()
            
            # Валидация
            is_valid, errors = self.validator.validate_all_data(data)
            app_logger.info(f"Предпросмотр - результат валидации: is_valid={is_valid}, errors={errors}")
            
            if not is_valid:
                error_message = "Обнаружены ошибки:\n\n" + "\n".join(f"• {err}" for err in errors)
                app_logger.warning(f"Предпросмотр - валидация не пройдена. Показываю окно с ошибками...")
                
                # Принудительно обновляем GUI перед показом messagebox
                self.update()
                self.lift()
                self.focus_force()
                
                messagebox.showerror("Ошибка валидации", error_message)
                app_logger.warning(f"Окно с ошибками показано")
                return
            
            # Создание окна предпросмотра
            preview_window = tk.Toplevel(self)
            preview_window.title("Предпросмотр данных")
            preview_window.geometry("600x500")
            preview_window.configure(bg='#2b2b2b')
            
            # Текстовое поле с данными
            text = tk.Text(preview_window, wrap=tk.WORD, padx=10, pady=10,
                          bg='#3c3c3c', fg='#ffffff', insertbackground='#ffffff',
                          selectbackground='#404040', selectforeground='#ffffff')
            text.pack(fill='both', expand=True)
            
            protocol_type = data.get('protocol_type', 'vertical')
            protocol_label = self.protocol_label_by_key.get(protocol_type, protocol_type)

            preview_text = f"""
ПРЕДПРОСМОТР ОТЧЁТА

Дата: {data['date']}
Заказчик: {data['customer']}
Тип протокола: {protocol_label}
Адрес/наименование испытываемого объекта:
{data['object_full_address']}
"""

            if protocol_type == 'vertical':
                preview_text += "\nИСПЫТЫВАЕМЫЕ ЛЕСТНИЦЫ:\n"
                ladders = data.get('ladders', [])
                for ladder in ladders:
                    try:
                        height = float(str(ladder.get('height', '0')).replace(',', '.'))
                        ladder_type = 'П1-1' if height <= 6 else 'П1-2'
                    except (ValueError, TypeError):
                        ladder_type = '?'

                    preview_text += f"""
  Лестница №{ladder.get('number', '?')}:
    Название: {ladder.get('name', 'Не указано')}
    Тип: {ladder_type} (автоопределение по высоте)
    Высота: {ladder.get('height', '')} м
    Ширина: {ladder.get('width', '')} м
    Количество ступеней: {ladder.get('steps_count', '')}
    Количество точек крепления: {ladder.get('mount_points', '')}
    Размер площадки: {ladder.get('platform_length', '')} × {ladder.get('platform_width', '')} м
    Высота ограждений площадки: {ladder.get('fence_height', '')} м
    Расстояние от стены: {ladder.get('wall_distance', '')} м
    Расстояние от земли: {ladder.get('ground_distance', '')} м
    Расстояние между ступенями: {ladder.get('step_distance', '')} м
"""
            elif protocol_type == 'stair':
                ladder_name = data.get('ladder_name', '').strip()
                if not ladder_name:
                    ladder_name = "Лестница маршевая №1"
                
                preview_text += f"""

ПАРАМЕТРЫ МАРШЕВОЙ ЛЕСТНИЦЫ:
• Название лестницы: {ladder_name}
• Маршевая лестница, тип П2
"""
                # Добавляем информацию о маршах
                marches = data.get('marches', [])
                if marches:
                    for march in marches:
                        has_march = march.get('has_march', True)
                        has_platform = march.get('has_platform', True)
                        
                        element_parts = []
                        if has_march:
                            element_parts.append("Марш")
                        if has_platform:
                            element_parts.append("Площадка")
                        element_name = " и ".join(element_parts) if element_parts else "Элемент"
                        
                        preview_text += f"""
{element_name.upper()} №{march.get('number', '?')}:"""
                        
                        if has_march:
                            preview_text += f"""
• Ширина марша: {march.get('march_width', '')} м
• Длина марша: {march.get('march_length', '')} м
• Ширина ступени: {march.get('step_width', '')} м
• Расстояние между ступенями: {march.get('step_distance', '')} м
• Количество ступеней: {march.get('steps_count', '')}
• Высота ограждений марша: {march.get('march_fence_height', '')} м"""
                        
                        if has_platform:
                            preview_text += f"""
• Длина площадки: {march.get('platform_length', '')} м
• Ширина площадки: {march.get('platform_width', '')} м
• Высота ограждений площадки: {march.get('platform_fence_height', '')} м"""
                            
                            ground_dist = march.get('platform_ground_distance', '').strip()
                            if ground_dist:
                                preview_text += f"""
• Расстояние от площадки до земли: {ground_dist} м"""
                        
                        preview_text += "\n"
            elif protocol_type == 'roof':
                preview_text += f"""

ХАРАКТЕРИСТИКИ ОГРАЖДЕНИЯ КРОВЛИ:
• Длина участка: {data.get('length', '')} м
• Высота ограждения: {data.get('height', '')} м
• Количество точек крепления: {data.get('mount_points', '')}
• Шаг крепления: {data.get('mount_pitch', '')} м
• Высота ограждения от парапета: {data.get('parapet_height', '')} м
"""

            preview_text += f"""
УСЛОВИЯ ПРОВЕДЕНИЯ ИСПЫТАНИЙ:
• Время проведения: {data['test_time']}
• Температура воздуха: {data['temperature']} °C
• Скорость ветра: {data['wind_speed']} м/с
"""

            if protocol_type == 'vertical':
                preview_text += "\nВИЗУАЛЬНЫЙ ОСМОТР (по лестницам):\n"
                for ladder in data.get('ladders', []):
                    ladder_num = ladder.get('number', 1)
                    damage = 'обнаружено' if ladder.get('damage_found') else 'не обнаружено'
                    mount = 'обнаружено' if ladder.get('mount_violation_found') else 'не обнаружено'
                    weld = 'обнаружено' if ladder.get('weld_violation_found') else 'не обнаружено'
                    paint = 'соответствует' if ladder.get('paint_compliant') else 'не соответствует'
                    preview_text += f"• Лестница №{ladder_num}: внешние повреждения {damage}, нарушение крепления {mount}, нарушение швов {weld}, защитное покрытие {paint}\n"

                preview_text += "\nСООТВЕТСТВИЕ НОРМАМ (по лестницам):\n"
                ladders_compliance = data.get('ladders_compliance', {})
                violation_names = {
                    'ladder_width': 'ширина лестницы',
                    'step_distance': 'расстояние между ступенями',
                    'wall_distance': 'расстояние от стены',
                    'ground_distance': 'расстояние от земли',
                    'platform_length': 'длина площадки',
                    'platform_width': 'ширина площадки',
                    'fence_height': 'высота ограждения площадки',
                    'ladder_fence': 'ограждение лестницы',
                    'mount_distance': 'расстояние между упорами',
                    'paint_coating': 'защитное покрытие'
                }

                for ladder_num, compliance_data in sorted(ladders_compliance.items()):
                    compliant = compliance_data.get('compliant', True)
                    if compliant:
                        preview_text += f"• Лестница №{ladder_num}: Соответствует ГОСТ Р 54253-2009\n"
                    else:
                        violations = compliance_data.get('violations', {})
                        selected_violations = [violation_names[key] for key, value in violations.items() if value]
                        if selected_violations:
                            violations_text = ', '.join(selected_violations)
                            preview_text += f"• Лестница №{ladder_num}: НЕ соответствует ({violations_text})\n"
                        else:
                            preview_text += f"• Лестница №{ladder_num}: НЕ соответствует\n"

            preview_text += f"""
• Соответствует проекту: {'Да' if data['project_compliant'] else 'Нет'}{f" (проект {data['project_number']})" if data['project_compliant'] and data['project_number'] else ''}
"""

            if protocol_type == 'vertical':
                preview_text += """
РАСЧЕТ ВЕЛИЧИНЫ НАГРУЗКИ:
Согласно ГОСТ Р 53254-2009 «Техника пожарная. Лестницы пожарные наружные стационарные. 
Ограждения кровли. Общие технические требования. Методы испытаний».

ИСПЫТАНИЯМ ПОДЛЕЖАТ:
• Балки крепления лестниц к стене (попарно, в месте крепления к лестнице);
• Ступени лестницы (в середине ступени) – каждая 5-я ступень;
• Ограждения лестницы в точках на расстоянии не более 1,5 м друг от друга по всей высоте лестницы.

РЕЗУЛЬТАТЫ ИСПЫТАНИЙ:
Таблица формируется автоматически на основе типа лестницы и введенных данных.
"""
            elif protocol_type == 'stair':
                preview_text += """
РАСЧЕТ НАГРУЗОК:
Испытания маршевых лестниц выполняются согласно ГОСТ Р 53254-2009 и СП 1.13130.2009.
В нагрузочные точки входят ступени, площадки, ограждения и анкеры крепления.
"""
            else:  # roof
                preview_text += """
РАСЧЕТ НАГРУЗОК:
Испытания ограждений кровли выполняются по ГОСТ Р 53254-2009 с контролем верхних и средних горизонталей,
а также узлов крепления к парапету/кровле.
"""
            
            text.insert('1.0', preview_text)
            text.config(state='disabled')
            
            # Кнопка закрытия
            ttk.Button(
                preview_window, 
                text="Закрыть",
                command=preview_window.destroy
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка предпросмотра: {str(e)}")
    
    def _open_reports_folder(self):
        """Открывает папку с отчётами"""
        try:
            if sys.platform == 'win32':
                os.startfile(config.REPORTS_DIR)
            elif sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', config.REPORTS_DIR])
            else:  # linux
                subprocess.Popen(['xdg-open', config.REPORTS_DIR])
            
            app_logger.info("Открыта папка с отчётами")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {str(e)}")
    
    def _clear_form(self):
        """Очищает форму"""
        result = messagebox.askyesno("Подтверждение", "Очистить все поля?")
        if result:
            # Основная информация
            self.customer_var.set('')
            self.object_full_address_text.delete('1.0', tk.END)
            self.protocol_selector_var.set(self.protocol_label_by_key['vertical'])
            self._on_protocol_selector_change()
            
            # Лестницы (очищаем все кроме одной пустой)
            self.ladders_manager.clear_all()
            
            # Условия проведения испытаний
            self.test_time_var.set("дневное время")
            self.temperature_entry.delete(0, tk.END)
            self.wind_speed_entry.delete(0, tk.END)
            
            # Соответствие нормам
            for ladder_num, ldata in self.ladder_compliance_data.items():
                ldata['compliance_var'].set(True)
                ldata['violations_frame'].pack_forget()
                for var in ldata['violation_vars'].values():
                    var.set(False)
            self.project_compliant_var.set(False)
            self.project_number_entry.delete(0, tk.END)
            self.project_number_entry.config(state='disabled')

            # Поля маршевых лестниц
            for key, var in self.stair_fields.items():
                var.set('')
            # Очищаем марши
            if self.marches_manager:
                self.marches_manager.clear_all()

            # Поля ограждений кровли
            for key, var in self.roof_fields.items():
                var.set('')
            
            self._update_status("Форма очищена")
            app_logger.info("Форма очищена")
    
    def _update_status(self, message):
        """Обновляет статус-бар"""
        self.status_label.config(text=message)
        self.update()
    
    def _load_recent_data(self):
        """Загружает последние использованные данные"""
        self._update_customer_list()
    
    def _update_customer_list(self):
        """Обновляет список заказчиков"""
        # Получаем заказчиков из разных источников
        recent_customers = self.history_manager.get_recent_customers()
        db_customers = self.contracts_db.get_all_customers()
        
        # Объединяем все списки, убираем дубликаты и сортируем
        all_customers = list(set(config.DEFAULT_CUSTOMERS + recent_customers + db_customers))
        all_customers.sort()
        
        self.customer_combo['values'] = all_customers
        app_logger.info(f"Список заказчиков обновлён: {len(all_customers)} записей")


def run_application():
    """Запускает приложение"""
    # Создание необходимых директорий
    config.ensure_directories()
    
    # Запуск GUI
    app = MainApplication()
    app.mainloop()


if __name__ == '__main__':
    run_application()

