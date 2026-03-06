# GitHub Push Script for PackOptima
# This script helps you push your code to GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PackOptima - Push to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your repository: https://github.com/Yeswanth0007-12/BUSINESS-IDEA.git" -ForegroundColor Yellow
Write-Host ""

Write-Host "OPTION 1: Use GitHub Desktop (EASIEST)" -ForegroundColor Green
Write-Host "----------------------------------------"
Write-Host "1. Download GitHub Desktop: https://desktop.github.com"
Write-Host "2. Install and sign in with your GitHub account"
Write-Host "3. Click 'Add' > 'Add Existing Repository'"
Write-Host "4. Browse to: $PWD"
Write-Host "5. Click 'Publish repository' or 'Push origin'"
Write-Host ""

Write-Host "OPTION 2: Use Personal Access Token" -ForegroundColor Green
Write-Host "----------------------------------------"
Write-Host "1. Go to: https://github.com/settings/tokens"
Write-Host "2. Click 'Generate new token' > 'Generate new token (classic)'"
Write-Host "3. Give it a name like 'PackOptima Push'"
Write-Host "4. Select scope: 'repo' (full control of private repositories)"
Write-Host "5. Click 'Generate token' and COPY the token"
Write-Host ""

$choice = Read-Host "Do you have a Personal Access Token ready? (yes/no)"

if ($choice -eq "yes" -or $choice -eq "y") {
    Write-Host ""
    Write-Host "Great! Now run this command:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "When prompted for password, paste your Personal Access Token" -ForegroundColor Yellow
    Write-Host "(Note: You won't see the token as you paste it - this is normal)" -ForegroundColor Gray
    Write-Host ""
    
    $pushNow = Read-Host "Push now? (yes/no)"
    if ($pushNow -eq "yes" -or $pushNow -eq "y") {
        git push -u origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "SUCCESS! Your code is now on GitHub!" -ForegroundColor Green
            Write-Host "View it at: https://github.com/Yeswanth0007-12/BUSINESS-IDEA" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "Push failed. Please check your token and try again." -ForegroundColor Red
        }
    }
} else {
    Write-Host ""
    Write-Host "No problem! Follow these steps:" -ForegroundColor Yellow
    Write-Host "1. Get your token from: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "2. Run this script again, or" -ForegroundColor White
    Write-Host "3. Use GitHub Desktop (easier option)" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
