@echo off
chcp 65001 >nul
title Быстрая загрузка в GitHub
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════
echo   БЫСТРАЯ ЗАГРУЗКА В GITHUB
echo ═══════════════════════════════════════════════════════════════
echo.

REM Настраиваем remote
git remote remove origin 2>nul
git remote add origin https://github.com/Hammer_1983/word-generator.git
git branch -M main 2>nul

echo [OK] Remote настроен
echo.

REM Пытаемся загрузить
echo Загружаем код...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo [ОШИБКА] Репозиторий не найден или нет доступа
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Создайте репозиторий на GitHub:
    echo   1. Откройте https://github.com/new
    echo   2. Название: word-generator
    echo   3. НЕ добавляйте README, .gitignore или лицензию
    echo   4. Нажмите "Create repository"
    echo   5. Запустите этот скрипт снова
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo [УСПЕХ] Код успешно загружен!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Репозиторий: https://github.com/Hammer_1983/word-generator
    echo.
    pause
)

