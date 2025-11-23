@echo off
chcp 65001 >nul
echo ========================================
echo Запуск веб-версии генератора протоколов
echo ========================================
echo.

REM Проверка виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo Ошибка: Виртуальное окружение не найдено!
    echo Создайте его командой: python -m venv venv
    pause
    exit /b 1
)

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Проверка установки зависимостей
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Установка зависимостей...
    pip install -r requirements.txt
)

REM Запуск веб-сервера
echo.
echo Веб-интерфейс доступен по адресу:
echo   http://localhost:8000
echo.
echo Для доступа с других устройств в локальной сети:
echo   http://<IP_адрес_компьютера>:8000
echo.
echo Для остановки нажмите Ctrl+C
echo ========================================
echo.

python start_web.py

pause

