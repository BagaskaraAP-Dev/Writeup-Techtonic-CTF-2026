# Ganda di Belakang

- **Kategori:** Digital Forensics (Eliminasi)
- **Poin:** 498 PTS (16 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **File Soal:** `ganda_dibelakang.png`
- **Flag:** `TechtonicExpoCTF{zip_menempel_D35D4ECD}`

---

## Deskripsi Soal

> Gambar yang terlihat seperti tanda peringatan, tapi di baliknya menempel sesuatu yang tidak terlihat sekilas. Setiap berkas punya akhir, dan akhir itu bukan selalu akhir. Yang menempel itu terkunci, dan kuncinya ditinggalkan di dalam gambar itu sendiri dengan cara yang tidak kasat mata. Buka lapisan demi lapisan, ikuti jejak yang tersembunyi di antara tumpukan.

---

## Analisis Petunjuk

Petunjuk deskripsi mengarahkan pada struktur file beruntun (*nested file carving*):
1. *"Setiap berkas punya akhir, dan akhir itu bukan selalu akhir"* $\implies$ Terdapat data tambahan yang menempel di belakang penutup berkas PNG (setelah chunk `IEND`).
2. *"Yang menempel itu terkunci, dan kuncinya ditinggalkan di dalam gambar itu sendiri dengan cara yang tidak kasat mata"* $\implies$ Data yang menempel adalah arsip terenkripsi (ZIP), dan password enkripsinya tersimpan di metadata PNG (`tEXt` chunk).
3. *"Buka lapisan demi lapisan, ikuti jejak yang tersembunyi di antara tumpukan"* $\implies$ Struktur berkas berlapis (*nested ZIP in ZIP*).

---

## Langkah Investigasi

### 1. Menemukan Password di Metadata PNG (`tEXt` Chunk)
Pemeriksaan chunk PNG mengungkapkan chunk metadata `tEXt`:
- Keyword: `pesan`
- Nilai: `cGludHUyMDI2`
- Decode Base64:
  $$\text{cGludHUyMDI2} \implies \mathbf{pintu2026}$$

Terdapat pula petunjuk kedua di chunk `tEXt` lain:
> *petunjuk: pintu di balik kata sandi yang tak terlihat*

---

### 2. Ekstraksi Trailing Data (Layer 1: Locked ZIP)
Setelah marker akhir PNG `IEND` (offset `17573`), ditemukan header arsip ZIP (`PK\x03\x04`).
Arsip ini terenkripsi dengan password.
- Password: `pintu2026`
- Berkas di dalamnya: `arsip.zip`

---

### 3. Ekstraksi `arsip.zip` (Layer 2)
Mengekstrak `arsip.zip` menghasilkan 2 berkas:
1. `catatan.txt`:
   > *"kamu mencari kunci yang salah, coba lagi dari awal"* *(Pesan jebakan / Decoy)*
2. `tanda.bin`

---

### 4. Analisis & Ekstraksi `tanda.bin` (Layer 3)
Memeriksa *magic byte* dari berkas `tanda.bin`:
- `tanda.bin` berawalan `50 4B 03 04` (`PK\x03\x04`), yang artinya berkas ini adalah arsip ZIP yang disamarkan namanya.
- Membuka `tanda.bin` sebagai ZIP menghasilkan satu berkas:
  $$\mathbf{kunci.txt}$$
- Isi dari `kunci.txt`:
  ```text
  zip_menempel
  ```

---

## Script Penyelesaian (`solve.py`)

```python
import base64
import io
import zipfile

img_path = r"C:\Users\User\Downloads\ganda_dibelakang.png"
team_code = "D35D4ECD"

with open(img_path, "rb") as f:
  data = f.read()

# 1. Password dari metadata tEXt
pesan_pos = data.find(b"tEXtpesan\x00")
b64_pass = data[pesan_pos + 10 : pesan_pos + 22].decode("ascii")
password = base64.b64decode(b64_pass).decode("ascii")  # 'pintu2026'

# 2. Ekstrak Layer 1 (Trailing ZIP)
iend_pos = data.find(b"IEND") + 8
zip_data = data[iend_pos:]
zf1 = zipfile.ZipFile(io.BytesIO(zip_data))
arsip_zip_bytes = zf1.read("arsip.zip", pwd=password.encode("ascii"))

# 3. Ekstrak Layer 2 (arsip.zip)
zf2 = zipfile.ZipFile(io.BytesIO(arsip_zip_bytes))
tanda_bytes = zf2.read("tanda.bin")

# 4. Ekstrak Layer 3 (tanda.bin sebagai ZIP)
zf3 = zipfile.ZipFile(io.BytesIO(tanda_bytes))
kunci = zf3.read("kunci.txt").decode("utf-8").strip()

flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
print(f"[+] Kunci : {kunci}")
print(f"[+] Flag  : {flag}")
```

---

## Flag

```text
TechtonicExpoCTF{zip_menempel_D35D4ECD}
```
