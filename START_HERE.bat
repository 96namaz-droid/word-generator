@echo off
chcp 65001 >nul
title 🚀 Загрузка проекта в GitHub
color 0A
mode con: cols=80 lines=30

echo.
echo ═══════════════════════════════════════════════════════════════
echo          🚀 ЗАГРУЗКА ПРОЕКТА В GITHUB
echo ═══════════════════════════════════════════════════════════════
echo.
echo Выберите способ:
echo.
echo   [1] Автоматически (создать репозиторий + загрузить код)
echo       └─ Требуется GitHub Personal Access Token
echo.
echo   [2] Полуу automatically (только загрузить код)
echo       └─ Репозиторий нужно создать вручную на GitHub
echo.
echo   [3] Показать инструкцию по получению токена
echo.
echo   [0] Выход
echo.
set /p CHOICE="Ваш выбор (1/2/3/0): "

if "%CHOICE%"=="1" (
    call CREATE_AND_UPLOAD.bat
    goto :end
)

if "%CHOICE%"=="2" (
    call AUTO_UPLOAD.bat
    goto :end
)

if "%CHOICE%"=="3" (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   КАК ПОЛУЧИТЬ GITHUB PERSONAL ACCESS TOKEN
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 1. Откройте в браузере:
    echo    https://github.com/settings/tokens
    echo.
    echo 2. Нажмите "Generate new token (classic)"
    echo.
    echo 3. Введите название: Word Generator Upload
    echo.
    echo 4. Выберите срок: 90 дней (или любой другой)
    echo.
    echo 5. Отметьте права: repo (полный доступ к репозиториям)
    echo.
    echo 6. Нажмите "Generate token"
    echo.
    echo 7. СКОПИРУЙТЕ ТОКЕН СРАЗУ! Он показывается только один раз.
    echo.
    echo Открываю страницу в браузере...
    start https://github.com/settings/tokens
    echo.
    pause
    goto :start
)

if "%CHOICE%"=="0" (
    exit /b 0
)

echo.
echo Неверный выбор!
pause
goto :start

:start
cls
goto :eof

:end
echo.
echo Готово!
pause

