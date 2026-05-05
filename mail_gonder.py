import smtplib
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv yüklü değilse .env manuel okunur

def _env(key):
    val = os.environ.get(key)
    if not val:
        raise EnvironmentError(f".env dosyasında '{key}' bulunamadı.")
    return val

# ──────────────────────────────────────────
# AYARLAR
# ──────────────────────────────────────────
GONDEREN_EMAIL  = _env("GONDEREN_EMAIL")
GMAIL_APP_SIFRE = _env("GMAIL_APP_SIFRE")

KONU = "2026 Yaz Stajı Başvurusu / 2026 Summer Internship Application - Barış Tuna Tuğrul"

ICERIK = """\
Dear Manager,

I am writing to express my interest in completing a summer internship at your company. I am currently a third-year Information Systems and Technologies (CTIS) student at Bilkent University, and I am seeking an opportunity where I can apply my skills in software development, data analytics, and data science in a real-world environment.

My academic background and hands-on projects have provided me with a strong technical foundation. I have built FastAPI-based backend systems, developed machine learning pipelines using XGBoost and scikit-learn, and worked extensively with Python, SQL, and R for data analysis and visualization. My portfolio projects include a music-based movie recommendation system and a flight delay prediction platform — both deployed and available at baristunatugrul.com. Additionally, I have worked on a football transfer data analysis project and developed an equipment rental management system for Bilkent University's COMD department.

I would also like to note that my internship insurance (SGK) will be fully covered by Bilkent University, and all required documents can be provided promptly. My internship can be full-time for a minimum of 1 month, with the possibility of extending up to 2 months based on your needs.

I would be happy to discuss how I can contribute to your organization. Please find my CV attached.

Sincerely,
Barış Tuna Tuğrul
+90 507 320 80 12
linkedin.com/in/baristunatugrul
github.com/jatuns
baristunatugrul.com

──────────────────────────────────────────

Merhaba,

Bilkent Üniversitesi Bilişim Sistemleri ve Teknolojileri (CTIS) bölümünde üçüncü sınıf öğrencisiyim. Şirketinizde yaz stajı yapmak istediğimi belirtmek için yazıyorum. Yazılım geliştirme, veri analitiği ve veri bilimi alanlarındaki birikimimi gerçek bir ortamda uygulayabileceğim bir staj fırsatı arıyorum.

Akademik geçmişim ve projelerim bana güçlü bir teknik altyapı kazandırdı. FastAPI ile backend sistemleri geliştirdim, XGBoost ve scikit-learn kullanarak makine öğrenmesi pipeline'ları kurdum; Python, SQL ve R ile veri analizi ve görselleştirme üzerine kapsamlı çalışmalar yaptım. Portföy projelerim arasında müzik tabanlı bir film öneri sistemi ve uçuş gecikme tahmin platformu yer alıyor — her ikisi de baristunatugrul.com adresinde yayında. Bunların yanı sıra futbol transfer verilerini analiz eden bir proje geliştirdim ve Bilkent Üniversitesi COMD departmanı için bir ekipman kiralama yönetim sistemi oluşturdum.

Staj sigortam (SGK) Bilkent Üniversitesi tarafından karşılanmakta olup gerekli evraklar kısa sürede temin edilebilir. Stajım en az 1 ay tam zamanlı olarak gerçekleştirilebilir; ihtiyacınıza göre 2 aya kadar uzatılabilir.

CV'mi ekte iletiyorum. Uygun görmeniz hâlinde görüşmekten memnuniyet duyarım.

İyi çalışmalar,
Barış Tuna Tuğrul
+90 507 320 80 12
linkedin.com/in/baristunatugrul
github.com/jatuns
baristunatugrul.com
"""

LISTE_DOSYASI = "liste.txt"
CV_DOSYASI    = "BarisTunaTugrul-CV.pdf"

BASLANGIC     = 0     # ilk gün: 0 | ikinci gün: 400
BITIS         = 400   # ilk gün: 400 | ikinci gün: 782
GECIKME_SN    = 2
# ──────────────────────────────────────────

def emailleri_oku():
    with open(LISTE_DOSYASI, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and "@" in line]

def mail_olustur(alici):
    msg = MIMEMultipart()
    msg["From"]    = GONDEREN_EMAIL
    msg["To"]      = alici
    msg["Subject"] = KONU
    msg.attach(MIMEText(ICERIK, "plain", "utf-8"))
    if os.path.exists(CV_DOSYASI):
        with open(CV_DOSYASI, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{CV_DOSYASI}"')
        msg.attach(part)
    return msg

def gonder():
    liste = emailleri_oku()
    hedef = liste[BASLANGIC:BITIS]
    print(f"Gönderilecek: {len(hedef)} mail ({BASLANGIC}–{BITIS})\n")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GONDEREN_EMAIL, GMAIL_APP_SIFRE)
        for i, alici in enumerate(hedef, 1):
            try:
                server.sendmail(GONDEREN_EMAIL, alici, mail_olustur(alici).as_string())
                print(f"[{i}/{len(hedef)}] ✓  {alici}")
            except Exception as e:
                print(f"[{i}/{len(hedef)}] ✗  {alici}  →  {e}")
            time.sleep(GECIKME_SN)
    print(f"\nBitti. {BASLANGIC}–{BITIS} aralığı tamamlandı.")

if __name__ == "__main__":
    gonder()
