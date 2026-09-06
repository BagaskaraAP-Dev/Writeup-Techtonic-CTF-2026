# Kubah Terbalik

- **Kategori:** Cryptography
- **Poin:** 627 PTS (3 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **Target URL:** `http://168.110.219.59:5016/`
- **Flag:** `TechtonicExpoCTF{balik_ulur_panjang_D35D4ECD}`

---

## Deskripsi Soal

> Dua pintu berlapis. Pintu pertama dikunci kartu terenkripsi yang rantainya saling memengaruhi. Mengubah satu kotak di depan akan mengubah isi di belakangnya. Ubah satu angka di kartu, dan peranmu berubah.
>
> Pintu kedua dijaga tanda tangan yang dibuat dari rahasia pendek yang disambung di depan data, lalu dicincang. Tanda itu bisa diulur tanpa tahu rahasianya, selama kamu paham cara cincang bekerja.
>
> Kedua lapis memberi separuh kata kunci.

---

## Analisis & Konsep Eksploitasi

Tantangan ini terdiri dari 2 pintu/lapis yang masing-masing menggunakan kerentanan kriptografi klasik:

1. **Lapis 1 (Pintu Izin): CBC Bit-Flipping Attack**
   - Hint: *"rantainya saling memengaruhi. Mengubah satu kotak di depan akan mengubah isi di belakangnya. Ubah satu angka di kartu, dan peranmu berubah."*
   - Merupakan enkripsi blok mode CBC (Cipher Block Chaining). Pada dekripsi CBC:
     $$P_i = D_K(C_i) \oplus C_{i-1}$$
     Jika kita mengubah byte pada blok $C_{i-1}$ (kotak di depan), maka byte pada blok plaintext $P_i$ (isi di belakangnya) akan berubah dengan XOR difference yang sama persis:
     $$P_i' = P_i \oplus \Delta \implies C_{i-1}' = C_{i-1} \oplus \Delta$$
   - Plaintext kartu memuat `admin=0` di blok 1 (offset byte ke-6). Dengan membalik bit `card[6] ^= 1` pada IV (blok 0), karakter `'0'` (ASCII `0x30`) berubah menjadi `'1'` (ASCII `0x31`) sehingga status privilege berubah menjadi `admin=1`.

2. **Lapis 2 (Pintu Ulur): SHA-256 Hash Length Extension Attack**
   - Hint: *"tanda tangan yang dibuat dari rahasia pendek yang disambung di depan data, lalu dicincang. Tanda itu bisa diulur tanpa tahu rahasianya, selama kamu paham cara cincang bekerja."*
   - Mekanisme penandatanganan menggunakan pola insecure: `H(secret || data)` dengan fungsi hash konstruksi Merkle–Damgård (SHA-256).
   - Karena sifat Merkle–Damgård, kita dapat melanjutkan internal state hash dari signature yang ada tanpa mengetahui isi `secret`, lalu menambahkan data perintah baru `&admin=1` dengan padding yang sesuai.
   - Melalui iterasi panjang rahasia, ditemukan bahwa panjang `secret` adalah 16 byte.

---

## Langkah Penyelesaian

### 1. Membuka Lapis 1 (Pintu Izin)
- Ambil kartu terenkripsi dari `/izin`.
- Ubah byte ke-6 pada IV dengan XOR 1:
  ```python
  card[6] ^= 1
```
- Kirim ke `/izin/buka?data=<hex>`
- Respon server:
  > *Kubah terbuka. Kata lapis pertama: `balik`*

### 2. Membuka Lapis 2 (Pintu Ulur)
- Data asli: `halaman=utama`
- Tanda tangan asli: `0be8eb5f8bc38356bbf06ad423ccf71581991159ccf49b133d7f50be0d72431e`
- Tambahkan ekstensi `&admin=1` dengan panjang rahasia 16 byte.
- Hitung new signature dan data berpadding baru menggunakan ekspansi SHA-256 state.
- Kirim ke `/ulur/buka?data=<new_data_hex>&tanda=<new_hash>`
- Respon server:
  > *Tali berhasil diulur. Kata lapis kedua: `ulur_panjang`*

### 3. Menggabungkan Kata Kunci & Flag
- Lapis 1: `balik`
- Lapis 2: `ulur_panjang`
- Kunci lengkap: `balik_ulur_panjang`
- Kode tim: `D35D4ECD`

Format: `TechtonicExpoCTF{kunci_KODETIM}`
$$\implies \mathbf{TechtonicExpoCTF\{balik\_ulur\_panjang\_D35D4ECD\}}$$

---

## Script Eksploitasi Otomatis (`solve.py`)

```python
import re
import struct
import urllib.request

BASE_URL = "http://168.110.219.59:5016"
TEAM_CODE = "D35D4ECD"

# --- LAPIS 1: CBC Bit Flipping ---
req = urllib.request.Request(f"{BASE_URL}/izin")
with urllib.request.urlopen(req) as resp:
  html = resp.read().decode("utf-8")
  card_hex = html.split("<pre>")[1].split("</pre>")[0].strip()

card = bytearray(bytes.fromhex(card_hex))
card[6] ^= 1  # Ubah admin=0 menjadi admin=1

req_izin = urllib.request.Request(f"{BASE_URL}/izin/buka?data={card.hex()}")
with urllib.request.urlopen(req_izin) as resp:
  html = resp.read().decode("utf-8")
  lapis1 = (
      re.search(r"Kata lapis pertama:\s*<code>([^<]+)</code>", html)
      .group(1)
      .strip()
  )
  print(f"[+] Lapis 1: {lapis1}")


# --- LAPIS 2: SHA-256 Length Extension ---
def ror(x, y):
  return ((x >> y) | (x << (32 - y))) & 0xFFFFFFFF


def sha256_compress(state, block):
  K = [
      0x428A2F98,
      0x71374491,
      0xB5C0FBCF,
      0xE9B5DBA5,
      0x3956C25B,
      0x59F111F1,
      0x923F82A4,
      0xAB1C5ED5,
      0xD807AA98,
      0x12835B01,
      0x243185BE,
      0x550C7DC3,
      0x72BE5D74,
      0x80DEB1FE,
      0x9BDC06A7,
      0xC19BF174,
      0xE49B69C1,
      0xEFBE4786,
      0x0FC19DC6,
      0x240CA1CC,
      0x2DE92C6F,
      0x4A7484AA,
      0x5CB0A9DC,
      0x76F988DA,
      0x983E5152,
      0xA831C66D,
      0xB00327C8,
      0xBF597FC7,
      0xC6E00BF3,
      0xD5A79147,
      0x06CA6351,
      0x14292967,
      0x27B70A85,
      0x2E1B2138,
      0x4D2C6DFC,
      0x53380D13,
      0x650A7354,
      0x766A0ABB,
      0x81C2C92E,
      0x92722C85,
      0xA2BFE8A1,
      0xA81A664B,
      0xC24B8B70,
      0xC76C51A3,
      0xD192E819,
      0xD6990624,
      0xF40E3585,
      0x106AA070,
      0x19A4C116,
      0x1E376C08,
      0x2748774C,
      0x34B0BCB5,
      0x391C0CB3,
      0x4ED8AA4A,
      0x5B9CCA4F,
      0x682E6FF3,
      0x748F82EE,
      0x78A5636F,
      0x84C87814,
      0x8CC70208,
      0x90BEFFFA,
      0xA4506CEB,
      0xBEF9A3F7,
      0xC67178F2,
  ]
  w = list(struct.unpack(">16I", block)) + [0] * 48
  for i in range(16, 64):
    s0 = ror(w[i - 15], 7) ^ ror(w[i - 15], 18) ^ (w[i - 15] >> 3)
    s1 = ror(w[i - 2], 17) ^ ror(w[i - 2], 19) ^ (w[i - 2] >> 10)
    w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF
  a, b, c, d, e, f, g, h = state
  for i in range(64):
    S1 = ror(e, 6) ^ ror(e, 11) ^ ror(e, 25)
    ch = (e & f) ^ ((~e) & g)
    temp1 = (h + S1 + ch + K[i] + w[i]) & 0xFFFFFFFF
    S0 = ror(a, 2) ^ ror(a, 13) ^ ror(a, 22)
    maj = (a & b) ^ (a & c) ^ (b & c)
    temp2 = (S0 + maj) & 0xFFFFFFFF
    h, g, f = g, f, e
    e = (d + temp1) & 0xFFFFFFFF
    d, c, b = c, b, a
    a = (temp1 + temp2) & 0xFFFFFFFF
  return [(s + x) & 0xFFFFFFFF for s, x in zip(state, [a, b, c, d, e, f, g, h])]


def length_extension(orig_hash, orig_data, ext, secret_len):
  pad = (
      b"\x80"
      + b"\x00" * ((56 - (secret_len + len(orig_data) + 1) % 64) % 64)
      + struct.pack(">Q", (secret_len + len(orig_data)) * 8)
  )
  new_data = orig_data + pad + ext
  state = list(struct.unpack(">8I", bytes.fromhex(orig_hash)))
  total_len = secret_len + len(new_data)
  ext_data = (
      ext
      + b"\x80"
      + b"\x00" * ((56 - (total_len + 1) % 64) % 64)
      + struct.pack(">Q", total_len * 8)
  )
  for i in range(0, len(ext_data), 64):
    state = sha256_compress(state, ext_data[i : i + 64])
  return new_data, "".join(f"{x:08x}" for x in state)


orig_hash = "0be8eb5f8bc38356bbf06ad423ccf71581991159ccf49b133d7f50be0d72431e"
orig_data = b"halaman=utama"
new_data, new_hash = length_extension(orig_hash, orig_data, b"&admin=1", 16)

req_ulur = urllib.request.Request(
    f"{BASE_URL}/ulur/buka?data={new_data.hex()}&tanda={new_hash}"
)
with urllib.request.urlopen(req_ulur) as resp:
  html = resp.read().decode("utf-8")
  lapis2 = (
      re.search(r"Kata lapis kedua:\s*<code>([^<]+)</code>", html)
      .group(1)
      .strip()
  )
  print(f"[+] Lapis 2: {lapis2}")

flag = f"TechtonicExpoCTF{{{lapis1}_{lapis2}_{TEAM_CODE}}}"
print(f"[+] FLAG: {flag}")
```
