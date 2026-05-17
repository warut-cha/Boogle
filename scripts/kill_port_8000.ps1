# PowerShell script to kill process on port 8000
Write-Host "Finding process on port 8000..." -ForegroundColor Yellow

$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($process) {
    Write-Host "Found process ID: $process" -ForegroundColor Green
    Write-Host "Killing process..." -ForegroundColor Yellow
    Stop-Process -Id $process -Force
    Write-Host "✓ Process killed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start the server with:" -ForegroundColor Cyan
    Write-Host "  python src/api_server.py" -ForegroundColor White
} else {
    Write-Host "No process found on port 8000" -ForegroundColor Red
}

# Made with Bob
