# master-start.ps1
# This script starts all backend services in separate windows

$RootPath = Get-Location

# 1. Start Local Gateway
Write-Host "Starting Local Gateway..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath\backend'; python local_gateway.py" -WindowStyle Normal

# 2. Start Atomic Services
$AtomicServices = @(
    @{ Name = "Student"; Dir = "backend\atomic\student"; Port = 5001 },
    @{ Name = "Tutor"; Dir = "backend\atomic\tutor"; Port = 5002 },
    @{ Name = "Session"; Dir = "backend\atomic\session"; Port = 5003 },
    @{ Name = "Meeting"; Dir = "backend\atomic\meeting"; Port = 5004 },
    @{ Name = "Calendar"; Dir = "backend\atomic\calendar"; Port = 5005 },
    @{ Name = "Email"; Dir = "backend\atomic\email"; Port = 5006 },
    @{ Name = "Payment"; Dir = "backend\atomic\payment"; Port = 5007 }
)

foreach ($Service in $AtomicServices) {
    Write-Host "Starting $($Service.Name) Service on port $($Service.Port)..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath\$($Service.Dir)'; python app.py" -WindowStyle Normal
}

# 3. Start Composite Services
$CompositeServices = @(
    @{ Name = "Book Session"; Dir = "backend\composite\book_session"; Port = 5100 },
    @{ Name = "Cancel Session"; Dir = "backend\composite\cancel_session"; Port = 5101 },
    @{ Name = "Rate Tutor"; Dir = "backend\composite\rate_tutor"; Port = 5102 },
    @{ Name = "Get Sessions"; Dir = "backend\composite\get_sessions"; Port = 5103 }
)

foreach ($Service in $CompositeServices) {
    Write-Host "Starting $($Service.Name) Composite Service on port $($Service.Port)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath\$($Service.Dir)'; python app.py" -WindowStyle Normal
}

Write-Host "`nAll services have been started in separate windows." -ForegroundColor Magenta
Write-Host "The Local Gateway is running on http://localhost:8000" -ForegroundColor Magenta
Write-Host "The Frontend should be updated to use http://localhost:8000/api/v1 as its base URL." -ForegroundColor Magenta
