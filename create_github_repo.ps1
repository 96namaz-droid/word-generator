# Скрипт для автоматического создания репозитория на GitHub и загрузки кода
# Требуется: GitHub Personal Access Token

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName = "word-generator",
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$Token,
    
    [switch]$Private = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== Создание репозитория на GitHub ===" -ForegroundColor Green
Write-Host ""

# Проверяем, что мы в git репозитории
if (-not (Test-Path .git)) {
    Write-Host "[ОШИБКА] Это не git репозиторий!" -ForegroundColor Red
    exit 1
}

# Создаем репозиторий через GitHub API
Write-Host "[1/4] Создаем репозиторий на GitHub..." -ForegroundColor Cyan

$body = @{
    name = $RepoName
    description = "Генератор Word-отчётов для протоколов испытаний"
    private = $Private
    auto_init = $false
} | ConvertTo-Json

$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "PowerShell"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "[✓] Репозиторий создан: $($response.html_url)" -ForegroundColor Green
} catch {
    Write-Host "[ОШИБКА] Не удалось создать репозиторий" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Проверьте правильность токена доступа" -ForegroundColor Yellow
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "Репозиторий с таким именем уже существует" -ForegroundColor Yellow
    }
    exit 1
}

# Проверяем существующий remote
Write-Host ""
Write-Host "[2/4] Настраиваем remote..." -ForegroundColor Cyan

$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "[!] Remote уже настроен: $existingRemote" -ForegroundColor Yellow
    $overwrite = Read-Host "Перезаписать? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Отменено" -ForegroundColor Yellow
        exit 0
    }
    git remote remove origin
}

$repoUrl = "https://github.com/$GitHubUsername/$RepoName.git"
git remote add origin $repoUrl
Write-Host "[✓] Remote добавлен" -ForegroundColor Green

# Переименовываем ветку в main
Write-Host ""
Write-Host "[3/4] Переименовываем ветку в main..." -ForegroundColor Cyan
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    git branch -M main
    Write-Host "[✓] Ветка переименована в main" -ForegroundColor Green
} else {
    Write-Host "[✓] Ветка уже называется main" -ForegroundColor Green
}

# Загружаем код
Write-Host ""
Write-Host "[4/4] Загружаем код в GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== УСПЕХ! ===" -ForegroundColor Green
    Write-Host "Репозиторий создан и код загружен:" -ForegroundColor Green
    Write-Host $response.html_url -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[ОШИБКА] Не удалось загрузить код" -ForegroundColor Red
    exit 1
}

