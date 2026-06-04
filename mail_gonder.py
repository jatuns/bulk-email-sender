import json
import os
import platform
import re
import smtplib
import sys
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

_SYS = platform.system()
if _SYS == "Darwin":
    _UI, _UI_B, _MONO = "Helvetica Neue", "Helvetica Neue", "Menlo"
    def _f(size): return (_UI, size)
    def _fb(size): return (_UI_B, size, "bold")
    def _fm(size): return (_MONO, size)
else:
    _UI, _UI_B, _MONO = "Segoe UI", "Segoe UI Semibold", "Cascadia Mono"
    def _f(size): return (_UI, size)
    def _fb(size): return (_UI_B, size)
    def _fm(size): return (_MONO, size)


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

BASE_DIR = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "settings.json"
ENV_FILE = BASE_DIR / ".env"

DEFAULT_SUBJECT = "Konu başlığınızı buraya yazın"
DEFAULT_BODY = """Merhaba,

Bu alanı kendi mail içeriğinize göre düzenleyin.

Uygulama tüm alıcılara bu metni gönderir. Sağ taraftaki editörden metni güncelleyebilir, ardından Ayarları Kaydet butonuyla sonraki açılışlar için saklayabilirsiniz.

İyi çalışmalar,
Ad Soyad
"""


def read_env_file():
    values = {}
    if not ENV_FILE.exists():
        return values
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def default_settings():
    env = read_env_file()
    return {
        "sender_email": env.get("GONDEREN_EMAIL", ""),
        "app_password": env.get("GMAIL_APP_SIFRE", ""),
        "subject": DEFAULT_SUBJECT,
        "body": DEFAULT_BODY,
        "list_file": str(BASE_DIR / "liste.txt"),
        "cv_file": str(BASE_DIR / "cv.pdf"),
        "portfolio_files": [],
        "start_index": 0,
        "end_index": 400,
        "delay_seconds": 2,
    }


def load_settings():
    settings = default_settings()
    if SETTINGS_FILE.exists():
        try:
            saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            known = set(settings.keys())
            settings.update({k: v for k, v in saved.items() if k in known})
        except (OSError, json.JSONDecodeError):
            pass
    return settings


def save_settings(settings):
    SETTINGS_FILE.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")


def read_recipients(path):
    with open(path, encoding="utf-8") as file:
        return [line.strip() for line in file if _EMAIL_RE.match(line.strip())]


LIMIT_ERROR_KEYWORDS = (
    "daily user sending limit exceeded",
    "user-rate limit exceeded",
    "rate limit exceeded",
    "sending limit exceeded",
    "4.7.0",
    "5.4.5",
)


def is_limit_error(exc):
    text = str(exc).lower()
    return any(keyword in text for keyword in LIMIT_ERROR_KEYWORDS)


@dataclass
class MailJob:
    sender_email: str
    app_password: str
    subject: str
    body: str
    list_file: str
    cv_file: str
    portfolio_files: list
    start_index: int
    end_index: int
    delay_seconds: float


