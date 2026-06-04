# Bulk Mail Dashboard

<div align="center">
  <a href="#türkçe">🇹🇷 Türkçe</a> &nbsp;·&nbsp; <a href="#english">🇬🇧 English</a>
</div>

---

<h2 id="türkçe">🇹🇷 Türkçe</h2>

Gmail SMTP üzerinden toplu mail göndermeyi kolaylaştıran masaüstü dashboard uygulaması. **Windows ve macOS** üzerinde çalışır.

Uygulama ile mail listesi seçebilir, listeyi uygulama içinden düzenleyebilir, konu ve mail içeriğini güncelleyebilir, CV/PDF eki seçebilir, ek olarak birden fazla portfolyo PDF'i ekleyebilir, gönderim aralığını belirleyebilir ve gönderim durumunu canlı olarak takip edebilirsiniz.

### Özellikler

- Modern Tkinter tabanlı dashboard arayüzü
- Gmail uygulama şifresi ile SMTP gönderimi
- `.txt` mail listesi seçme ve uygulama içinde düzenleme
- PDF/CV eki seçme
- Birden fazla portfolyo PDF'i ekleme (sertifika, referans mektubu vb.)
- Konu ve mail içeriğini arayüzden güncelleme
- Başlangıç/bitiş index aralığı ile parça parça gönderim
- Gönderilen, hatalı, son index ve limit indexi göstergeleri
- Gönderim günlüğü
- Türkçe "Nasıl Kullanılır?" rehberi

### Hızlı Kullanım

**macOS** — hazır uygulama paketini çift tıklayarak veya terminal ile açın:

```bash
open dist/BulkMailDashboard.app
```

