@echo off
chcp 65001 >nul
title Исправление и загрузка в GitHub
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ИСПРАВЛЕНИЕ И ЗАГРУЗКА В GITHUB
echo ═══════════════════════════════════════════════════════════════
echo.

echo Текущий remote:
git remote -v
echo.

set /p GITHUB_USERNAME="Введите ваш GitHub username: "
if "%GITHUB_USERNAME%"=="" (
    echo [ОШИБКА] Username не может быть пустым!
    pause
    exit /b 1
)

set /p REPO_NAME="Введите название репозитория: "
if "%REPO_NAME%"=="" (
    echo [ОШИБКА] Название не может быть пустым!
    pause
    exit /b 1
)

echo.
echo Обновляю remote...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
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
    echo   2. Неправильное название или username
    echo   3. Нет прав на запись
    echo   4. Нужна аутентификация
    echo.
    echo Проверьте URL репозитория:
    echo   https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo [УСПЕХ] Код успешно загружен!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Репозиторий: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
    start https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    pause
)

