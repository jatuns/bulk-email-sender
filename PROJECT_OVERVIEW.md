# Bulk Mail Dashboard Proje Dokümantasyonu

Bu doküman, Bulk Mail Dashboard projesinin ne yaptığını, nasıl çalıştığını, dosya yapısını ve geliştirme/build sürecini genel olarak açıklar.

## Projenin Amacı

Bulk Mail Dashboard, Gmail SMTP kullanarak `.txt` dosyasındaki alıcılara toplu mail göndermek için geliştirilmiş bir Windows masaüstü uygulamasıdır.

Uygulama özellikle aynı mail içeriğini çok sayıda kişiye göndermek isteyen kullanıcılar için hazırlanmıştır. Kullanıcı, teknik detaylarla uğraşmadan arayüz üzerinden mail listesi seçebilir, listeyi düzenleyebilir, konu ve içerik yazabilir, CV/PDF eki seçebilir ve gönderim durumunu takip edebilir.

## Ana Özellikler

- Windows üzerinde çalışan `.exe` uygulaması
- Modern dashboard arayüzü
- Gmail SMTP ile mail gönderimi
- Gmail uygulama şifresi desteği
- `.txt` mail listesi seçme
- Mail listesini uygulama içinde düzenleme
- CV/PDF eki seçme
- Mail konusu ve içeriğini arayüzden güncelleme
- Başlangıç ve bitiş indexleriyle parça parça gönderim
- Gönderilen ve hatalı mail sayısını takip etme
- Son işlenen index bilgisini gösterme
- Gmail limit/rate limit hatalarında kaldığı indexi gösterme
- Gönderim günlüğü
- Türkçe “Nasıl Kullanılır?” rehberi
- Ayarları `settings.json` içine kaydetme

## Kullanılan Teknolojiler

Proje Python ile geliştirilmiştir.

Kullanılan temel modüller:

- `tkinter`: Masaüstü arayüzü
- `smtplib`: Gmail SMTP bağlantısı
- `email.mime`: Mail içeriği ve ek dosya oluşturma
- `threading`: Gönderim sırasında arayüzün donmaması
- `json`: Kullanıcı ayarlarını saklama
- `pathlib`: Dosya yollarını yönetme
- `PyInstaller`: Python dosyasını Windows `.exe` dosyasına çevirme

## Proje Yapısı

```text
bulk-email-sender/
├── dist/
│   └── BulkMailDashboard_windows.exe
├── examples/
│   └── liste.example.txt
├── scripts/
│   └── build_exe.ps1
├── .env.example
├── .gitattributes
├── .gitignore
├── LICENSE
├── PROJECT_OVERVIEW.md
├── README.md
├── mail_gonder.py
└── requirements.txt
```

## Dosyaların Görevleri

### `mail_gonder.py`

Projenin ana kaynak kodudur. Hem arayüzü hem de mail gönderme mantığını içerir.

Bu dosyada:

- Dashboard penceresi oluşturulur.
- Gmail bilgileri alınır.
- Mail listesi okunur.
- Mail içeriği ve ek dosya hazırlanır.
- SMTP bağlantısı kurulur.
- Gönderim işlemi arka planda çalıştırılır.
- Loglar ve sayaçlar arayüzde güncellenir.
- Mail listesi düzenleme penceresi açılır.
- “Nasıl Kullanılır?” rehberi gösterilir.

### `dist/BulkMailDashboard_windows.exe`

Son kullanıcı için hazırlanmış Windows uygulamasıdır.

Python kurmadan uygulamayı çalıştırmak isteyen kullanıcılar bu dosyayı açabilir.

### `examples/liste.example.txt`

Mail listesi formatını gösteren örnek dosyadır.

Her satıra bir mail adresi yazılması önerilir:

```text
ik@example.com
kariyer@example.com
hr@example.com
```

### `scripts/build_exe.ps1`

Kodda değişiklik yaptıktan sonra yeni exe oluşturmak için kullanılan PowerShell scriptidir.

Çalıştırıldığında `mail_gonder.py` dosyasını PyInstaller ile paketler ve `dist/BulkMailDashboard_windows.exe` dosyasını üretir.

### `requirements.txt`

Geliştirme ve build için gereken Python paketlerini listeler.

Şu anda temel olarak PyInstaller içerir.

### `.env.example`

Gmail bilgileri için örnek environment dosyasıdır.

Gerçek `.env` dosyası GitHub’a yüklenmemelidir.

### `.gitignore`

GitHub’a gitmemesi gereken dosyaları belirler.

Örneğin:

- `.env`
- `settings.json`
- `liste.txt`
- PDF/CV dosyaları
- `.venv/`
- `build/`
- eski build çıktıları

### `README.md`

Kullanıcıya hızlı başlangıç, kurulum, exe kullanımı ve build alma adımlarını anlatır.

### `PROJECT_OVERVIEW.md`

Bu dosyadır. Projeyi daha geniş açıdan açıklar.

## Uygulamanın Çalışma Mantığı

Uygulama açıldığında önce kayıtlı ayarları okumaya çalışır.

Eğer `settings.json` varsa:

