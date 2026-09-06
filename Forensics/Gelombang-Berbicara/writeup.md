# Gelombang Berbicara

- **Kategori:** Digital Forensics (Eliminasi)
- **Poin:** 555 PTS (8 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **File Soal:** `gelombang_bicara.wav`
- **Flag:** `TechtonicExpoCTF{spektrum_visual_D35D4ECD}`

---

## Deskripsi Soal

> Suara yang kelihatannya hanya desisan dan dengung. Tapi di dalamnya ada gambar yang tidak terlihat oleh telinga, dan ada pesan yang berbisik terlalu tinggi untuk didengar biasa. Dengarkan dengan mata, dan lihat dengan telinga. Dua lapisan harus disatukan, masing-masing berada di ujung frekuensi yang berbeda.

---

## Analisis Petunjuk & Investigasi Forensik

Petunjuk deskripsi mengarahkan pada dua teknik steganografi audio pada domain frekuensi (spektrogram):
1. *"di dalamnya ada gambar yang tidak terlihat oleh telinga"* $\implies$ Teks/gambar visual yang disisipkan ke dalam spektrogram audio.
2. *"ada pesan yang berbisik terlalu tinggi untuk didengar biasa"* $\implies$ Sinyal kode Morse pada frekuensi ultrasonik tinggi (~18.000 Hz).
3. *"Dua lapisan harus disatukan, masing-masing berada di ujung frekuensi yang berbeda"* $\implies$ Menggabungkan kata yang ditemukan di frekuensi rendah dan kata dari frekuensi tinggi:
   $$\text{Kunci} = \text{kata\_rendah} + \text{"\_"} + \text{kata\_tinggi}$$

---

## Langkah Penyelesaian

### 1. Ekstraksi Spektrogram Frekuensi Rendah (0 – 4.000 Hz)
Pada rentang frekuensi 1.000 Hz hingga 3.000 Hz pada detik ke-1 s/d 4, spektrogram menampilkan tulisan teks:
```text
s p e k t r u m
```
Kata pertama:
$$\mathbf{spektrum}$$

---

### 2. Ekstraksi Kode Morse Frekuensi Tinggi (~18.000 Hz)
Pada frekuensi ~18.000 Hz (di luar pendengaran umum manusia), terdapat gelombang nada diskrit yang termodulasi (*on-off keying*) membentuk pola kode Morse:

```text
...-   ..   ...   ..-   .-   .-..
```

Translasi kode Morse:
- `...-` $\implies$ **V**
- `..` $\implies$ **I**
- `...` $\implies$ **S**
- `..-` $\implies$ **U**
- `.-` $\implies$ **A**
- `.-..` $\implies$ **L**

Kata kedua:
$$\mathbf{visual}$$

---

### 3. Penggabungan Kata Kunci & Flag
Menggabungkan kedua kata dari ujung frekuensi rendah dan tinggi:
$$\text{Kunci} = \mathbf{spektrum\_visual}$$

Format flag: `TechtonicExpoCTF{kunci_KODETIM}`
$$\implies \mathbf{TechtonicExpoCTF\{spektrum\_visual\_D35D4ECD\}}$$

*(Opsi urutan terbalik: `TechtonicExpoCTF{visual_spektrum_D35D4ECD}`)*

---

## Script Eksploitasi (`solve.py`)

```python
import os
import wave
import numpy as np
from PIL import Image

wav_path = r"C:\Users\User\Downloads\gelombang_bicara.wav"
team_code = "D35D4ECD"

with wave.open(wav_path, "rb") as w:
  rate = w.getframerate()
  audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(
      np.float32
  )

# STFT Analysis
n_fft = 1024
hop_length = 256
window = np.hanning(n_fft)
num_frames = (len(audio) - n_fft) // hop_length

spectrogram = []
for i in range(num_frames):
  segment = audio[i * hop_length : i * hop_length + n_fft] * window
  spectrogram.append(np.abs(np.fft.rfft(segment)))

spec_matrix = np.array(spectrogram).T

# 1. Kata di Frekuensi Rendah
kata_rendah = "spektrum"

# 2. Decode Morse di Frekuensi Tinggi (~18000 Hz)
high_bin = int(18000 / (rate / 2) * 513)
sig = spec_matrix[high_bin - 3 : high_bin + 4, :].mean(axis=0)
thresh = (np.percentile(sig, 20) + np.percentile(sig, 98)) / 2
binary = (sig > thresh).astype(int)

runs = []
curr_val, curr_len = binary[0], 0
for b in binary:
  if b == curr_val:
    curr_len += 1
  else:
    runs.append((curr_val, curr_len))
    curr_val, curr_len = b, 1
runs.append((curr_val, curr_len))

MORSE_DICT = {
    "...-": "V",
    "..": "I",
    "...": "S",
    "..-": "U",
    ".-": "A",
    ".-..": "L",
}
morse_letters, cur = [], ""
for val, length in runs:
  if val == 1 and length >= 5:
    cur += "-" if length > 30 else "."
  elif val == 0 and length > 35 and cur:
    morse_letters.append(cur)
    cur = ""
if cur:
  morse_letters.append(cur)

kata_tinggi = "".join(MORSE_DICT.get(m, "?") for m in morse_letters).lower()
# Hasil: 'visual'

# 3. Gabungkan Flag
kunci = f"{kata_rendah}_{kata_tinggi}"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
print(f"[+] Kunci : {kunci}")
print(f"[+] Flag  : {flag}")
```

---

## Flag

```text
TechtonicExpoCTF{spektrum_visual_D35D4ECD}
```
