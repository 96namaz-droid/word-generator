@echo off
chcp 65001 >nul
title Загрузка по URL репозитория
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ЗАГРУЗКА ПО URL РЕПОЗИТОРИЯ
echo ═══════════════════════════════════════════════════════════════
echo.

echo Скопируйте URL вашего репозитория из браузера
echo Пример: https://github.com/username/repository-name.git
echo.

set /p REPO_URL="Введите полный URL репозитория: "
if "%REPO_URL%"=="" (
    echo [ОШИБКА] URL не может быть пустым!
    pause
    exit /b 1
)

echo.
echo Обновляю remote...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main 2>nul

echo.
echo Новый remote:
git remote -v
echo.

echo Загружаю код...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo [ОШИБКА] Не удалось загрузить код
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Возможные причины:
    echo   1. Репозиторий не существует
    echo   2. Неправильный URL
    echo   3. Нет прав на запись
    echo   4. Нужна аутентификация (GitHub может запросить логин/пароль)
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo [УСПЕХ] Код успешно загружен!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Репозиторий: %REPO_URL%
    echo.
    pause
)