def create_message(job, recipient):
    msg = MIMEMultipart()
    msg["From"] = job.sender_email
    msg["To"] = recipient
    msg["Subject"] = job.subject
    msg.attach(MIMEText(job.body, "plain", "utf-8"))

    attachments = []
    if job.cv_file:
        attachments.append(job.cv_file)
    attachments.extend(job.portfolio_files or [])

    for path in attachments:
        if not path or not os.path.exists(path):
            continue
        with open(path, "rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=os.path.basename(path))
        msg.attach(part)

    return msg


class BulkMailDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bulk Mail Dashboard")
        self.geometry("1240x820")
        self.minsize(1080, 760)
        self.configure(bg="#eef2f6")

        self.settings = load_settings()
        self.stop_event = threading.Event()
        self.worker = None

        self._configure_style()
        self._build_variables()
        self._build_layout()
        self.refresh_summary()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#eef2f6")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("TLabel", background="#eef2f6", foreground="#172033", font=_f(10))
        style.configure("Panel.TLabel", background="#ffffff", foreground="#172033", font=_f(10))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#68768a", font=_f(9))
        style.configure("Title.TLabel", background="#eef2f6", foreground="#0f172a", font=_fb(19))
        style.configure("Subtitle.TLabel", background="#eef2f6", foreground="#68768a", font=_f(10))
        style.configure("Metric.TLabel", background="#ffffff", foreground="#0f172a", font=_fb(21))
        style.configure("TEntry", fieldbackground="#f8fafc", bordercolor="#d9e2ec", lightcolor="#d9e2ec", darkcolor="#d9e2ec", padding=8)
        style.configure("TSpinbox", fieldbackground="#f8fafc", bordercolor="#d9e2ec", lightcolor="#d9e2ec", darkcolor="#d9e2ec", padding=7)
        style.configure("Horizontal.TProgressbar", troughcolor="#dfe7f0", background="#1f7a5c", bordercolor="#dfe7f0", lightcolor="#1f7a5c", darkcolor="#1f7a5c")
        style.layout(
            "Modern.Vertical.TScrollbar",
            [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})],
        )
        style.configure("Modern.Vertical.TScrollbar", background="#bcc8d6", troughcolor="#f8fafc", bordercolor="#f8fafc", arrowcolor="#bcc8d6", relief="flat", width=10)
        style.layout(
            "Modern.Horizontal.TScrollbar",
            [("Horizontal.Scrollbar.trough", {"sticky": "ew", "children": [("Horizontal.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})],
        )
        style.configure("Modern.Horizontal.TScrollbar", background="#bcc8d6", troughcolor="#f8fafc", bordercolor="#f8fafc", arrowcolor="#bcc8d6", relief="flat", width=10)

    def _build_variables(self):
        self.sender_email = tk.StringVar(value=self.settings["sender_email"])
        self.app_password = tk.StringVar(value=self.settings["app_password"])
        self.subject = tk.StringVar(value=self.settings["subject"])
        self.list_file = tk.StringVar(value=self.settings["list_file"])
        self.cv_file = tk.StringVar(value=self.settings["cv_file"])
        self.portfolio_files = list(self.settings.get("portfolio_files") or [])
        self.start_index = tk.IntVar(value=int(self.settings["start_index"]))
        self.end_index = tk.IntVar(value=int(self.settings["end_index"]))
        self.delay_seconds = tk.DoubleVar(value=float(self.settings["delay_seconds"]))
        self.total_count = tk.StringVar(value="0")
        self.target_count = tk.StringVar(value="0")
        self.sent_count = tk.StringVar(value="0")
        self.failed_count = tk.StringVar(value="0")
        self.last_index = tk.StringVar(value="-")
        self.limit_index = tk.StringVar(value="-")
        self.status_text = tk.StringVar(value="Hazır")
        self.progress_value = tk.DoubleVar(value=0)

    def _build_layout(self):
        header = ttk.Frame(self, padding=(18, 16, 18, 8))
        header.pack(fill="x")
        title_group = ttk.Frame(header)
        title_group.pack(side="left")
        ttk.Label(title_group, text="Bulk Mail Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_group, text="Ayarla, düzenle, gönderimi takip et", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))
        self._button(header, "Ayarları Kaydet", self.save_current_settings, "secondary").pack(side="right", padx=(8, 0))
        self._button(header, "Listeyi Yenile", self.refresh_summary, "ghost").pack(side="right")
        self._button(header, "Nasıl Kullanılır?", self.open_help_guide, "ghost").pack(side="right", padx=(0, 8))

        metrics = ttk.Frame(self, padding=(18, 8))
        metrics.pack(fill="x")
        metric_items = (
            ("Toplam mail", self.total_count),
            ("Seçilen aralık", self.target_count),
            ("Gönderilen", self.sent_count),
            ("Hatalı", self.failed_count),
            ("Son index", self.last_index),
            ("Limit indexi", self.limit_index),
        )
        for column, (label, variable) in enumerate(metric_items):
            metrics.columnconfigure(column, weight=1)
            pad_left = 0 if column == 0 else 6
            pad_right = 0 if column == len(metric_items) - 1 else 6
            self._metric_card(metrics, label, variable).grid(row=0, column=column, sticky="ew", padx=(pad_left, pad_right))

        main = ttk.Frame(self, padding=(18, 8, 18, 18))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main, style="Panel.TFrame", padding=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ttk.Frame(main, style="Panel.TFrame", padding=16)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right.rowconfigure(3, weight=3)
        right.rowconfigure(5, weight=2, minsize=190)
        right.columnconfigure(0, weight=1)

        self._build_settings_panel(left)
        self._build_message_panel(right)

    def _metric_card(self, parent, label, variable):
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=(14, 12))
        ttk.Label(frame, text=label, style="Muted.TLabel").pack(anchor="w")
        ttk.Label(frame, textvariable=variable, style="Metric.TLabel").pack(anchor="w", pady=(4, 0))
        return frame

    def _button(self, parent, text, command, variant="primary", state="normal"):
        palette = {
            "primary": ("#176b50", "#ffffff", "#135b44"),
            "secondary": ("#172033", "#000000", "#0f172a"),
            "danger": ("#c24141", "#ffffff", "#a83232"),
            "ghost": ("#e7edf4", "#172033", "#d8e1ec"),
        }
        bg, fg, active = palette[variant]
        return tk.Button(
            parent,
            text=text,
            command=command,
            state=state,
            bg=bg,
            fg=fg,
            activebackground=active,
            activeforeground=fg,
            disabledforeground="#edf2f7",
            bd=0,
            relief="flat",
            cursor="hand2",
            font=_fb(10),
            padx=14,
            pady=9,
        )

    def _build_settings_panel(self, parent):
        parent.columnconfigure(1, weight=1)

        ttk.Label(parent, text="Gönderici", style="Panel.TLabel", font=_fb(12)).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        self._entry(parent, "Gmail", self.sender_email, 1)
        self._entry(parent, "Uygulama şifresi", self.app_password, 2, show="*")

        ttk.Label(parent, text="Dosyalar", style="Panel.TLabel", font=_fb(12)).grid(row=3, column=0, columnspan=3, sticky="w", pady=(18, 12))
        self._file_row(parent, "Mail listesi", self.list_file, 4, [("Text files", "*.txt"), ("All files", "*.*")])
        self._file_row(parent, "CV eki", self.cv_file, 5, [("PDF files", "*.pdf"), ("All files", "*.*")])
        self._portfolio_row(parent, 6)

        list_tools = ttk.Frame(parent, style="Panel.TFrame")
        list_tools.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(8, 4))
        list_tools.columnconfigure(0, weight=1)
        list_tools.columnconfigure(1, weight=1)
        self._button(list_tools, "Mail Listesini Düzenle", self.open_list_editor, "secondary").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(list_tools, "Dosyayı Yenile", self.refresh_summary, "ghost").grid(row=0, column=1, sticky="ew", padx=(6, 0))

        ttk.Label(parent, text="Gönderim", style="Panel.TLabel", font=_fb(12)).grid(row=8, column=0, columnspan=3, sticky="w", pady=(18, 12))
        self._spin(parent, "Başlangıç", self.start_index, 9, 0, 100000)
        self._spin(parent, "Bitiş", self.end_index, 10, 1, 100000)
        self._spin(parent, "Gecikme sn", self.delay_seconds, 11, 0, 3600, increment=0.5)

        buttons = ttk.Frame(parent, style="Panel.TFrame")
        buttons.grid(row=12, column=0, columnspan=3, sticky="ew", pady=(22, 10))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        self.send_button = self._button(buttons, "Gönderimi Başlat", self.start_sending, "primary")
        self.send_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.stop_button = self._button(buttons, "Durdur", self.stop_sending, "danger", state="disabled")
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        ttk.Label(parent, textvariable=self.status_text, style="Muted.TLabel").grid(row=13, column=0, columnspan=3, sticky="w")
        ttk.Progressbar(parent, variable=self.progress_value, maximum=100).grid(row=14, column=0, columnspan=3, sticky="ew", pady=(8, 0))

    def _build_message_panel(self, parent):
        ttk.Label(parent, text="Konu", style="Panel.TLabel", font=_fb(12)).grid(row=0, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.subject).grid(row=1, column=0, sticky="ew", pady=(8, 14))

        ttk.Label(parent, text="Mail içeriği", style="Panel.TLabel", font=_fb(12)).grid(row=2, column=0, sticky="w")
        body_frame = ttk.Frame(parent, style="Panel.TFrame")
        body_frame.grid(row=3, column=0, sticky="nsew", pady=(8, 14))
        body_frame.rowconfigure(0, weight=1)
        body_frame.columnconfigure(0, weight=1)
        self.body_text = tk.Text(
            body_frame,
            wrap="word",
            font=_f(10),
            bg="#f8fafc",
            fg="#172033",
            insertbackground="#176b50",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#d9e2ec",
            highlightcolor="#176b50",
            padx=12,
            pady=12,
        )
        self.body_text.insert("1.0", self.settings["body"])
        self.body_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(body_frame, orient="vertical", command=self.body_text.yview, style="Modern.Vertical.TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.body_text.configure(yscrollcommand=scrollbar.set)

        ttk.Label(parent, text="Gönderim günlüğü", style="Panel.TLabel", font=_fb(12)).grid(row=4, column=0, sticky="w")
        log_frame = ttk.Frame(parent, style="Panel.TFrame")
        log_frame.grid(row=5, column=0, sticky="nsew", pady=(8, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(
            log_frame,
            height=10,
            wrap="word",
            font=_fm(9),
            bg="#0f172a",
            fg="#dbeafe",
            insertbackground="#ffffff",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#1e293b",
            padx=12,
            pady=10,
            state="disabled",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview, style="Modern.Vertical.TScrollbar")
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)

    def _entry(self, parent, label, variable, row, show=None):
        ttk.Label(parent, text=label, style="Panel.TLabel").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(parent, textvariable=variable, show=show).grid(row=row, column=1, columnspan=2, sticky="ew", pady=6)

    def _file_row(self, parent, label, variable, row, filetypes):
        ttk.Label(parent, text=label, style="Panel.TLabel").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6, padx=(0, 8))
        self._button(parent, "Seç", lambda: self.choose_file(variable, filetypes), "ghost").grid(row=row, column=2, sticky="e", pady=6)

    def _spin(self, parent, label, variable, row, from_, to, increment=1):
        ttk.Label(parent, text=label, style="Panel.TLabel").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Spinbox(parent, textvariable=variable, from_=from_, to=to, increment=increment).grid(row=row, column=1, columnspan=2, sticky="ew", pady=6)

    def _portfolio_row(self, parent, row):
        ttk.Label(parent, text="Portfolyo ekleri", style="Panel.TLabel").grid(row=row, column=0, sticky="nw", pady=6)
        box = ttk.Frame(parent, style="Panel.TFrame")
        box.grid(row=row, column=1, columnspan=2, sticky="ew", pady=6)
        box.columnconfigure(0, weight=1)

        listbox = tk.Listbox(
            box,
            height=4,
            font=_fm(9),
            bg="#f8fafc",
            fg="#172033",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#d9e2ec",
            highlightcolor="#176b50",
            selectbackground="#176b50",
            selectforeground="#ffffff",
            activestyle="none",
            exportselection=False,
        )
        listbox.grid(row=0, column=0, sticky="ew")
        scroll = ttk.Scrollbar(box, orient="vertical", command=listbox.yview, style="Modern.Vertical.TScrollbar")
        scroll.grid(row=0, column=1, sticky="ns")
        listbox.configure(yscrollcommand=scroll.set)
        self.portfolio_listbox = listbox

        actions = ttk.Frame(box, style="Panel.TFrame")
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        self._button(actions, "PDF Ekle", self.add_portfolio_file, "ghost").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(actions, "Seçileni Sil", self.remove_portfolio_file, "ghost").grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._refresh_portfolio_list()

    def _refresh_portfolio_list(self):
        self.portfolio_listbox.delete(0, "end")
        for path in self.portfolio_files:
            self.portfolio_listbox.insert("end", os.path.basename(path) or path)

    def add_portfolio_file(self):
        filenames = filedialog.askopenfilenames(
            initialdir=BASE_DIR,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not filenames:
            return
        added = 0
        for path in filenames:
            if path not in self.portfolio_files:
                self.portfolio_files.append(path)
                added += 1
        if added:
            self._refresh_portfolio_list()
            self.log(f"Portfolyoya {added} dosya eklendi.")

    def remove_portfolio_file(self):
        selection = self.portfolio_listbox.curselection()
        if not selection:
            return
        for index in reversed(selection):
            del self.portfolio_files[index]
        self._refresh_portfolio_list()

    def choose_file(self, variable, filetypes):
        filename = filedialog.askopenfilename(initialdir=BASE_DIR, filetypes=filetypes)
        if filename:
            variable.set(filename)
            self.refresh_summary()

    def open_help_guide(self):
        guide = tk.Toplevel(self)
        guide.title("Nasıl Kullanılır?")
        guide.geometry("820x720")
        guide.minsize(680, 560)
        guide.configure(bg="#eef2f6")
        guide.transient(self)

        header = ttk.Frame(guide, padding=(18, 16, 18, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Nasıl Kullanılır?", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="İlk kullanım için adım adım kısa rehber", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        panel = ttk.Frame(guide, style="Panel.TFrame", padding=16)
        panel.pack(fill="both", expand=True, padx=18, pady=(10, 14))
        panel.rowconfigure(0, weight=1)
        panel.columnconfigure(0, weight=1)

        text = tk.Text(
            panel,
            wrap="word",
            font=_f(10),
            bg="#f8fafc",
            fg="#172033",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#d9e2ec",
            padx=14,
            pady=14,
        )
        text.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(panel, orient="vertical", command=text.yview, style="Modern.Vertical.TScrollbar")
        scroll.grid(row=0, column=1, sticky="ns")
        text.configure(yscrollcommand=scroll.set)

        guide_text = """Bulk Mail Dashboard Kullanım Rehberi

Bu uygulama, belirlediğin mail listesindeki adreslere Gmail hesabın üzerinden toplu mail göndermek için kullanılır. İlk kullanımda aşağıdaki adımları sırayla takip etmen yeterli.

1. Gmail bilgilerini gir

Sol taraftaki Gmail alanına gönderen mail adresini yaz.

Uygulama şifresi alanına Gmail uygulama şifreni gir. Bu normal Gmail şifren değildir. Google hesabında iki aşamalı doğrulama açık olmalı ve Gmail için bir uygulama şifresi oluşturmalısın.

Gmail App Password Nasıl Alınır?
Normal Gmail şifresi çalışmaz. Google'a özel bir App Password gereklidir.

myaccount.google.com → Güvenlik
2 Adımlı Doğrulama'yı etkinleştir
Arama kutusuna "App passwords" yaz → tıkla
Uygulama adı gir (örn. mail-script) → Create
Çıkan 16 haneli şifreyi uygulama şifresi kısmına koy.

2. Mail listesini seç

Mail listesi alanında alıcıların bulunduğu .txt dosyasını seç.

Dosyanın içinde her satırda bir mail adresi olması önerilir. Örnek:

ornek1@sirket.com
ornek2@sirket.com
ornek3@sirket.com

Listeyi seçtikten sonra üstteki Toplam mail kartından kaç geçerli mail okunduğunu görebilirsin.

3. Mail listesini uygulama içinden düzenle

Yeni mail adresleri bulduğunda dosyayı dışarıdan açmana gerek yok.

Mail Listesini Düzenle butonuna bas. Açılan pencerede mevcut .txt dosyasının içeriğini görebilir, yeni mailleri ekleyebilir veya eski satırları silebilirsin.

İşin bitince Kaydet ve Yenile butonuna bas. Uygulama aynı .txt dosyasını günceller ve toplam mail sayısını yeniden hesaplar.

4. CV dosyasını seç

CV eki alanından göndermek istediğin PDF dosyasını seç.

CV seçmezsen mail eki gönderilmez. Seçili PDF varsa her mailin ekine otomatik eklenir.

Portfolyo ekleri kısmından birden fazla PDF (portfolyo, sertifika, referans mektubu vb.) ekleyebilirsin. PDF Ekle butonu ile bir veya birden fazla dosya seçebilir, Seçileni Sil butonu ile listeden çıkarabilirsin. CV'den ayrı olarak bu dosyalar da her mailin ekine eklenir.

5. Konu ve mail içeriğini düzenle

Sağ taraftaki Konu alanına mail başlığını yaz.

Mail içeriği alanından göndermek istediğin metni düzenleyebilirsin. Buradaki metin tüm alıcılara aynı şekilde gönderilir.

6. Gönderim aralığını belirle

Başlangıç ve Bitiş alanları, listedeki hangi index aralığının gönderileceğini belirler.

Örnek:
Başlangıç 0, Bitiş 100 olursa listedeki 0 ile 99 arasındaki ilk 100 mail gönderilir.

Gönderim yarıda kalırsa Son index veya Limit indexi kartına bakarak bir sonraki denemede Başlangıç değerini kaldığın yerden devam edecek şekilde ayarlayabilirsin.

7. Gecikme süresini ayarla

Gecikme sn alanı, iki mail arasında kaç saniye bekleneceğini belirler.

Gmail sınırlarına daha yavaş yaklaşmak için 2 saniye veya daha yüksek bir değer kullanmak daha sağlıklıdır.

8. Ayarları kaydet

Her şeyi hazırladıktan sonra Ayarları Kaydet butonuna bas.

Böylece uygulamayı kapatıp açtığında aynı ayarlar tekrar gelir.

9. Gönderimi başlat

Gönderimi Başlat butonuna basınca uygulama Gmail'e bağlanır ve seçilen aralıktaki mailleri göndermeye başlar.

Sağ alttaki Gönderim günlüğü bölümünden hangi adrese mail gittiğini, hata olup olmadığını ve o an hangi indexte olduğunu takip edebilirsin.

10. Gönderimi durdur

Gönderimi durdurmak istersen Durdur butonuna bas.

Uygulama mevcut işlemi durdurur. Son index kartından en son hangi indexte kaldığını görebilirsin.

11. Gmail limitine ulaşırsan

Gmail günlük gönderim sınırı veya rate limit hatası dönerse uygulama bunu algılamaya çalışır ve gönderimi durdurur.

Bu durumda Limit indexi kartında kaldığın index görünür. Daha sonra devam etmek istersen Başlangıç değerini bu indexe veya bir sonraki indexe göre ayarlayabilirsin.

Kısa kontrol listesi

Gmail adresi doğru mu?
Uygulama şifresi doğru mu?
Mail listesi seçili mi?
CV dosyası doğru mu?
Konu ve içerik hazır mı?
Başlangıç ve Bitiş aralığı doğru mu?
Ayarları Kaydet butonuna bastın mı?

Hazırsan Gönderimi Başlat butonuna basabilirsin."""

        text.insert("1.0", guide_text)
        text.configure(state="disabled")

        footer = ttk.Frame(guide, padding=(18, 0, 18, 18))
        footer.pack(fill="x")
        self._button(footer, "Kapat", guide.destroy, "primary").pack(side="right")

    def open_list_editor(self):
        path = self.list_file.get().strip()
        if not path:
            messagebox.showerror("Liste yok", "Önce bir mail listesi dosyası seçmelisin.")
            return

        list_path = Path(path)
        if not list_path.exists():
            create = messagebox.askyesno("Dosya bulunamadı", "Seçili liste dosyası yok. Bu isimle yeni dosya oluşturulsun mu?")
            if not create:
                return
            list_path.write_text("", encoding="utf-8")

        editor = tk.Toplevel(self)
        editor.title("Mail Listesini Düzenle")
        editor.geometry("760x640")
        editor.minsize(640, 520)
        editor.configure(bg="#eef2f6")
        editor.transient(self)

        header = ttk.Frame(editor, padding=(16, 14, 16, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Mail Listesini Düzenle", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text=str(list_path), style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        body = ttk.Frame(editor, style="Panel.TFrame", padding=14)
        body.pack(fill="both", expand=True, padx=16, pady=(8, 12))
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)

        text = tk.Text(
            body,
            wrap="none",
            font=_fm(10),
            bg="#f8fafc",
            fg="#172033",
            insertbackground="#176b50",
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#d9e2ec",
            highlightcolor="#176b50",
            padx=12,
            pady=12,
        )
        text.grid(row=0, column=0, sticky="nsew")
        text.insert("1.0", list_path.read_text(encoding="utf-8"))

        y_scroll = ttk.Scrollbar(body, orient="vertical", command=text.yview, style="Modern.Vertical.TScrollbar")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(body, orient="horizontal", command=text.xview, style="Modern.Horizontal.TScrollbar")
        x_scroll.grid(row=1, column=0, sticky="ew")
        text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        footer = ttk.Frame(editor, padding=(16, 0, 16, 16))
        footer.pack(fill="x")
        count_var = tk.StringVar()

        def update_count():
            lines = [line.strip() for line in text.get("1.0", "end").splitlines()]
            count = len([line for line in lines if line and "@" in line])
            count_var.set(f"Geçerli mail sayısı: {count}")

        def save_list():
            content = text.get("1.0", "end-1c")
            list_path.write_text(content, encoding="utf-8")
            self.refresh_summary()
            update_count()
            self.log("Mail listesi güncellendi.")

        ttk.Label(footer, textvariable=count_var, style="Subtitle.TLabel").pack(side="left")
        self._button(footer, "Kaydet ve Yenile", save_list, "primary").pack(side="right", padx=(8, 0))
        self._button(footer, "Kapat", editor.destroy, "ghost").pack(side="right")

        text.bind("<KeyRelease>", lambda _event: update_count())
        update_count()

    def collect_settings(self):
        return {
            "sender_email": self.sender_email.get().strip(),
            "app_password": self.app_password.get().strip(),
            "subject": self.subject.get().strip(),
            "body": self.body_text.get("1.0", "end").strip(),
            "list_file": self.list_file.get().strip(),
            "cv_file": self.cv_file.get().strip(),
            "portfolio_files": list(self.portfolio_files),
            "start_index": int(self.start_index.get()),
            "end_index": int(self.end_index.get()),
            "delay_seconds": float(self.delay_seconds.get()),
        }

    def save_current_settings(self):
        try:
            save_settings(self.collect_settings())
            self.log("Ayarlar kaydedildi.")
        except Exception as exc:
            messagebox.showerror("Kaydedilemedi", str(exc))

    def refresh_summary(self):
        try:
            recipients = read_recipients(self.list_file.get())
            start = max(0, int(self.start_index.get()))
            end = min(len(recipients), int(self.end_index.get()))
            target = max(0, end - start)
            self.total_count.set(str(len(recipients)))
            self.target_count.set(str(target))
            if not (self.worker and self.worker.is_alive()):
                self.status_text.set("Hazır")
        except Exception as exc:
            self.total_count.set("0")
            self.target_count.set("0")
            if not (self.worker and self.worker.is_alive()):
                self.status_text.set(f"Liste okunamadı: {exc}")

    def validate_job(self, settings):
        if not settings["sender_email"]:
            raise ValueError("Gmail alanı boş olamaz.")
        if not settings["app_password"]:
            raise ValueError("Uygulama şifresi boş olamaz.")
        if not settings["subject"]:
            raise ValueError("Konu boş olamaz.")
        if not settings["body"]:
            raise ValueError("Mail içeriği boş olamaz.")
        if not os.path.exists(settings["list_file"]):
            raise ValueError("Mail listesi bulunamadı.")
        recipients = read_recipients(settings["list_file"])
        if not recipients:
            raise ValueError("Mail listesi boş veya geçerli adres içermiyor.")
        if settings["start_index"] >= len(recipients):
            raise ValueError(f"Başlangıç indeksi ({settings['start_index']}) liste boyutunu aşıyor ({len(recipients)} kayıt).")
        if settings["cv_file"] and not os.path.exists(settings["cv_file"]):
            raise ValueError("CV dosyası bulunamadı.")
        for path in settings.get("portfolio_files") or []:
            if not os.path.exists(path):
                raise ValueError(f"Portfolyo dosyası bulunamadı: {path}")
        if settings["start_index"] < 0 or settings["end_index"] <= settings["start_index"]:
            raise ValueError("Başlangıç ve bitiş aralığı geçersiz.")

    def start_sending(self):
        self.send_button.configure(state="disabled")
        if self.worker and self.worker.is_alive():
            return
        try:
            settings = self.collect_settings()
            self.validate_job(settings)
            job = MailJob(**settings)
        except Exception as exc:
            messagebox.showerror("Başlatılamadı", str(exc))
            self.send_button.configure(state="normal")
            return

        self.stop_event.clear()
        self.sent_count.set("0")
        self.failed_count.set("0")
        self.last_index.set("-")
        self.limit_index.set("-")
        self.progress_value.set(0)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_text.set("Gönderim başladı")

        self.worker = threading.Thread(target=self.send_worker, args=(job,), daemon=True)
        self.worker.start()

    def stop_sending(self):
        self.stop_event.set()
        self.status_text.set("Durdurma isteniyor...")

    def send_worker(self, job):
        sent = 0
        failed = 0
        limit_reached = False
        try:
            recipients = read_recipients(job.list_file)
            targets = recipients[job.start_index:job.end_index]
            total = len(targets)
            self.ui(lambda: self.target_count.set(str(total)))
            self.ui(lambda: self.log(f"Gönderilecek mail: {total} ({job.start_index}-{job.end_index})"))

            if total == 0:
                self.ui(lambda: self.update_progress(100, 0, 0, job.start_index))
                self.ui(lambda: self.log("Gönderilecek mail yok. Başlangıç indeksini kontrol edin."))
                return

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(job.sender_email, job.app_password)
                for index, recipient in enumerate(targets, 1):
                    absolute_index = job.start_index + index - 1
                    if self.stop_event.is_set():
                        self.ui(lambda: self.log("Gönderim kullanıcı tarafından durduruldu."))
                        break
                    try:
                        server.sendmail(job.sender_email, recipient, create_message(job, recipient).as_string())
                        sent += 1
                        self.ui(lambda r=recipient, i=index, a=absolute_index: self.log(f"[{i}/{total}] OK  index {a}  {r}"))
                    except Exception as exc:
                        failed += 1
                        self.ui(lambda r=recipient, i=index, a=absolute_index, e=exc: self.log(f"[{i}/{total}] HATA  index {a}  {r} -> {e}"))
                        if is_limit_error(exc):
                            limit_reached = True
                            self.ui(lambda a=absolute_index: self.limit_index.set(str(a)))
                            self.ui(lambda a=absolute_index: self.status_text.set(f"Limit algılandı: index {a}"))
                            self.ui(lambda a=absolute_index: self.log(f"Mail gönderim limiti algılandı. Kalınan index: {a}"))
                            self.stop_event.set()

                    progress = (index / total * 100) if total else 100
                    self.ui(lambda p=progress, s=sent, f=failed, a=absolute_index: self.update_progress(p, s, f, a))
                    if self.stop_event.is_set():
                        break
                    if index < total and job.delay_seconds > 0:
                        self.stop_event.wait(job.delay_seconds)

            if limit_reached:
                self.ui(lambda: self.status_text.set("Limit nedeniyle durdu"))
            else:
                self.ui(lambda: self.status_text.set("Tamamlandı" if not self.stop_event.is_set() else "Durduruldu"))

            if sent > 0:
                try:
                    persisted = load_settings()
                    persisted["start_index"] = job.start_index + sent
                    save_settings(persisted)
                except Exception:
                    pass
        except Exception as exc:
            self.ui(lambda e=exc: messagebox.showerror("Gönderim hatası", str(e)))
            self.ui(lambda e=exc: self.status_text.set(f"Hata: {e}"))
        finally:
            self.ui(self.finish_worker)

    def update_progress(self, progress, sent, failed, absolute_index=None):
        self.progress_value.set(progress)
        self.sent_count.set(str(sent))
        self.failed_count.set(str(failed))
        if absolute_index is not None:
            self.last_index.set(str(absolute_index))

    def finish_worker(self):
        final_status = self.status_text.get()
        self.send_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.refresh_summary()
        if final_status and final_status != "Hazır":
            self.status_text.set(final_status)

    def ui(self, callback):
        self.after(0, callback)

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{timestamp}  {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


if __name__ == "__main__":
    app = BulkMailDashboard()
    app.mainloop()
