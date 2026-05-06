$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name BulkMailDashboard_windows mail_gonder.py

Write-Host "Build tamamlandı: dist\BulkMailDashboard_windows.exe"
