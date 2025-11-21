# Скрипт для автоматической загрузки проекта в GitHub
# Использование: .\upload_to_github.ps1 -RepoName "название-репозитория" -GitHubUsername "ваш-username"

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername
)

Write-Host "=== Загрузка проекта в GitHub ===" -ForegroundColor Green

# Проверяем, что мы в git репозитории
if (-not (Test-Path .git)) {
    Write-Host "Ошибка: это не git репозиторий!" -ForegroundColor Red
    exit 1
}

# Проверяем наличие коммитов
$commits = git log --oneline 2>$null
if (-not $commits) {
    Write-Host "Ошибка: нет коммитов для загрузки!" -ForegroundColor Red
    exit 1
}

# Проверяем, не добавлен ли уже remote
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "Remote уже настроен: $remote" -ForegroundColor Yellow
    $response = Read-Host "Перезаписать? (y/n)"
    if ($response -ne "y") {
        Write-Host "Отменено" -ForegroundColor Yellow
        exit 0
    }
    git remote remove origin
}

# Добавляем remote
$repoUrl = "https://github.com/$GitHubUsername/$RepoName.git"
Write-Host "Добавляем remote: $repoUrl" -ForegroundColor Cyan
git remote add origin $repoUrl

# Переименовываем ветку в main (если нужно)
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "Переименовываем ветку $currentBranch в main" -ForegroundColor Cyan
    git branch -M main
}

# Загружаем в GitHub
Write-Host "Загружаем код в GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Успешно! ===" -ForegroundColor Green
    Write-Host "Репозиторий доступен по адресу: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Green
} else {
    Write-Host "`n=== Ошибка при загрузке ===" -ForegroundColor Red
    Write-Host "Возможные причины:" -ForegroundColor Yellow
    Write-Host "1. Репозиторий еще не создан на GitHub" -ForegroundColor Yellow
    Write-Host "2. Неправильное имя пользователя или репозитория" -ForegroundColor Yellow
    Write-Host "3. Проблемы с аутентификацией" -ForegroundColor Yellow
    Write-Host "`nСоздайте репозиторий на GitHub и повторите попытку" -ForegroundColor Yellow
}

