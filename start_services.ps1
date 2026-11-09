Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Library Management System (LMS)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if database exists
if (-Not (Test-Path "database\lms.db")) {
    Write-Host "Initializing database..." -ForegroundColor Yellow
    python -m database.init_db
    python -m database.seed_data
}

Write-Host "Starting User Service on port 8001..." -ForegroundColor Green
Start-Process python -ArgumentList "-m", "uvicorn", "services.userservice.main:app", "--port", "8001" -NoNewWindow
Start-Sleep -Seconds 1

Write-Host "Starting Book Service on port 8002..." -ForegroundColor Green
Start-Process python -ArgumentList "-m", "uvicorn", "services.bookservice.main:app", "--port", "8002" -NoNewWindow
Start-Sleep -Seconds 1

Write-Host "Starting Issue Service on port 8003..." -ForegroundColor Green
Start-Process python -ArgumentList "-m", "uvicorn", "services.issueservice.main:app", "--port", "8003" -NoNewWindow
Start-Sleep -Seconds 1

Write-Host "Starting Payment Service on port 8004..." -ForegroundColor Green
Start-Process python -ArgumentList "-m", "uvicorn", "services.paymentservice.main:app", "--port", "8004" -NoNewWindow
Start-Sleep -Seconds 1

Write-Host "Starting Admin Service on port 8005..." -ForegroundColor Green
Start-Process python -ArgumentList "-m", "uvicorn", "services.adminservice.main:app", "--port", "8005" -NoNewWindow
Start-Sleep -Seconds 1

Write-Host "`nAll backend services online!" -ForegroundColor Cyan
Write-Host "Swagger Docs:"
Write-Host "  - User Service    : http://localhost:8001/docs"
Write-Host "  - Book Service    : http://localhost:8002/docs"
Write-Host "  - Issue Service   : http://localhost:8003/docs"
Write-Host "  - Payment Service : http://localhost:8004/docs"
Write-Host "  - Admin Service   : http://localhost:8005/docs"

Write-Host "`nStarting Streamlit Frontend on http://localhost:8501 ..." -ForegroundColor Magenta
streamlit run app.py