- Gmail adresi
- uygulama şifresi
- konu
- mail içeriği
- liste dosyası
- CV dosyası
- başlangıç/bitiş indexleri
- gecikme süresi

bu dosyadan yüklenir.

Eğer `settings.json` yoksa varsayılan değerlerle açılır.

Kullanıcı arayüzden bilgileri girip `Ayarları Kaydet` butonuna basarsa bu bilgiler `settings.json` dosyasına yazılır.

## Mail Gönderim Akışı

1. Kullanıcı `Gönderimi Başlat` butonuna basar.
2. Uygulama gerekli alanları kontrol eder.
3. Mail listesi dosyası okunur.
4. Başlangıç ve bitiş indexlerine göre gönderilecek alıcılar seçilir.
5. Gmail SMTP sunucusuna SSL bağlantısı kurulur.
6. Her alıcı için mail oluşturulur.
7. Eğer CV/PDF seçildiyse mail ekine eklenir.
8. Mail gönderilir.
9. Sonuç log alanına yazılır.
10. Sayaçlar ve progress bar güncellenir.
11. Hata olursa ilgili alıcı loga yazılır.
12. Gmail limit hatası algılanırsa gönderim durdurulur ve limit indexi gösterilir.

## Index Sistemi

Mail listesi sıfırdan başlayan index sistemiyle çalışır.

Örneğin 700 mail varsa:

- İlk mailin indexi `0`
- İkinci mailin indexi `1`
- Son mailin indexi `699`

Başlangıç `0`, bitiş `100` girilirse ilk 100 mail gönderilir.

Gönderim yarıda kalırsa `Son index` kartında en son işlenen index görülür.

Gmail limitine takılırsa `Limit indexi` kartında limitin geldiği index gösterilir.

Devam etmek için başlangıç değeri kaldığınız indexe göre ayarlanabilir.

## Mail Listesi Düzenleme Özelliği

Kullanıcı yalnızca `.txt` dosyası seçmek zorunda değildir. Seçilen dosyanın içeriği uygulama içinde düzenlenebilir.

`Mail Listesini Düzenle` butonuna basıldığında ayrı bir pencere açılır.

Bu pencerede:

- mevcut mail adresleri görüntülenir
- yeni mail adresleri eklenebilir
- eski mail adresleri silinebilir
- içerik aynı `.txt` dosyasına kaydedilebilir
- kayıt sonrası dashboard’daki toplam mail sayısı yenilenir

## Ayarların Saklanması

Uygulama kullanıcı ayarlarını `settings.json` dosyasında saklar.

Bu dosya kişisel bilgi içerebileceği için GitHub’a yüklenmez.

`settings.json` içinde şunlar bulunabilir:

- Gmail adresi
- Gmail uygulama şifresi
- mail konusu
- mail içeriği
- seçilen liste dosyası
- seçilen CV dosyası
- gönderim aralığı
- gecikme süresi

## Güvenlik Notları

Bu projede kişisel ve hassas bilgilerin GitHub’a yüklenmemesi önemlidir.

GitHub’a yüklenmemesi gerekenler:

- gerçek Gmail şifresi
- Gmail uygulama şifresi
- gerçek mail listeleri
- kişisel CV/PDF dosyaları
- `settings.json`
- `.env`

Bu dosyalar `.gitignore` ile ignore edilir.

## Gmail Limitleri

Gmail günlük gönderim sınırlarına sahiptir. Bu sınırlar hesap türüne göre değişebilir.

Uygulama Gmail’den gelen limit/rate limit/quota türü hataları algılamaya çalışır. Böyle bir durumda gönderimi durdurur ve kaldığı indexi dashboard’da gösterir.

Yine de limitlerin Google tarafından yönetildiği unutulmamalıdır. Uygulama limitleri aşmayı sağlamaz, yalnızca gönderimi daha kontrollü takip etmeye yardımcı olur.

## Geliştirme Süreci

Kaynak koddan çalıştırmak için:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe mail_gonder.py
```

Yeni exe oluşturmak için:

```powershell
.\scripts\build_exe.ps1
```

veya:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name BulkMailDashboard_windows mail_gonder.py
```

## GitHub İçin Önerilen Commit İçeriği

GitHub’a eklenmesi uygun dosyalar:

- `mail_gonder.py`
- `README.md`
- `PROJECT_OVERVIEW.md`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `.gitattributes`
- `LICENSE`
- `examples/liste.example.txt`
- `scripts/build_exe.ps1`
- `dist/BulkMailDashboard_windows.exe`

GitHub’a eklenmemesi gereken dosyalar:

- `.env`
- `settings.json`
- `liste.txt`
- gerçek CV/PDF dosyaları
- `.venv/`
- `build/`
- eski exe dosyaları
- `.spec` dosyaları

## Sorumluluk Notu

Bu uygulama teknik olarak toplu mail gönderimini kolaylaştırmak için geliştirilmiştir.

Toplu mail gönderirken:

- alıcıların izni
- ilgili yasal düzenlemeler
- Gmail kullanım kuralları
- spam politikaları

kullanıcının sorumluluğundadır.
