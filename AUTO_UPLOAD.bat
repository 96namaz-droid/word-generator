@echo off
chcp 65001 >nul
title Автоматическая загрузка в GitHub
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════
echo   АВТОМАТИЧЕСКАЯ ЗАГРУЗКА ПРОЕКТА В GITHUB
echo ═══════════════════════════════════════════════════════════════
echo.

REM Проверяем git
where git >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Git не установлен или не найден в PATH
    echo Установите Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Проверяем, что мы в git репозитории
if not exist .git (
    echo [ОШИБКА] Это не git репозиторий!
    pause
    exit /b 1
)

echo [✓] Git найден
echo [✓] Git репозиторий обнаружен
echo.

REM Проверяем коммиты
git log --oneline >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Нет коммитов для загрузки!
    pause
    exit /b 1
)

echo [✓] Коммиты найдены
echo.

REM Получаем информацию от пользователя
set /p GITHUB_USERNAME="Введите ваш GitHub username: "
if "%GITHUB_USERNAME%"=="" (
    echo [ОШИБКА] Username не может быть пустым!
    pause
    exit /b 1
)

set /p REPO_NAME="Введите название репозитория (или нажмите Enter для 'word-generator'): "
if "%REPO_NAME%"=="" set REPO_NAME=word-generator

echo.
echo ═══════════════════════════════════════════════════════════════
echo Информация:
echo   Username: %GITHUB_USERNAME%
echo   Репозиторий: %REPO_NAME%
echo ═══════════════════════════════════════════════════════════════
echo.

REM Проверяем существующий remote
git remote get-url origin >nul 2>&1
if not errorlevel 1 (
    echo [ВНИМАНИЕ] Remote уже настроен!
    git remote get-url origin
    echo.
    set /p OVERWRITE="Перезаписать? (y/n): "
    if /i not "%OVERWRITE%"=="y" (
        echo Отменено
        pause
        exit /b 0
    )
    git remote remove origin
    echo [✓] Старый remote удален
)

REM Добавляем remote
echo.
echo [1/3] Настраиваем remote...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
if errorlevel 1 (
    echo [ОШИБКА] Не удалось добавить remote
    pause
    exit /b 1
)
echo [✓] Remote добавлен

REM Переименовываем ветку в main
echo.
echo [2/3] Переименовываем ветку в main...
git branch --show-current | findstr /C:"main" >nul
if errorlevel 1 (
    git branch -M main
    echo [✓] Ветка переименована в main
) else (
    echo [✓] Ветка уже называется main
)

REM Загружаем
echo.
echo [3/3] Загружаем код в GitHub...
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo [ОШИБКА] Не удалось загрузить код
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Возможные причины:
    echo   1. Репозиторий еще не создан на GitHub
    echo   2. Неправильное имя пользователя или репозитория
    echo   3. Проблемы с аутентификацией
    echo.
    echo РЕШЕНИЕ:
    echo   1. Откройте https://github.com/new
    echo   2. Создайте репозиторий с названием: %REPO_NAME%
    echo   3. НЕ добавляйте README, .gitignore или лицензию
    echo   4. Запустите этот скрипт снова
    echo.
    echo Или выполните вручную:
    echo   git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
    echo   git branch -M main
    echo   git push -u origin main
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo [УСПЕХ] Проект успешно загружен в GitHub!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Репозиторий доступен по адресу:
    echo   https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
    echo.
)

pause

