@echo off
chcp 65001 >nul
cls
echo ====================================================
echo    Отправка изменений на сервер
echo ====================================================
echo.

cd /d "%~dp0"

echo [1/4] Проверка изменений...
git status
echo.

set /p commit_msg="Введите описание изменений: "
if "%commit_msg%"=="" (
    set commit_msg=Обновление проекта
)

echo.
echo [2/4] Добавление файлов...
git add .
if errorlevel 1 (
    echo [ОШИБКА] Не удалось добавить файлы
    pause
    exit /b 1
)

echo [3/4] Создание коммита...
git commit -m "%commit_msg%"
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Нет изменений для коммита или ошибка
    pause
    exit /b 1
)

echo [4/4] Отправка на сервер...
git push origin main
if errorlevel 1 (
    echo [ОШИБКА] Не удалось отправить изменения
    echo Попробуй выполнить: git pull origin main
    pause
    exit /b 1
)

echo.
echo [OK] Изменения успешно отправлены!
echo.

pause

