# 🏴 Writeup — TechtonicExpo CTF 2026

Kumpulan writeup **TechtonicExpo CTF 2026**, diselenggarakan oleh **Himpunan Mahasiswa Teknik Informatika (HMTI) — Universitas Bangka Belitung**.

- **Event:** TechtonicExpo CTF 2026
- **Penyelenggara:** HMTI Universitas Bangka Belitung
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **Author:** Bagaskara Amukti Palapa ([@BagaskaraAP-Dev](https://github.com/BagaskaraAP-Dev))

> Tiap soal punya folder sendiri berisi `writeup.md`, script solver (`solve.py`), dan file soal aslinya.

---

## 📊 Ringkasan

| Kategori | Jumlah Soal | Total Poin |
|----------|:-----------:|:----------:|
| [Crypto](#-cryptography) | 5 | 2494 |
| [Forensics](#-digital-forensics) | 4 | 1707 |
| [Pwn](#-binary-exploitation-pwn) | 1 | 591 |
| [Web](#-web-exploitation) | 5 | 3022 |
| **Total** | **15** | **7814** |

---

## 🔐 Cryptography

| # | Soal | Poin (Solves) | Teknik | Flag |
|---|------|:-------------:|--------|------|
| 1 | [Tabung Tembaga](./Crypto/Tabung-Tembaga/writeup.md) | 522 (12) | Franklin–Reiter Related Message (RSA, e=3) | `TechtonicExpoCTF{kembar_terkait_D35D4ECD}` |
| 2 | [Generator Nakal](./Crypto/Generator-Nakal/writeup.md) | 565 (7) | LCG parameter recovery | `TechtonicExpoCTF{ramal_lcg_nakal_D35D4ECD}` |
| 3 | [Bisikan Orator](./Crypto/Bisikan-Orator/writeup.md) | 368 (7) | Padding Oracle Attack (CBC / PKCS#7) | `TechtonicExpoCTF{bisikan_bocor_bisikan_bocor_D35D4ECD}` |
| 4 | [Lilitan Siput](./Crypto/Lilitan-Siput/writeup.md) | 412 (3) | Vigenère + Columnar Transposition | `TechtonicExpoCTF{lilit_putar_dua_D35D4ECD}` |
| 5 | [Kubah Terbalik](./Crypto/Kubah-Terbalik/writeup.md) | 627 (3) | CBC Bit-Flip + SHA-256 Length Extension | `TechtonicExpoCTF{balik_ulur_panjang_D35D4ECD}` |

## 🔎 Digital Forensics

| # | Soal | Poin (Solves) | Teknik | Flag |
|---|------|:-------------:|--------|------|
| 1 | [Gelombang Berbicara](./Forensics/Gelombang-Berbicara/writeup.md) | 555 (8) | Audio spectrogram stego (HF/LF) | `TechtonicExpoCTF{spektrum_visual_D35D4ECD}` |
| 2 | [Ganda di Belakang](./Forensics/Ganda-di-Belakang/writeup.md) | 498 (16) | Appended ZIP / trailing data | `TechtonicExpoCTF{zip_menempel_D35D4ECD}` |
| 3 | [Jejak Metadata](./Forensics/Jejak-Metadata/writeup.md) | 337 (12) | EXIF metadata disclosure | `TechtonicExpoCTF{meta_tersimpan_D35D4ECD}` |
| 4 | [Piksel Senyap](./Forensics/Piksel-Senyap/writeup.md) | 317 (17) | LSB / bit-plane steganography | `TechtonicExpoCTF{lsb_tersembunyi_D35D4ECD}` |

## 💥 Binary Exploitation (Pwn)

| # | Soal | Poin (Solves) | Teknik | Flag |
|---|------|:-------------:|--------|------|
| 1 | [Canary Malas](./Pwn/Canary-Malas/writeup.md) | 591 (5) | Timing side-channel canary brute + PIE leak + ret2win | `TechtonicExpoCTF{tebak_satu_D35D4ECD}` |

> ℹ️ Berkas soal [`Trailing`](./Pwn/Trailing/) turut disertakan tetapi belum ada writeup-nya — lihat [catatannya](./Pwn/Trailing/README.md).

## 🌐 Web Exploitation

| # | Soal | Poin (Solves) | Teknik | Flag |
|---|------|:-------------:|--------|------|
| 1 | [Kurir Buta](./Web/Kurir-Buta/writeup.md) | 750 | SSRF (bypass filter host) | `TechtonicExpoCTF{jalur_dalam_buta_D35D4ECD}` |
| 2 | [Pabrik Lembaran](./Web/Pabrik-Lembaran/writeup.md) | 750 | Server-Side Template Injection (SSTI) | `TechtonicExpoCTF{cetak_dari_dalam_D35D4ECD}` |
| 3 | [Arsip Tanpa Tanda](./Web/Arsip-Tanpa-Tanda/writeup.md) | 689 (1) | JWT forgery (secret disclosure) | `TechtonicExpoCTF{tanda_tanpa_sah_D35D4ECD}` |
| 4 | [Gerbang Legiun](./Web/Gerbang-Legiun/writeup.md) | 456 (1) | SQL Injection (case-filter bypass) | `TechtonicExpoCTF{dua_titik_suntik_D35D4ECD}` |
| 5 | [Eko-Sistem Pencatatan](./Web/Eko-Sistem-Pencatatan/writeup.md) | 377 (6) | Recon / Info Disclosure / Cookie | `TechtonicExpoCTF{empat_kanal_benteng_D35D4ECD}` |

---

## 🗂️ Struktur Repo

```
Writeup-Techtonic-CTF-2026/
├── Crypto/       # 5 soal — tiap folder: writeup.md + solve.py
├── Forensics/    # 4 soal — writeup.md + solve.py + file soal
├── Pwn/          # Canary-Malas (+ Trailing: binary tanpa writeup)
└── Web/          # 5 soal — writeup.md per folder
```

---

_Dibuat oleh **Bagaskara Amukti Palapa** — TechtonicExpo CTF 2026 (HMTI Universitas Bangka Belitung)._
