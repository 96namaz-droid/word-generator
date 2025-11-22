# Скрипт для настройки интерпретатора Python в PyCharm
Write-Host "Настройка интерпретатора Python..." -ForegroundColor Green

$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $projectPath "venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Путь к проекту: $projectPath" -ForegroundColor Yellow
Write-Host "Путь к интерпретатору: $pythonExe" -ForegroundColor Yellow

# Проверка существования интерпретатора
if (Test-Path $pythonExe) {
    Write-Host "✓ Интерпретатор найден" -ForegroundColor Green
    
    # Проверка версии Python
    $version = & $pythonExe --version
    Write-Host "Версия Python: $version" -ForegroundColor Cyan
    
    # Проверка установленных пакетов
    Write-Host "`nПроверка установленных пакетов..." -ForegroundColor Yellow
    & $pythonExe -m pip list | Select-String -Pattern "python-docx|tkcalendar|Pillow|requests|fastapi|uvicorn"
    
    Write-Host "`n✓ Интерпретатор готов к использованию" -ForegroundColor Green
    Write-Host "`nИнструкция для PyCharm:" -ForegroundColor Yellow
    Write-Host "1. File → Settings (Ctrl+Alt+S)" -ForegroundColor White
    Write-Host "2. Project: word_generator → Python Interpreter" -ForegroundColor White
    Write-Host "3. Выбери интерпретатор:" -ForegroundColor White
    Write-Host "   $pythonExe" -ForegroundColor Cyan
    Write-Host "`nИли используй автоматическую настройку (если доступна в PyCharm)" -ForegroundColor Yellow
    
} else {
    Write-Host "✗ Интерпретатор не найден по пути: $pythonExe" -ForegroundColor Red
    Write-Host "Создай venv заново или проверь путь" -ForegroundColor Yellow
}

Write-Host "`nНажми любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

