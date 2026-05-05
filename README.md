# Otomatik Mail Gönderme Scripti

Bu script, bir alıcı listesine toplu e-posta göndermenizi sağlar. Staj başvurusu, iş başvurusu veya herhangi bir toplu mail ihtiyacı için kullanılabilir.

---

## Gereksinimler

- Python 3.8 veya üzeri
- Gmail hesabı + **App Password** (normal şifre çalışmaz)

---

## Kurulum

### 1. Repoyu klonla

```bash
git clone https://github.com/KULLANICI_ADI/REPO_ADI.git
cd REPO_ADI
```

### 2. (Opsiyonel) Virtual environment oluştur

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. `python-dotenv` kütüphanesini yükle

```bash
pip install python-dotenv
```

> Script dotenv olmadan da çalışabilir, ama `.env` dosyasını okumak için bu kütüphane gereklidir.

---

## Gmail App Password Nasıl Alınır?

Normal Gmail şifreniz bu script için **çalışmaz**. Google'ın 2 adımlı doğrulama sistemine özel bir "App Password" oluşturmanız gerekir.

1. [myaccount.google.com](https://myaccount.google.com) adresine git
2. Sol menüden **Güvenlik** sekmesini aç
3. **2 Adımlı Doğrulama**'yı etkinleştir (etkin değilse)
4. Arama kutusuna **"App passwords"** yaz ve tıkla
5. Uygulama adı olarak istediğinizi yazın (örn. `mail-script`) ve **Create** butonuna tıklayın
6. Çıkan **16 haneli şifreyi** kopyalayın (boşluklu gösterilir, olduğu gibi kullanabilirsiniz)

---

## Yapılandırma

### 4. `.env` dosyası oluştur

Proje klasörünün içinde `.env` adında bir dosya oluştur ve aşağıdaki bilgileri gir:

```
GONDEREN_EMAIL=senin@gmail.com
GMAIL_APP_SIFRE=xxxx xxxx xxxx xxxx
```

> `.env` dosyası `.gitignore`'a eklenmiştir, GitHub'a **yüklenmez**.

### 5. `mail_gonder.py` içindeki ayarları düzenle

Dosyanın üst kısmındaki sabit değerleri kendinize göre güncelleyin:

| Değişken | Açıklama |
|---|---|
| `KONU` | E-posta konu satırı |
| `ICERIK` | E-posta gövdesi (istediğiniz dili/metni yazabilirsiniz) |
| `LISTE_DOSYASI` | Alıcı e-posta adreslerini içeren dosyanın adı |
| `CV_DOSYASI` | Eklemek istediğiniz PDF dosyasının adı (yoksa ek gönderilmez) |
| `BASLANGIC` | Listede kaçıncı adresten başlanacak (0 = baştan) |
| `BITIS` | Listede kaçıncı adrese kadar gidilecek |
| `GECIKME_SN` | Her mail arasındaki bekleme süresi (saniye) |

### 6. Alıcı listesini hazırla

`liste.txt` adında bir dosya oluştur; her satıra bir e-posta adresi yaz:

```
hr@firma1.com
info@firma2.com
kariyer@firma3.com
```

### 7. (Opsiyonel) PDF ekini yerleştir

Eğer bir dosya eklemek istiyorsanız, PDF'i proje klasörüne koyun ve `CV_DOSYASI` değişkenini dosya adıyla güncelleyin.

---

## Çalıştırma

```bash
python mail_gonder.py
```

Çıktı şu şekilde görünür:

```
Gönderilecek: 400 mail (0–400)

[1/400] ✓  hr@firma1.com
[2/400] ✓  kariyer@firma2.com
[3/400] ✗  hataliadres@firma3  →  ...hata mesajı...
...
Bitti. 0–400 aralığı tamamlandı.
```

---

## Büyük Listeler için Toplu Gönderim (Gmail Limiti)

Gmail günlük ~500 mail gönderme limitine sahiptir. Listeyi birden fazla günde göndermeye bölmek için `BASLANGIC` ve `BITIS` değerlerini değiştirin:

| Gün | BASLANGIC | BITIS |
|---|---|---|
| 1. Gün | 0 | 400 |
| 2. Gün | 400 | 782 |

---

## Proje Yapısı

```
mail-automation/
├── mail_gonder.py   # Ana script
├── liste.txt        # Alıcı listesi (gitignore'da)
├── CV.pdf           # Ek dosya (gitignore'da)
├── .env             # Gizli bilgiler (gitignore'da, paylaşma!)
├── .gitignore
└── README.md
```
