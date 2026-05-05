# Bulk Email Sender

Gmail SMTP ile toplu mail gönderme scripti. CV veya herhangi bir dosyayı ek olarak gönderebilir, kişiselleştirilmiş mesaj yazabilirsiniz.

---

## Hızlı Başlangıç

### 1. Repoyu klonla

```bash
git clone https://github.com/jatuns/bulk-email-sender.git
cd bulk-email-sender
```

### 2. Bağımlılığı yükle

```bash
pip install python-dotenv
```

### 3. `.env` dosyasını oluştur

```bash
cp .env.example .env
```

`.env` dosyasını aç ve kendi bilgilerini gir:

```
GONDEREN_EMAIL=senin@gmail.com
GMAIL_APP_SIFRE=xxxx xxxx xxxx xxxx
```

> App Password için aşağıdaki bölüme bak.

### 4. Alıcı listeni oluştur

```bash
cp liste.txt.example liste.txt
```

`liste.txt` dosyasını aç ve mail göndermek istediğin adresleri yaz (her satıra bir adres):

```
hr@sirket1.com
kariyer@sirket2.com
```

### 5. CV veya ek dosyayı ekle

PDF dosyasını proje klasörüne koy. `mail_gonder.py` içinde `CV_DOSYASI` değişkenini dosya adınla güncelle.

### 6. Mail içeriğini yaz

`mail_gonder.py` dosyasını aç, `KONU` ve `ICERIK` değişkenlerini kendinize göre düzenle.

### 7. Çalıştır

```bash
python mail_gonder.py
```

---

## Gmail App Password Nasıl Alınır?

Normal Gmail şifresi çalışmaz. Google'a özel bir App Password gereklidir.

1. [myaccount.google.com](https://myaccount.google.com) → **Güvenlik**
2. **2 Adımlı Doğrulama**'yı etkinleştir
3. Arama kutusuna **"App passwords"** yaz → tıkla
4. Uygulama adı gir (örn. `mail-script`) → **Create**
5. Çıkan **16 haneli şifreyi** `.env` dosyasına kopyala

---

## Büyük Listeler (Gmail Günlük Limiti ~500)

`mail_gonder.py` içindeki `BASLANGIC` ve `BITIS` değerleriyle listeyi günlere böl:

| Gün | BASLANGIC | BITIS |
|-----|-----------|-------|
| 1   | 0         | 400   |
| 2   | 400       | 800   |

---

## Proje Yapısı

```
bulk-email-sender/
├── mail_gonder.py       # Ana script — konu, içerik ve ayarlar burada
├── liste.txt.example    # Alıcı listesi formatı (bunu liste.txt olarak kopyala)
├── .env.example         # Gizli bilgi şablonu (bunu .env olarak kopyala)
├── .gitignore
├── LICENSE
└── README.md
```

> `.env` ve `liste.txt` gitignore'dadır — GitHub'a yüklenmez.

---

## Lisans

MIT © [Barış Tuna Tuğrul](https://github.com/jatuns)
