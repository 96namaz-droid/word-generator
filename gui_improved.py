"""
Улучшенный графический интерфейс для десктопа
Версия с вкладками, горячими клавишами и улучшенной навигацией
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
from weather_service import WeatherService
from logger import app_logger
import config


class ImprovedMainApplication(tk.Tk):
    """Улучшенное главное окно с вкладками"""
    
    def __init__(self):
        super().__init__()
        
        self.title(config.WINDOW_TITLE + " (Улучшенная версия)")
        self.geometry("1400x900")  # Больше пространства
        
        # Центрирование окна
        self._center_window()
        
        # Инициализация компонентов
        self.generator = DocumentGenerator()
        self.history_manager = HistoryManager()
        self.validator = DataValidator()
        self.contracts_db = ContractsDatabase()
        self.weather_service = WeatherService()
        
        # Горячие клавиши
        self._setup_hotkeys()
        
        # Настройка UI
        self._setup_ui()
        
        # Загрузка данных
        self._load_recent_data()
        self._auto_update_contracts_database()
        
        app_logger.info("Улучшенное приложение запущено")
    
    def _center_window(self):
        """Центрирует окно на экране"""
        self.update_idletasks()
        width = 1400
        height = 900
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_hotkeys(self):
        """Настройка горячих клавиш"""
        self.bind('<Control-g>', lambda e: self._generate_report())  # Ctrl+G - генерация
        self.bind('<Control-w>', lambda e: self._update_weather())   # Ctrl+W - погода
        self.bind('<Control-n>', lambda e: self._clear_form())       # Ctrl+N - новая форма
        self.bind('<Control-s>', lambda e: self._generate_report())  # Ctrl+S - сохранить (генерация)
        self.bind('<F5>', lambda e: self._update_weather())          # F5 - обновить погоду
        self.bind('<F1>', lambda e: self._show_help())               # F1 - справка
    
    def _setup_ui(self):
        """Настройка улучшенного интерфейса"""
        # Применяем улучшенную тему
        self._apply_improved_theme()
        
        # Создаем меню
        self._create_menu_bar()
        
        # Создаем панель инструментов
        self._create_toolbar()
        
        # Создаем главный контейнер с вкладками
        self._create_tabbed_interface()
        
        # Статус-бар внизу
        self._create_status_bar()
    
    def _apply_improved_theme(self):
        """Применяет улучшенную светлую тему"""
        self.configure(bg='#f5f5f5')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема
        bg_color = '#ffffff'
        fg_color = '#2c3e50'
        accent_color = '#3498db'
        success_color = '#27ae60'
        
        # Общие настройки
        style.configure('.', background='#f5f5f5', foreground=fg_color, font=('Segoe UI', 9))
        
        # Вкладки
        style.configure('TNotebook', background='#f5f5f5', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#e0e0e0',
                       foreground=fg_color,
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', bg_color)],
                 foreground=[('selected', accent_color)])
        
        # Фреймы
        style.configure('TFrame', background=bg_color)
        style.configure('Card.TFrame', background=bg_color, relief='solid', borderwidth=1)
        
        # LabelFrame
        style.configure('TLabelframe', background=bg_color, borderwidth=2, relief='groove')
        style.configure('TLabelframe.Label', 
                       background=bg_color,
                       foreground=accent_color,
                       font=('Segoe UI', 10, 'bold'))
        
        # Кнопки
        style.configure('TButton',
                       background=accent_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9, 'bold'),
                       padding=[15, 8])
        style.map('TButton',
                 background=[('active', '#2980b9'), ('pressed', '#21618c')])
        
        # Специальные кнопки
        style.configure('Success.TButton', background=success_color)
        style.map('Success.TButton',
                 background=[('active', '#229954'), ('pressed', '#1e8449')])
        
        style.configure('Danger.TButton', background='#e74c3c')
        style.map('Danger.TButton',
                 background=[('active', '#c0392b'), ('pressed', '#a93226')])
        
        # Labels
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 14, 'bold'),
                       foreground=accent_color,
                       background=bg_color)
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 10),
                       foreground='#7f8c8d',
                       background=bg_color)
    
    def _create_menu_bar(self):
        """Создает строку меню"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый отчёт", command=self._clear_form, accelerator="Ctrl+N")
        file_menu.add_command(label="Сгенерировать", command=self._generate_report, accelerator="Ctrl+G")
        file_menu.add_separator()
        file_menu.add_command(label="Открыть папку с отчётами", command=self._open_reports_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        
        # Меню Данные
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Данные", menu=data_menu)
        data_menu.add_command(label="Обновить погоду", command=self._update_weather, accelerator="Ctrl+W")
        data_menu.add_command(label="Обновить базу договоров", command=self._update_contracts_database)
        
        # Меню Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Предпросмотр", command=self._preview_report)
        
        # Меню Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Горячие клавиши", command=self._show_help, accelerator="F1")
        help_menu.add_command(label="О программе", command=self._show_about)
    
    def _create_toolbar(self):
        """Создает панель инструментов"""
        toolbar = ttk.Frame(self, relief='raised', borderwidth=1)
        toolbar.pack(side='top', fill='x', padx=5, pady=5)
        
        # Кнопки быстрого доступа
        ttk.Button(toolbar, text="📄 Генерировать (Ctrl+G)", 
                  style='Success.TButton',
                  command=self._generate_report).pack(side='left', padx=2)
        
        ttk.Button(toolbar, text="🌤 Погода (Ctrl+W)",
                  command=self._update_weather).pack(side='left', padx=2)
        
        ttk.Button(toolbar, text="👁 Предпросмотр",
                  command=self._preview_report).pack(side='left', padx=2)
        
        ttk.Button(toolbar, text="📁 Папка отчётов",
                  command=self._open_reports_folder).pack(side='left', padx=2)
        
        ttk.Button(toolbar, text="🗑 Очистить (Ctrl+N)",
                  style='Danger.TButton',
                  command=self._clear_form).pack(side='left', padx=2)
        
        # Справа - счётчик лестниц
        self.ladders_count_label = ttk.Label(toolbar, text="Лестниц: 0", 
                                             font=('Segoe UI', 9, 'bold'))
        self.ladders_count_label.pack(side='right', padx=10)
    
    def _create_tabbed_interface(self):
        """Создает интерфейс с вкладками"""
        # Создаём Notebook (вкладки)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Вкладка 1: Основная информация
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="  📋 Основная информация  ")
        self._create_main_info_tab()
        
        # Вкладка 2: Лестницы
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="  🪜 Испытываемые лестницы  ")
        self._create_ladders_tab()
        
        # Вкладка 3: Условия и соответствие
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="  ⚙️ Условия и соответствие  ")
        self._create_conditions_tab()
    
    def _create_main_info_tab(self):
        """Вкладка основной информации"""
        # Контейнер с прокруткой
        canvas = tk.Canvas(self.tab1, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab1, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, text="Протокол испытания вертикальных пожарных лестниц",
                 style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Заполните основную информацию о заказчике и объекте",
                 style='Subtitle.TLabel').pack()
        
        # Основная информация
        info_frame = ttk.LabelFrame(scrollable_frame, text="Основная информация", padding=20)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        # Дата
        ttk.Label(info_frame, text="Дата проведения испытаний:").grid(row=0, column=0, sticky='w', pady=8, padx=(0, 10))
        self.date_entry = DateEntry(info_frame, width=20, date_pattern='dd.mm.yyyy', locale='ru_RU',
                                    font=('Segoe UI', 10))
        self.date_entry.grid(row=0, column=1, sticky='ew', pady=8)
        
        # Заказчик
        ttk.Label(info_frame, text="Заказчик:").grid(row=1, column=0, sticky='w', pady=8, padx=(0, 10))
        
        customer_frame = ttk.Frame(info_frame)
        customer_frame.grid(row=1, column=1, sticky='ew', pady=8)
        
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, 
                                          font=('Segoe UI', 10), width=50)
        self.customer_combo.pack(side='left', fill='x', expand=True)
        self.customer_combo['values'] = config.DEFAULT_CUSTOMERS
        self.customer_combo.bind('<<ComboboxSelected>>', self._on_customer_selected)
        
        ttk.Button(customer_frame, text="📂", width=3,
                  command=self._load_contract).pack(side='left', padx=2)
        ttk.Button(customer_frame, text="🔄", width=3,
                  command=self._update_contracts_database).pack(side='left', padx=2)
        
        # Адрес/наименование объекта
        ttk.Label(info_frame, text="Адрес/наименование\nиспытываемого объекта:").grid(row=2, column=0, sticky='nw', pady=8, padx=(0, 10))
        
        object_frame = ttk.Frame(info_frame)
        object_frame.grid(row=2, column=1, sticky='ew', pady=8)
        
        self.object_full_address_text = tk.Text(object_frame, height=4, width=50, wrap=tk.WORD,
                                                font=('Segoe UI', 9),
                                                bg='white', fg='#2c3e50',
                                                insertbackground='#2c3e50',
                                                relief='solid', borderwidth=1)
        self.object_full_address_text.pack(side='left', fill='both', expand=True)
        
        scrollbar_obj = ttk.Scrollbar(object_frame, command=self.object_full_address_text.yview)
        scrollbar_obj.pack(side='right', fill='y')
        self.object_full_address_text.config(yscrollcommand=scrollbar_obj.set)
        
        info_frame.columnconfigure(1, weight=1)
    
    def _create_ladders_tab(self):
        """Вкладка с лестницами"""
        # Заголовок
        header_frame = ttk.Frame(self.tab2)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, text="Испытываемые лестницы",
                 style='Title.TLabel').pack(side='left')
        
        ttk.Button(header_frame, text="➕ Добавить лестницу",
                  style='Success.TButton',
                  command=self._add_ladder_and_update).pack(side='right')
        
        # Контейнер для лестниц
        self.ladders_manager = LaddersManager(self.tab2)
        self.ladders_manager.pack(fill='both', expand=True, padx=20)
    
    def _create_conditions_tab(self):
        """Вкладка условий и соответствия"""
        # Контейнер с прокруткой
        canvas = tk.Canvas(self.tab3, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab3, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Условия проведения испытаний
        conditions_frame = ttk.LabelFrame(scrollable_frame, text="Условия проведения испытаний", padding=20)
        conditions_frame.pack(fill='x', padx=20, pady=10)
        
        # Время
        ttk.Label(conditions_frame, text="Время проведения:").grid(row=0, column=0, sticky='w', pady=5)
        self.test_time_var = tk.StringVar(value="дневное время")
        test_time_combo = ttk.Combobox(conditions_frame, textvariable=self.test_time_var, 
                                      width=30, state='readonly', font=('Segoe UI', 10))
        test_time_combo['values'] = ("дневное время", "ночное время")
        test_time_combo.grid(row=0, column=1, sticky='w', pady=5, padx=5)
        
        # Температура и ветер
        ttk.Label(conditions_frame, text="Температура воздуха (°C):").grid(row=1, column=0, sticky='w', pady=5)
        self.temperature_entry = ttk.Entry(conditions_frame, width=20, font=('Segoe UI', 10))
        self.temperature_entry.grid(row=1, column=1, sticky='w', pady=5, padx=5)
        
        ttk.Label(conditions_frame, text="Скорость ветра (м/с):").grid(row=2, column=0, sticky='w', pady=5)
        self.wind_speed_entry = ttk.Entry(conditions_frame, width=20, font=('Segoe UI', 10))
        self.wind_speed_entry.grid(row=2, column=1, sticky='w', pady=5, padx=5)
        
        # Кнопка погоды
        weather_btn = ttk.Button(conditions_frame, text="🌤 Получить текущую погоду (Екатеринбург)",
                                command=self._update_weather)
        weather_btn.grid(row=3, column=0, columnspan=2, sticky='w', pady=10)
        
        self.weather_status_label = ttk.Label(conditions_frame, text="", foreground='#7f8c8d')
        self.weather_status_label.grid(row=3, column=2, sticky='w', padx=10)
        
        # Соответствие нормам
        self._create_compliance_section(scrollable_frame)
    
    def _create_compliance_section(self, parent):
        """Создает секцию соответствия нормам"""
        self.compliance_frame = ttk.LabelFrame(parent, text="Соответствие нормам", padding=20)
        self.compliance_frame.pack(fill='x', padx=20, pady=10)
        
        # Инициализация
        self.ladder_compliance_data = {}
        
        # Контейнер для динамического содержимого
        self.compliance_content_frame = ttk.Frame(self.compliance_frame)
        self.compliance_content_frame.pack(fill='both', expand=True)
        
        # Информация
        info_label = ttk.Label(self.compliance_frame, 
                              text="ℹ️ Список обновляется автоматически при генерации отчёта",
                              foreground='#7f8c8d', font=('Segoe UI', 8))
        info_label.pack(pady=5)
        
        ttk.Button(self.compliance_frame, text="🔄 Обновить список лестниц вручную",
                  command=self._update_compliance_ladders).pack(pady=5)
        
        # Соответствие проекту
        project_frame = ttk.Frame(self.compliance_frame)
        project_frame.pack(fill='x', pady=10)
        
        self.project_compliant_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(project_frame, text="Соответствует проекту",
                       variable=self.project_compliant_var,
                       command=self._toggle_project_field).pack(side='left', padx=5)
        
        # Номер проекта
        project_entry_frame = ttk.Frame(self.compliance_frame)
        project_entry_frame.pack(fill='x', pady=5)
        
        ttk.Label(project_entry_frame, text="Номер проекта:").pack(side='left', padx=(0, 5))
        self.project_number_entry = ttk.Entry(project_entry_frame, width=40, font=('Segoe UI', 10))
        self.project_number_entry.pack(side='left', padx=5)
        self.project_number_entry.config(state='disabled')
        
        self.project_number_group = project_entry_frame
        self.project_number_group.pack_forget()  # Изначально скрыт
    
    def _create_status_bar(self):
        """Создает статус-бар"""
        status_frame = ttk.Frame(self, relief='sunken', borderwidth=1)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_label = ttk.Label(status_frame, text="Готов к работе", 
                                      font=('Segoe UI', 9), foreground='#27ae60')
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Версия справа
        version_label = ttk.Label(status_frame, text="v2.0 Улучшенная версия",
                                 font=('Segoe UI', 8), foreground='#95a5a6')
        version_label.pack(side='right', padx=10)
    
    def _add_ladder_and_update(self):
        """Добавляет лестницу и обновляет счётчик"""
        self.ladders_manager.add_ladder()
        self._update_ladder_count()
    
    def _update_ladder_count(self):
        """Обновляет счётчик лестниц"""
        count = len(self.ladders_manager.ladders)
        self.ladders_count_label.config(text=f"Лестниц: {count}")
    
    def _show_help(self):
        """Показывает справку по горячим клавишам"""
        help_text = """
Горячие клавиши:

Ctrl+G  - Сгенерировать отчёт
Ctrl+S  - Сгенерировать отчёт (сохранить)
Ctrl+W  - Обновить погоду
Ctrl+N  - Очистить форму (новый отчёт)
F5      - Обновить погоду
F1      - Эта справка

Навигация:
Tab     - Переход к следующему полю
Shift+Tab - Переход к предыдущему полю

Советы:
• Используйте вкладки для удобной навигации
• Панель инструментов содержит быстрые действия
• Статус-бар показывает текущее состояние
        """
        messagebox.showinfo("Горячие клавиши", help_text)
    
    def _show_about(self):
        """Показывает информацию о программе"""
        about_text = """
Генератор отчётов о пожарных лестницах
Улучшенная версия 2.0

Особенности:
✅ Интерфейс с вкладками
✅ Горячие клавиши
✅ Панель инструментов
✅ Автоматическое получение погоды
✅ База договоров с автозаполнением
✅ Валидация обязательных полей
✅ Адаптивный интерфейс

© 2024
        """
        messagebox.showinfo("О программе", about_text)
    
    # Остальные методы импортируются из оригинального gui.py
    # (для краткости не дублирую все методы - они такие же)
    
    def _toggle_project_field(self):
        """Показывает/скрывает поле номера проекта"""
        if self.project_compliant_var.get():
            self.project_number_group.pack(fill='x', pady=5)
            self.project_number_entry.config(state='normal')
        else:
            self.project_number_group.pack_forget()
            self.project_number_entry.config(state='disabled')
            self.project_number_entry.delete(0, tk.END)
    
    def _update_status(self, message, color='#27ae60'):
        """Обновляет статус-бар"""
        self.status_label.config(text=message, foreground=color)
        self.update()


# Импортируем методы из оригинального GUI для повторного использования
from gui import MainApplication

# Наследуем методы, которые не были переопределены
ImprovedMainApplication._on_customer_selected = MainApplication._on_customer_selected
ImprovedMainApplication._update_contracts_database = MainApplication._update_contracts_database
ImprovedMainApplication._auto_update_contracts_database = MainApplication._auto_update_contracts_database
ImprovedMainApplication._load_contract = MainApplication._load_contract
ImprovedMainApplication._load_contract_for_customer = MainApplication._load_contract_for_customer
ImprovedMainApplication._collect_data = MainApplication._collect_data
ImprovedMainApplication._generate_report = MainApplication._generate_report
ImprovedMainApplication._preview_report = MainApplication._preview_report
ImprovedMainApplication._open_reports_folder = MainApplication._open_reports_folder
ImprovedMainApplication._clear_form = MainApplication._clear_form
ImprovedMainApplication._update_customer_list = MainApplication._update_customer_list
ImprovedMainApplication._load_recent_data = MainApplication._load_recent_data
ImprovedMainApplication._update_compliance_ladders = MainApplication._update_compliance_ladders
ImprovedMainApplication._toggle_ladder_violations = MainApplication._toggle_ladder_violations
ImprovedMainApplication._update_weather = MainApplication._update_weather


def run_improved_application():
    """Запускает улучшенное приложение"""
    config.ensure_directories()
    app = ImprovedMainApplication()
    app.mainloop()


if __name__ == '__main__':
    run_improved_application()
