@echo off
chcp 65001 >nul
title Создание репозитория на GitHub и загрузка кода
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════
echo   СОЗДАНИЕ РЕПОЗИТОРИЯ НА GITHUB И ЗАГРУЗКА КОДА
echo ═══════════════════════════════════════════════════════════════
echo.

REM Проверяем PowerShell
where powershell >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] PowerShell не найден
    pause
    exit /b 1
)

echo [✓] PowerShell найден
echo.

REM Получаем информацию от пользователя
set /p GITHUB_USERNAME="Введите ваш GitHub username: "
if "%GITHUB_USERNAME%"=="" (
    echo [ОШИБКА] Username не может быть пустым!
    pause
    exit /b 1
)

set /p REPO_NAME="Введите название репозитория (Enter для 'word-generator'): "
if "%REPO_NAME%"=="" set REPO_NAME=word-generator

echo.
echo ═══════════════════════════════════════════════════════════════
echo ВАЖНО: Для создания репозитория нужен GitHub Personal Access Token
echo ═══════════════════════════════════════════════════════════════
echo.
echo Как получить токен:
echo   1. Откройте https://github.com/settings/tokens
echo   2. Нажмите "Generate new token (classic)"
echo   3. Выберите срок действия (например, 90 дней)
echo   4. Отметьте права: "repo" (полный доступ к репозиториям)
echo   5. Нажмите "Generate token"
echo   6. Скопируйте токен (он показывается только один раз!)
echo.
set /p TOKEN="Введите ваш GitHub Personal Access Token: "
if "%TOKEN%"=="" (
    echo [ОШИБКА] Токен не может быть пустым!
    pause
    exit /b 1
)

set /p IS_PRIVATE="Создать приватный репозиторий? (y/n, по умолчанию n): "
if /i "%IS_PRIVATE%"=="y" (
    set PRIVATE_FLAG=-Private
) else (
    set PRIVATE_FLAG=
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo Информация:
echo   Username: %GITHUB_USERNAME%
echo   Репозиторий: %REPO_NAME%
echo   Приватный: %IS_PRIVATE%
echo ═══════════════════════════════════════════════════════════════
echo.

REM Запускаем PowerShell скрипт
powershell -ExecutionPolicy Bypass -File "create_github_repo.ps1" -RepoName "%REPO_NAME%" -GitHubUsername "%GITHUB_USERNAME%" -Token "%TOKEN%" %PRIVATE_FLAG%

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Произошла ошибка
    pause
    exit /b 1
)

echo.
pause

