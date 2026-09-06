# Bisikan Orator

- **Kategori:** Cryptography (Eliminasi)
- **Poin:** 368 PTS (7 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **Target URL:** `http://168.110.219.59:5012/`
- **Flag:** `TechtonicExpoCTF{bisikan_bocor_bisikan_bocor_D35D4ECD}`

---

## Deskripsi Soal

> Orator ini berbisik dalam blok-blok sandi. Setiap pesan dibungkus dengan kunci yang sama, dan setiap blok terakhir selalu dilapisi penanda panjangnya.
>
> Yang paling berharga bukan isi bisikannya, melainkan reaksi orator saat mendengarnya. Bisikan yang utuh disambut dengan anggukan, yang terpotong dengan gelengan. Perbedaan sekecil itu adalah celah.
>
> Ambil pesan tersandi dari ruang rahasia, lalu bongkar sedikit demi sedikit. Satu blok terakhir, satu byte penanda, satu bisikan pada satu waktu.
>
> **Endpoint:**
> - Ambil ciphertext dari `/rahasia`
> - Uji oracle ke `/bisik?data=...`

### Ciphertext yang Diberikan:

```text
645d1f4584e0303cd3f4c2f97e97356672649189a5ed16ab470b9cef00fe4d08b65ff0a0e695072f966d0cc9b6ac8362
```

---

## Analisis & Konsep Kriptografi

Petunjuk pada soal secara eksplisit mengindikasikan kerentanan **Padding Oracle Attack** pada mode operasi blok **CBC** dengan padding standar **PKCS#7**:
- *"setiap blok terakhir selalu dilapisi penanda panjangnya"* $\implies$ Padding PKCS#7.
- *"Bisikan yang utuh disambut dengan anggukan, yang terpotong dengan gelengan"* $\implies$ Oracle yang membedakan valid/tidaknya padding:
  - Padding valid: `Orator mengangguk` (HTTP 200)
  - Padding tidak valid: `Orator menggeleng` (HTTP 200)

### Mekanisme CBC Decryption:
Pada CBC mode:
$$P_i = D_K(C_i) \oplus C_{i-1}$$

Dengan memanipulasi blok $R$ yang dikirimkan sebelum target blok $C_i$:
$$P_i' = D_K(C_i) \oplus R$$

Jika kita mencari nilai $R[k]$ sedemikian rupa sehingga padding valid (misal bernilai `pad`), maka intermediate value $I[k] = D_K(C_i)[k]$ dapat dihitung:
$$I[k] = R[k] \oplus \text{pad}$$
Dan plaintext asli diperoleh dengan:
$$P_i[k] = I[k] \oplus C_{i-1}[k]$$

---

## Optimasi Brute-Force (Prioritas Karakter ASCII)

Untuk mempercepat proses tebakan tanpa harus menguji 256 nilai secara linear:
$$R[k] = p \oplus C_{i-1}[k] \oplus \text{pad}$$
Dengan memprioritaskan tebakan karakter $p$ dari distribusi karakter teks yang paling mungkin muncul (huruf kecil, underscore, padding bytes), setiap byte berhasil ditebak rata-rata hanya dalam 1–5 request menggunakan *multi-threading* dan *HTTP Keep-Alive session pooling*.

---

## Hasil Dekripsi Byte per Byte

- **Blok 1 (bytes 0–15):**
  ```text
  Byte 00..15: b i s i k a n _ b o c o r _ b i
  -> b'bisikan_bocor_bi'
  ```

- **Blok 2 (bytes 16–31):**
  ```text
  Byte 00..15: s i k a n _ b o c o r \x05 \x05 \x05 \x05 \x05
  -> b'sikan_bocor\x05\x05\x05\x05\x05'
  ```

- **Plaintext Lengkap (setelah unpadding PKCS#7 5 byte `\x05`):**
  ```text
  bisikan_bocor_bisikan_bocor
  ```

---

## Script Eksploitasi (`solve.py`)

```python
import concurrent.futures
import string
import requests

BASE_URL = "http://168.110.219.59:5012/bisik?data="
cipher_hex = "645d1f4584e0303cd3f4c2f97e97356672649189a5ed16ab470b9cef00fe4d08b65ff0a0e695072f966d0cc9b6ac8362"
raw = bytes.fromhex(cipher_hex)
blocks = [raw[i : i + 16] for i in range(0, len(raw), 16)]

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30)
session.mount("http://", adapter)


def oracle(payload):
  url = BASE_URL + payload.hex()
  try:
    r = session.get(url, timeout=3)
    return "mengangguk" in r.text
  except Exception:
    return False


likely_chars = (
    [ord(c) for c in " etaoinshrdlcumwfgypbvkjxqz_"]
    + list(range(1, 17))
    + [ord(c) for c in string.digits + string.ascii_uppercase + "{}-:!?,."]
)
remaining = [b for b in range(256) if b not in likely_chars]
ordered_guesses = likely_chars + remaining


def decrypt_block(prev_block, target_block, block_num):
  print(f"\n[*] Mendekripsi Blok {block_num}...", flush=True)
  I = [0] * 16
  P = [0] * 16

  for pad_len in range(1, 17):
    byte_pos = 16 - pad_len
    prefix = bytearray(16)
    for k in range(byte_pos + 1, 16):
      prefix[k] = I[k] ^ pad_len

    candidates = []
    for p_guess in ordered_guesses:
      cand = p_guess ^ prev_block[byte_pos] ^ pad_len
      if cand not in candidates:
        candidates.append(cand)

    found_g = None

    def test_candidate(val):
      test_prefix = bytearray(prefix)
      test_prefix[byte_pos] = val
      if pad_len == 1:
        test_prefix[14] ^= 1
        if oracle(bytes(test_prefix) + target_block):
          return val
        test_prefix[14] ^= 1
      if oracle(bytes(test_prefix) + target_block):
        return val
      return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
      future_to_val = {
          executor.submit(test_candidate, g): g for g in candidates
      }
      for fut in concurrent.futures.as_completed(future_to_val):
        res = fut.result()
        if res is not None:
          found_g = res
          for f in future_to_val:
            f.cancel()
          break

    if found_g is None:
      return None

    I[byte_pos] = found_g ^ pad_len
    P[byte_pos] = I[byte_pos] ^ prev_block[byte_pos]
    ch = chr(P[byte_pos]) if 32 <= P[byte_pos] < 127 else f"\\x{P[byte_pos]:02x}"
    print(f"    Byte {byte_pos:02d}: {ch}", flush=True)

  return bytes(P)


p1 = decrypt_block(blocks[0], blocks[1], 1)
p2 = decrypt_block(blocks[1], blocks[2], 2)

full_plaintext = p1 + p2
pad_val = full_plaintext[-1]
unpadded = full_plaintext[:-pad_val]
kunci = unpadded.decode("utf-8")

team_code = "D35D4ECD"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print(f"\n[+] Kunci : {kunci}")
print(f"[+] Flag  : {flag}")
```

---

## Flag

```text
TechtonicExpoCTF{bisikan_bocor_bisikan_bocor_D35D4ECD}
```

*(Catatan: Jika platform CTF hanya menginginkan satu pengulangan frasa: `TechtonicExpoCTF{bisikan_bocor_D35D4ECD}`)*.
