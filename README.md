# Bulk Mail Dashboard

Windows için hazırlanmış, Gmail SMTP üzerinden toplu mail göndermeyi kolaylaştıran masaüstü dashboard uygulaması.

Uygulama ile mail listesi seçebilir, listeyi uygulama içinden düzenleyebilir, konu ve mail içeriğini güncelleyebilir, CV/PDF eki seçebilir, gönderim aralığını belirleyebilir ve gönderim durumunu canlı olarak takip edebilirsiniz.

## Özellikler

- Modern Tkinter tabanlı dashboard arayüzü
- Gmail uygulama şifresi ile SMTP gönderimi
- `.txt` mail listesi seçme ve uygulama içinde düzenleme
- PDF/CV eki seçme
- Konu ve mail içeriğini arayüzden güncelleme
- Başlangıç/bitiş index aralığı ile parça parça gönderim
- Gönderilen, hatalı, son index ve limit indexi göstergeleri
- Gönderim günlüğü
- Türkçe "Nasıl Kullanılır?" rehberi

## Hızlı Kullanım

Hazır exe dosyası:

```text
dist/BulkMailDashboard_v4.exe
```

Windows üzerinde `BulkMailDashboard_v4.exe` dosyasını çift tıklayarak açın.

İlk kullanımda:

1. Gmail adresinizi girin.
2. Gmail uygulama şifrenizi girin.
3. Mail listenizi `.txt` dosyası olarak seçin.
4. Gerekirse `Mail Listesini Düzenle` butonu ile listeyi güncelleyin.
5. CV/PDF dosyanızı seçin.
6. Konu ve mail içeriğini düzenleyin.
7. Başlangıç ve bitiş indexlerini belirleyin.
8. `Ayarları Kaydet` butonuna basın.
9. `Gönderimi Başlat` ile gönderimi başlatın.

Uygulama içinde `Nasıl Kullanılır?` butonu da aynı adımları daha ayrıntılı anlatır.

Daha kapsamlı teknik açıklama için [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) dosyasına bakabilirsiniz.

## Gmail Uygulama Şifresi

Normal Gmail şifresiyle SMTP gönderimi yapılamaz. Google hesabınızda iki aşamalı doğrulama açık olmalı ve uygulama şifresi oluşturmalısınız.

1. Google hesabınıza gidin: <https://myaccount.google.com>
2. `Güvenlik` bölümünü açın.
3. `2 Adımlı Doğrulama` özelliğini etkinleştirin.
4. Google hesap aramasında `Uygulama şifreleri` veya `App passwords` arayın.
5. Yeni bir uygulama şifresi oluşturun.
6. Oluşan 16 haneli şifreyi uygulamadaki `Uygulama şifresi` alanına girin.

## Mail Listesi Formatı

Mail listesi düz bir `.txt` dosyası olmalıdır. Her satıra bir mail adresi yazılması önerilir.

```text
ik@example.com
kariyer@example.com
hr@example.com
```

Örnek dosya:

```text
examples/liste.example.txt
```

Gerçek `liste.txt` dosyanızı GitHub'a yüklemeyin. Bu dosya `.gitignore` içinde ignore edilir.

## Kaynak Koddan Çalıştırma

Python ile çalıştırmak için:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe mail_gonder.py
```

## Exe Build Alma

Kodda değişiklik yaptıktan sonra exe otomatik güncellenmez. Yeni exe oluşturmak için:

```powershell
.\scripts\build_exe.ps1
```

Alternatif olarak doğrudan:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name BulkMailDashboard_v4 mail_gonder.py
```

Çıktı:

```text
dist/BulkMailDashboard_v4.exe
```

## Proje Yapısı

```text
bulk-email-sender/
├── dist/
│   └── BulkMailDashboard_v4.exe
├── examples/
│   └── liste.example.txt
├── scripts/
│   └── build_exe.ps1
├── .env.example
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── mail_gonder.py
└── requirements.txt
```

## GitHub'a Eklenmemesi Gerekenler

Aşağıdaki dosyalar kişisel veya build çıktısı olduğu için repoya eklenmez:

- `.env`
- `settings.json`
- `liste.txt`
- PDF/CV dosyaları
- `.venv/`
- `build/`
- eski `.spec` dosyaları
- eski exe çıktıları

## Notlar

Gmail günlük gönderim sınırlarına tabidir. Sınıra ulaşıldığında uygulama hatayı algılamaya çalışır ve `Limit indexi` alanında kaldığı indexi gösterir.

Toplu mail gönderirken alıcıların izni, ilgili mevzuat ve platform kurallarına uymak sizin sorumluluğunuzdedir.

## Lisans

MIT