**Windows** — repo içinde hazır `.exe` yok. Python kurulu ise [Kaynak Koddan Çalıştırma](#kaynak-koddan-çalıştırma) adımlarını izleyin; tek dosyalık `.exe` istiyorsanız [Build Alma](#build-alma) bölümüne göre kendi `.exe`'nizi oluşturun.

İlk kullanımda:

1. Gmail adresinizi girin.
2. Gmail uygulama şifrenizi girin.
3. Mail listenizi `.txt` dosyası olarak seçin.
4. Gerekirse `Mail Listesini Düzenle` butonu ile listeyi güncelleyin.
5. CV/PDF dosyanızı seçin. İsterseniz `Portfolyo ekleri` bölümünden ek PDF'ler de ekleyebilirsiniz.
6. Konu ve mail içeriğini düzenleyin.
7. Başlangıç ve bitiş indexlerini belirleyin.
8. `Ayarları Kaydet` butonuna basın.
9. `Gönderimi Başlat` ile gönderimi başlatın.

Uygulama içinde `Nasıl Kullanılır?` butonu da aynı adımları daha ayrıntılı anlatır.

### Gmail Uygulama Şifresi

Normal Gmail şifresiyle SMTP gönderimi yapılamaz. Google hesabınızda iki aşamalı doğrulama açık olmalı ve uygulama şifresi oluşturmalısınız.

1. Google hesabınıza gidin: <https://myaccount.google.com>
2. `Güvenlik` bölümünü açın.
3. `2 Adımlı Doğrulama` özelliğini etkinleştirin.
4. Google hesap aramasında `App passwords` arayın.
5. Yeni bir uygulama şifresi oluşturun.
6. Oluşan 16 haneli şifreyi uygulamadaki `Uygulama şifresi` alanına girin.

### Mail Listesi Formatı

Mail listesi düz bir `.txt` dosyası olmalıdır. Her satıra bir mail adresi yazılması önerilir.

```text
ik@example.com
kariyer@example.com
hr@example.com
```

Örnek dosya: `examples/liste.example.txt`

Gerçek `liste.txt` dosyanızı GitHub'a yüklemeyin. Bu dosya `.gitignore` içinde yoksayılır.

### Kaynak Koddan Çalıştırma

**Windows:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe mail_gonder.py
```

**macOS:**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python mail_gonder.py
```

### Build Alma

**Windows** — yeni `.exe` oluşturmak için:

```powershell
.\scripts\build_exe.ps1
```

**macOS** — yeni `.app` oluşturmak için:

```bash
bash scripts/build_mac.sh
```

macOS build scripti otomatik olarak sanal ortam oluşturur, bağımlılıkları kurar, uygulamayı derler ve imzalar.

### Proje Yapısı

```text
bulk-email-sender/
├── dist/
│   └── BulkMailDashboard.app      # macOS (Windows: build locally)
├── examples/
│   └── liste.example.txt
├── scripts/
│   ├── build_exe.ps1              # Windows build
│   └── build_mac.sh               # macOS build
├── LICENSE
├── README.md
├── mail_gonder.py
└── requirements.txt
```

### Notlar

Gmail günlük gönderim sınırlarına tabidir. Sınıra ulaşıldığında uygulama hatayı algılamaya çalışır ve `Limit indexi` alanında kaldığı indexi gösterir.

Toplu mail gönderirken alıcıların izni, ilgili mevzuat ve platform kurallarına uymak sizin sorumluluğunuzdadır.

### Lisans

MIT

---

<h2 id="english">🇬🇧 English</h2>

A desktop dashboard application for sending bulk emails via Gmail SMTP. Works on **Windows and macOS**.

You can select a recipient list, edit it directly within the app, update the subject and body, attach a PDF/CV, add multiple portfolio PDFs, set a sending range, and monitor the sending progress in real time.

### Features

- Modern Tkinter-based dashboard UI
- Gmail SMTP sending via app password
- Select and edit a `.txt` recipient list within the app
- PDF/CV attachment support
- Multiple portfolio PDFs (certificates, reference letters, etc.)
- Update subject and body from the UI
- Send in chunks using start/end index ranges
- Live counters for sent, failed, last index, and limit index
- Real-time sending log
- Built-in "How to Use" guide

### Quick Start

**macOS** — double-click or open from the terminal:

```bash
open dist/BulkMailDashboard.app
```

**Windows** — no prebuilt `.exe` is shipped in the repo. If Python is installed, follow [Running from Source](#running-from-source); to produce a single-file `.exe`, see [Building](#building).

First-time setup:

1. Enter your Gmail address.
2. Enter your Gmail app password.
3. Select your recipient list as a `.txt` file.
4. Optionally edit the list using the `Edit Mail List` button.
5. Select your PDF/CV file. Optionally, add extra PDFs via the `Portfolio attachments` section.
6. Edit the subject and message body.
7. Set the start and end index range.
8. Click `Save Settings`.
9. Click `Start Sending` to begin.

The in-app `How to Use?` button walks through the same steps in more detail.

### Gmail App Password

Standard Gmail passwords do not work with SMTP. You need two-factor authentication enabled and a dedicated app password.

1. Go to your Google account: <https://myaccount.google.com>
2. Open the `Security` section.
3. Enable `2-Step Verification`.
4. Search for `App passwords` in the Google account search bar.
5. Create a new app password.
6. Paste the generated 16-character password into the `App password` field in the app.

### Recipient List Format

The recipient list must be a plain `.txt` file with one email address per line.

```text
hr@example.com
careers@example.com
jobs@example.com
```

Example file: `examples/liste.example.txt`

Do not commit your actual `liste.txt` to GitHub — it is listed in `.gitignore`.

### Running from Source

**Windows:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe mail_gonder.py
```

**macOS:**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python mail_gonder.py
```

### Building

**Windows** — generate a new `.exe`:

```powershell
.\scripts\build_exe.ps1
```

**macOS** — generate a new `.app`:

```bash
bash scripts/build_mac.sh
```

The macOS build script automatically creates a virtual environment, installs dependencies, compiles the app, and signs the bundle.

### Project Structure

```text
bulk-email-sender/
├── dist/
│   └── BulkMailDashboard.app      # macOS (Windows: build locally)
├── examples/
│   └── liste.example.txt
├── scripts/
│   ├── build_exe.ps1              # Windows build
│   └── build_mac.sh               # macOS build
├── LICENSE
├── README.md
├── mail_gonder.py
└── requirements.txt
```

### Notes

Gmail enforces daily sending limits. When a limit is reached, the app attempts to detect the error and displays the last index in the `Limit index` field so you can resume later.

It is your responsibility to ensure you have recipients' consent and comply with applicable laws and platform rules when sending bulk email.

### License

MIT
