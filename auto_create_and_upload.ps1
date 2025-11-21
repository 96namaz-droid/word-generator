# Auto create repository and upload code
param(
    [string]$RepoName = "word-generator",
    [string]$GitHubUsername = "Hammer_1983",
    [string]$Token = "",
    [switch]$Private = $false
)

$ErrorActionPreference = "Continue"

Write-Host "`n=== Auto create GitHub repository ===" -ForegroundColor Green
Write-Host "Repository: $GitHubUsername/$RepoName`n" -ForegroundColor Cyan

# Setup remote
Write-Host "[1/4] Setting up git remote..." -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin "https://github.com/$GitHubUsername/$RepoName.git"
git branch -M main 2>$null
Write-Host "[OK] Remote configured`n" -ForegroundColor Green

# Try to create repo via API if token provided
if ($Token -and $Token.Length -gt 0) {
    Write-Host "[2/4] Creating repository via GitHub API..." -ForegroundColor Cyan
    
    $body = @{
        name = $RepoName
        description = "Word Generator for test protocols"
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
        
        Write-Host "[OK] Repository created: $($response.html_url)`n" -ForegroundColor Green
        $repoCreated = $true
    } catch {
        if ($_.Exception.Response.StatusCode -eq 422) {
            Write-Host "[!] Repository already exists or name taken" -ForegroundColor Yellow
            $repoCreated = $true
        } else {
            Write-Host "[!] Failed to create via API: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "Continuing with upload attempt..." -ForegroundColor Yellow
            $repoCreated = $false
        }
    }
} else {
    Write-Host "[2/4] No token provided, skipping API creation" -ForegroundColor Yellow
    Write-Host "Make sure repository is created manually on GitHub`n" -ForegroundColor Yellow
    $repoCreated = $false
}

# Wait a bit if repo was created
if ($repoCreated) {
    Write-Host "[3/4] Waiting for GitHub sync..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
} else {
    Write-Host "[3/4] Checking if repository exists..." -ForegroundColor Cyan
    $maxAttempts = 10
    $attempt = 0
    $repoExists = $false
    
    while ($attempt -lt $maxAttempts -and -not $repoExists) {
        $attempt++
        Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
        
        $testPush = git ls-remote "https://github.com/$GitHubUsername/$RepoName.git" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $repoExists = $true
            Write-Host "[OK] Repository found!`n" -ForegroundColor Green
            break
        }
        
        if ($attempt -lt $maxAttempts) {
            Write-Host "  Repository not created yet, waiting 5 seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
    
    if (-not $repoExists) {
        Write-Host "[!] Repository not found after $maxAttempts attempts" -ForegroundColor Red
        Write-Host "Create repository manually at https://github.com/new" -ForegroundColor Yellow
        Write-Host "Name: $RepoName" -ForegroundColor Yellow
        Write-Host "Then run this script again`n" -ForegroundColor Yellow
        exit 1
    }
}

# Upload code
Write-Host "[4/4] Uploading code to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== SUCCESS! ===" -ForegroundColor Green
    Write-Host "Repository created and code uploaded:" -ForegroundColor Green
    Write-Host "https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
} else {
    Write-Host "`n[ERROR] Failed to upload code" -ForegroundColor Red
    Write-Host "Check:" -ForegroundColor Yellow
    Write-Host "  1. Repository is created on GitHub" -ForegroundColor Yellow
    Write-Host "  2. You have write permissions" -ForegroundColor Yellow
    Write-Host "  3. Correct username and repository name" -ForegroundColor Yellow
    exit 1
}
