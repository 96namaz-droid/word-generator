@echo off
chcp 65001 >nul
cls
echo ====================================================
echo    Настройка интерпретатора Python для PyCharm
echo ====================================================
echo.

cd /d "%~dp0"

set "PYTHON_PATH=venv\Scripts\python.exe"

if not exist "%PYTHON_PATH%" (
    echo [ОШИБКА] Интерпретатор не найден: %PYTHON_PATH%
    echo Проверь, что venv создан правильно
    pause
    exit /b 1
)

echo [OK] Интерпретатор найден: %CD%\%PYTHON_PATH%
echo.

echo Проверка версии Python:
"%PYTHON_PATH%" --version
echo.

echo Инструкция для PyCharm:
echo ====================================================
echo 1. File → Settings (Ctrl+Alt+S)
echo 2. Project: word_generator → Python Interpreter
echo 3. Нажми на шестеренку ^(Settings^) → Add...
echo 4. Выбери "Existing environment"
echo 5. Укажи путь к интерпретатору:
echo    %CD%\%PYTHON_PATH%
echo 6. Нажми OK → Apply → OK
echo ====================================================
echo.

echo После настройки:
echo - Кнопка запуска появится рядом с "if __name__ == '__main__':" в main.py
echo - Можно запускать через Ctrl+Shift+F10 или зелёную кнопку ▶️
echo.

pause

