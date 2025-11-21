@echo off
chcp 65001 >nul
cls
cd /d "%~dp0"
echo ====================================================
echo    Запуск Генератора Word-отчётов
echo ====================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python: https://www.python.org/downloads/
    echo При установке отметьте "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python найден
echo.

if not exist "main.py" (
    echo [ОШИБКА] Файл main.py не найден!
    pause
    exit /b 1
)

echo Запуск программы...
echo Текущая папка: %CD%
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Программа завершилась с ошибкой!
    echo Проверьте файл logs\app.log
    pause
)

