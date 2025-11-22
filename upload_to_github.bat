@echo off
chcp 65001 >nul
echo === Загрузка проекта в GitHub ===
echo.

set /p REPO_NAME="Введите название репозитория на GitHub: "
set /p GITHUB_USERNAME="Введите ваш GitHub username: "

echo.
echo Проверяем git репозиторий...
if not exist .git (
    echo Ошибка: это не git репозиторий!
    pause
    exit /b 1
)

echo Проверяем коммиты...
git log --oneline >nul 2>&1
if errorlevel 1 (
    echo Ошибка: нет коммитов для загрузки!
    pause
    exit /b 1
)

echo Проверяем remote...
git remote get-url origin >nul 2>&1
if not errorlevel 1 (
    echo Remote уже настроен!
    set /p OVERWRITE="Перезаписать? (y/n): "
    if /i not "%OVERWRITE%"=="y" (
        echo Отменено
        pause
        exit /b 0
    )
    git remote remove origin
)

echo Добавляем remote...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo Переименовываем ветку в main (если нужно)...
git branch --show-current | findstr /C:"main" >nul
if errorlevel 1 (
    git branch -M main
)

echo Загружаем код в GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo === Ошибка при загрузке ===
    echo Возможные причины:
    echo 1. Репозиторий еще не создан на GitHub
    echo 2. Неправильное имя пользователя или репозитория
    echo 3. Проблемы с аутентификацией
    echo.
    echo Создайте репозиторий на GitHub и повторите попытку
) else (
    echo.
    echo === Успешно! ===
    echo Репозиторий доступен по адресу: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
)

echo.
pause

