# Jejak Metadata

- **Kategori:** Digital Forensics (Eliminasi)
- **Poin:** 337 PTS (12 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **File Soal:** `foto_jejak.jpg`
- **Flag:** `TechtonicExpoCTF{meta_tersimpan_D35D4ECD}`

---

## Deskripsi Soal

> Sebuah foto yang seolah hanya pemandangan biasa, tapi pembuatnya meninggalkan terlalu banyak catatan di tempat yang tidak terlihat.
>
> Catatan yang paling mencolok justru paling menyesatkan. Ada yang tersimpan sebagai teks, ada yang menyamar sebagai data tanpa nama. Baca setiap bagian kecil berkas ini sampai tidak ada yang tersisa, lalu rangkai apa yang saling bersambung.

---

## Analisis & Investigasi Forensik

Petunjuk pada soal memuat pemetaan yang presisi terhadap struktur internal berkas JPEG:

1. *"Catatan yang paling mencolok justru paling menyesatkan"*
   - Pada EXIF metadata tag `ImageDescription` (tag `0x010e`), terdapat teks:
     ```text
     kunci_sesungguhnya_ada_disini
     ```
   - Sesuai peringatan soal, ini adalah *decoy / false flag*.

2. *"Ada yang menyamar sebagai data tanpa nama"*
   - Pada JPEG, segmen marker `COM` (`\xff\xfe`) tidak memiliki pengenal nama standar (berbeda dengan `APP0 JFIF` atau `APP1 Exif`).
   - Di dalam segmen `COM`, tersimpan string base64:
     ```text
     bWV0YV8=
     ```
   - Hasil decode base64:
     $$\text{bWV0YV8=} \implies \mathbf{meta\_}$$
     *(Perhatikan akhiran tanda garis bawah `_` yang menunjukkan kata ini adalah awalan yang bersambung).*

3. *"Ada yang tersimpan sebagai teks"*
   - Pada tag EXIF `UserComment` (tag `0x9286`), tersimpan teks:
     $$\mathbf{tersimpan}$$

4. *"lalu rangkai apa yang saling bersambung"*
   - Menggabungkan kedua bagian yang saling bersambung:
     $$\text{meta\_} + \text{tersimpan} = \mathbf{meta\_tersimpan}$$

---

## Script Penyelesaian (`solve.py`)

```python
import base64
import struct

img_path = r"C:\Users\User\Downloads\foto_jejak.jpg"
team_code = "D35D4ECD"

with open(img_path, "rb") as f:
  data = f.read()

# 1. Ekstrak data COM marker (Base64)
com_pos = data.find(b"\xff\xfe")
com_len = struct.unpack(">H", data[com_pos + 2 : com_pos + 4])[0]
com_data = data[com_pos + 4 : com_pos + 2 + com_len]
kata_awalan = base64.b64decode(com_data).decode("ascii")  # 'meta_'

# 2. Ekstrak EXIF UserComment
kata_akhiran = "tersimpan"

# 3. Rangkai
kunci = f"{kata_awalan}{kata_akhiran}"  # 'meta_tersimpan'
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print(f"[+] Kunci : {kunci}")
print(f"[+] Flag  : {flag}")
```

---

## Flag

```text
TechtonicExpoCTF{meta_tersimpan_D35D4ECD}
```
