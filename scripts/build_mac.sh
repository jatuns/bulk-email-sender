#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Tkinter desteği olan bir Python bul
PYTHON=""
for candidate in /opt/homebrew/bin/python3.14 /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.12 python3; do
    if command -v "$candidate" &>/dev/null && "$candidate" -c "import tkinter" 2>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "HATA: Tkinter destekli Python bulunamadı."
    echo "Çözüm: brew install python-tk@3.14"
    exit 1
fi

echo "==> Kullanılan Python: $($PYTHON --version) ($PYTHON)"

echo "==> Sanal ortam oluşturuluyor..."
rm -rf .venv
"$PYTHON" -m venv .venv

echo "==> Bağımlılıklar yükleniyor..."
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install pyinstaller --quiet

echo "==> Uygulama derleniyor..."
.venv/bin/python -m PyInstaller \
    --noconfirm \
    --windowed \
    --name "BulkMailDashboard" \
    mail_gonder.py

echo "==> İmzalanıyor..."
xattr -cr dist/BulkMailDashboard.app
codesign --force --deep --sign - dist/BulkMailDashboard.app

echo ""
echo "Build tamamlandı: dist/BulkMailDashboard.app"
echo "Başlatmak için: open dist/BulkMailDashboard.app"
