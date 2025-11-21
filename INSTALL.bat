@echo off
chcp 65001 >nul
cls
echo ====================================================
echo    Установка зависимостей
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
python --version
echo.

echo Обновление pip...
python -m pip install --upgrade pip
echo.

echo ====================================================
echo Установка библиотек...
echo ====================================================
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось установить зависимости!
    echo Попробуйте запустить от имени администратора
    pause
    exit /b 1
)

echo.
echo ====================================================
echo [УСПЕХ] Все зависимости установлены!
echo ====================================================
echo.
echo Теперь можете запустить ЗАПУСК.bat
pause

