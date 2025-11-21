@echo off
chcp 65001 >nul
cls
echo ====================================================
echo    Синхронизация проекта через Git
echo ====================================================
echo.

cd /d "%~dp0"

echo [1/3] Загрузка последних изменений с сервера...
git pull origin main
if errorlevel 1 (
    echo [ОШИБКА] Не удалось загрузить изменения
    echo Проверь подключение к интернету и настройки remote
    pause
    exit /b 1
)
echo [OK] Изменения загружены
echo.

echo [2/3] Проверка локальных изменений...
git status --short
echo.

echo [3/3] Готово! Проект синхронизирован.
echo.
echo Если есть незакоммиченные изменения, выполни:
echo   git add .
echo   git commit -m "Описание изменений"
echo   git push origin main
echo.

pause

