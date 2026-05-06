$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name BulkMailDashboard_v4 mail_gonder.py

Write-Host "Build tamamlandı: dist\BulkMailDashboard_v4.exe"
