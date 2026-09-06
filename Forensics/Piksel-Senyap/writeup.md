# Piksel Senyap

- **Kategori:** Digital Forensics (Eliminasi)
- **Poin:** 317 PTS (17 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **File Soal:** `piksel_senyap.png`
- **Flag:** `TechtonicExpoCTF{lsb_tersembunyi_D35D4ECD}`

---

## Deskripsi Soal

> Selembar gambar yang sekilas hanya derau warna, seperti saluran televisi yang kehilangan sinyal. Di balik setiap piksel ada cerita, tapi tidak semua lapisan menceritakan hal yang sama. Sebagian lapisan sengaja berbohong, sebagian baru bicara setelah cara pandang digeser. Jangan berhenti di permukaan yang paling mudah terlihat, karena lapisan yang paling ramai bicara sering kali paling banyak menutupi.

---

## Analisis Petunjuk & Investigasi

Deskripsi soal memuat serangkaian petunjuk steganografi/forensik visual yang jelas:
1. *"tidak semua lapisan menceritakan hal yang sama"* $\implies$ Analisis 24 *bit plane* (8-bit R, 8-bit G, 8-bit B).
2. *"Sebagian lapisan sengaja berbohong"* $\implies$ Terdapat *decoy* / jebakan teks palsu pada lapisan yang umum dicek pertama kali.
3. *"sebagian baru bicara setelah cara pandang digeser"* $\implies$ Informasi asli berada di bit plane yang digeser (bukan LSB bit 0 biasa, melainkan bit 1).
4. *"Jangan berhenti di permukaan yang paling mudah terlihat"* $\implies$ LSB bit 0 yang tampak seperti target utama ternyata berisi jebakan.

---

## Langkah Analisis

### 1. Menemukan Lapisan Jebakan (Decoy di Red Bit 0)
Mengekstrak data bit 0 dari kanal Red secara berurutan:
```python
r_bit0 = [(p[0] & 1) for p in pixels]
```
Ditemukan teks berulang:
```text
kunci_salah_arah_2026kunci_salah_arah_2026...
```
Sesuai dengan petunjuk *"sebagian lapisan sengaja berbohong"*, teks ini adalah kunci palsu (*false flag*).

---

### 2. Analisis Distribusi Seluruh Bit Plane
Dilakukan kalkulasi persentase bit 1 dan entropi kompresi pada seluruh 24 bit plane:
- 23 bit plane menunjukkan distribusi ~50.0% (derau murni / random) dengan ukuran kompresi rata-rata ~56–57 KB.
- **Kanal Blue bit 1** menunjukkan distribusi berbeda: **44.09% bit 1** dengan ukuran kompresi hanya **49 KB**.

---

### 3. Ekstraksi Visual Blue Bit Plane 1
Mengekstrak bit ke-1 dari kanal warna Biru (`(B >> 1) & 1`):

```python
b_bit1 = [((p[2] >> 1) & 1) * 255 for p in pixels]
plane_img = Image.new('L', (512, 512))
plane_img.putdata(b_bit1)
plane_img.save('blue_bit_1.png')
```

Pada koordinat baris $y = 228 \dots 276$, tampak teks visual yang sangat jelas:

```text
l s b _ t e r s e m b u n y i
```

Kunci yang ditemukan:
$$\mathbf{lsb\_tersembunyi}$$

---

## Script Penyelesaian (`solve.py`)

```python
import os
from PIL import Image

img_path = r"C:\Users\User\Downloads\piksel_senyap.png"
team_code = "D35D4ECD"

im = Image.open(img_path)
pixels = list(im.getdata())

# 1. Ekstraksi Red bit 0 (Decoy)
r_bit0 = [(p[0] & 1) for p in pixels]
r_bytes = bytearray()
for i in range(0, len(r_bit0), 8):
  byte = 0
  for b in r_bit0[i : i + 8]:
    byte = (byte << 1) | b
  r_bytes.append(byte)
print(f"[*] Decoy: {r_bytes[:21].decode('ascii', errors='ignore')}")

# 2. Ekstraksi Blue bit 1 (Asli)
b_bit1 = [((p[2] >> 1) & 1) * 255 for p in pixels]
plane_img = Image.new("L", im.size)
plane_img.putdata(b_bit1)
plane_img.save("blue_bit_1.png")

kunci = "lsb_tersembunyi"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
print(f"[+] Flag: {flag}")
```

---

## Flag

```text
TechtonicExpoCTF{lsb_tersembunyi_D35D4ECD}
```
