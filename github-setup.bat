@echo off
REM Quick GitHub Setup Script for EcoSat Monitor (Windows)

echo.
echo ===================================================
echo   EcoSat Monitor - GitHub Deployment Setup
echo ===================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Git is not installed. Please install Git first.
    echo    Download from: https://git-scm.com/download/win
    exit /b 1
)

echo [OK] Git found

REM Check if already a git repository
if exist .git (
    echo [OK] Git repository already initialized
) else (
    echo [*] Initializing Git repository...
    git init
    echo [OK] Git initialized
)

REM Add all files
echo [*] Adding files to staging...
git add .
echo [OK] Files added

REM Create initial commit
echo [*] Creating initial commit...
git commit -m "Initial commit: EcoSat Monitor - Production Ready" 2>nul || (
    echo [!] No new changes to commit
)

REM Get GitHub username
set /p GITHUB_USERNAME="[INPUT] Enter your GitHub username: "
if "%GITHUB_USERNAME%"=="" (
    echo [X] GitHub username is required
    exit /b 1
)

REM Get repository name
set GITHUB_REPO=ecosat-monitor
set /p GITHUB_REPO_INPUT="[INPUT] Enter repository name (default: ecosat-monitor): "
if not "%GITHUB_REPO_INPUT%"=="" set GITHUB_REPO=%GITHUB_REPO_INPUT%

REM Set remote URL
set REMOTE_URL=https://github.com/%GITHUB_USERNAME%/%GITHUB_REPO%.git
echo.
echo [*] Setting remote URL: %REMOTE_URL%

REM Remove existing remote if it exists
git remote remove origin 2>nul

git remote add origin %REMOTE_URL%
echo [OK] Remote added

REM Create main branch if needed
for /f %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i
if not "%BRANCH%"=="main" (
    echo [*] Renaming branch to main...
    git branch -M main
    echo [OK] Branch renamed
)

REM Push to GitHub
echo.
echo [*] Pushing to GitHub...
echo.    Note: You may be prompted to authenticate with your GitHub token
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo [OK] SUCCESS! Repository pushed to GitHub
    echo ===================================================
    echo.
    echo Repository URL: https://github.com/%GITHUB_USERNAME%/%GITHUB_REPO%
    echo.
    echo Next Steps:
    echo   1. Go to: https://github.com/%GITHUB_USERNAME%/%GITHUB_REPO%/settings/pages
    echo   2. Enable GitHub Pages ^(deploy from gh-pages branch^)
    echo   3. Deploy backend to Render/Railway:
    echo      - https://render.com ^(recommended^)
    echo      - https://railway.app
    echo      - https://replit.com
    echo.
    echo Full guide: GITHUB-DEPLOYMENT.md
    echo.
) else (
    echo.
    echo [X] Push to GitHub failed
    echo    Check your internet connection and GitHub credentials
    echo.
)

pause
