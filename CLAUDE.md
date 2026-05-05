# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A single-file Python script (`mail_gonder.py`) for sending batch internship application emails with a CV attachment to Turkish company HR contacts. Uses only Python's standard library — no dependencies to install.

## Running the Script

```bash
python mail_gonder.py
```

## Architecture

All logic lives in `mail_gonder.py` with three functions:

- `emailleri_oku()` — reads `liste.txt`, filters lines containing `@`
- `mail_olustur(alici)` — builds a MIME multipart email with a plain-text bilingual body and optional PDF attachment
- `gonder()` — authenticates to Gmail via SMTP_SSL, iterates the recipient slice `[BASLANGIC:BITIS]` with a per-email delay, handles per-email exceptions

**Data files:**
- `liste.txt` — 781 recipient email addresses (one per line)
- `BarisTunaTugrul-CV.pdf` — attached to every email

## Configuration (top of `mail_gonder.py`, lines ~10–60)

All settings are hardcoded constants:

| Variable | Purpose |
|---|---|
| `GONDEREN_EMAIL` | Sender Gmail address |
| `GMAIL_APP_SIFRE` | Gmail App Password (not account password) |
| `KONU` | Email subject line |
| `ICERIK` | Bilingual email body (English + Turkish) |
| `LISTE_DOSYASI` | Path to recipient list file |
| `CV_DOSYASI` | Path to PDF attachment |
| `BASLANGIC` / `BITIS` | Slice indices for resumable batch sending |
| `GECIKME_SN` | Seconds to wait between sends (default: 2) |

## Batch Processing

The script sends `liste[BASLANGIC:BITIS]`. Split across multiple runs to stay within Gmail's daily send limit (≈500/day):
- Run 1: `BASLANGIC=0`, `BITIS=400`
- Run 2: `BASLANGIC=400`, `BITIS=782`

## Gmail Setup Requirement

Requires a Gmail **App Password** (not the account password). Generate one at Google Account → Security → 2-Step Verification → App passwords. The script connects to `smtp.gmail.com:465` with SSL.
