# Generator Nakal

- **Kategori:** Cryptography (Eliminasi)
- **Poin:** 565 PTS (7 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **Target URL:** `http://168.110.219.59:5014/`
- **Flag:** `TechtonicExpoCTF{ramal_lcg_nakal_D35D4ECD}`

---

## Deskripsi Soal

> Mesin ini membangkitkan angka dengan rumus yang kaku. Setiap angka adalah anak dari angka sebelumnya. Rumusnya memakai pengali, penambah, dan sisa bagi besar yang semuanya tersembunyi.
>
> Tapi deret keluarannya bicara lebih banyak dari yang disangka. Dari beberapa angka berurutan, semua parameter rahasia bisa dibedah satu per satu.
>
> Tebak angka berikutnya dan kirim ke mesin. Kalau tepat, mesin mengakui kuncinya.
>
> **Tantangan:** Tebak angka berikutnya di `/tebak?angka=...`

### Deret Angka yang Diberikan:

```text
x0 = 987654321012345678
x1 = 6729977692791834322
x2 = 6578750652915850225
x3 = 16888812019745501733
x4 = 2381187045401728115
x5 = 16223185267011201142
x6 = 249113833186806331
x7 = 7114183187174364876
```

---

## Analisis & Metodologi

Deskripsi menyebutkan: *"pengali, penambah, dan sisa bagi besar yang semuanya tersembunyi"* serta *"setiap angka adalah anak dari angka sebelumnya"*. Pola ini mencirikan sebuah **Linear Congruential Generator (LCG)** dengan relasi rekurensi:

$$x_{n+1} \equiv (a \cdot x_n + c) \pmod m$$

Di mana:
- $a$ = pengali (multiplier)
- $c$ = penambah (increment)
- $m$ = sisa bagi (modulus)

Meskipun $a$, $c$, dan $m$ dirahasiakan, kita diberikan 8 state berurutan ($x_0$ s/d $x_7$). Parameter LCG dapat dibongkar secara bertahap menggunakan teknik kriptanalisis LCG klasik:

### 1. Eliminasi Penambah ($c$)
Definisikan selisih antara dua angka berturutan:
$$t_n = x_{n+1} - x_n$$

Maka:
$$t_n \equiv (a \cdot x_n + c) - (a \cdot x_{n-1} + c) \equiv a(x_n - x_{n-1}) \equiv a \cdot t_{n-1} \pmod m$$

Konstanta $c$ berhasil dieliminasi.

### 2. Eliminasi Pengali ($a$)
Karena $t_{n+1} \equiv a \cdot t_n \pmod m$ dan $t_n \equiv a \cdot t_{n-1} \pmod m$, jika kita kalikan silang:
$$t_{n+1} \cdot t_{n-1} \equiv (a \cdot t_n) \cdot t_{n-1} \equiv t_n \cdot (a \cdot t_{n-1}) \equiv t_n^2 \pmod m$$

Sehingga:
$$t_{n+1} \cdot t_{n-1} - t_n^2 \equiv 0 \pmod m$$

Artinya, nilai $u_n = |t_{n+1} \cdot t_{n-1} - t_n^2|$ pasti merupakan kelipatan bulat dari modulus $m$.

### 3. Menemukan Modulus ($m$)
Dengan menghitung $u_n$ untuk beberapa nilai $n$ ($n = 1, 2, 3, \dots$), modulus $m$ adalah pembagi persekutuan terbesar (GCD) dari nilai-nilai $u_n$ tersebut:
$$m = \gcd(u_1, u_2, u_3, \dots)$$

### 4. Menemukan Multiplier ($a$) dan Increment ($c$)
Setelah $m$ diketahui:
$$t_1 \equiv a \cdot t_0 \pmod m \implies a \equiv t_1 \cdot (t_0)^{-1} \pmod m$$
$$c \equiv (x_1 - a \cdot x_0) \pmod m$$

### 5. Memprediksi Angka Berikutnya ($x_8$)
$$x_8 = (a \cdot x_7 + c) \pmod m$$

---

## Parameter yang Berhasil Dibongkar

- **$m$** = `18446744073709551557` (bilangan prima 64-bit dekat $2^{64}$)
- **$a$** = `6364136223846793005` (konstanta Donald Knuth MMIX)
- **$c$** = `1442695040888963407` (konstanta Donald Knuth MMIX)
- **$x_8$** = `359657071830169386`

---

## Script Eksploitasi (`solve.py`)

```python
import math
import urllib.request
import re

X = [
    987654321012345678,
    6729977692791834322,
    6578750652915850225,
    16888812019745501733,
    2381187045401728115,
    16223185267011201142,
    249113833186806331,
    7114183187174364876
]

# 1. Eliminasi c
T = [X[i+1] - X[i] for i in range(len(X)-1)]

# 2. Eliminasi a
U = [abs(T[i+1]*T[i-1] - T[i]**2) for i in range(1, len(T)-1)]

# 3. Temukan m via GCD
m = U[0]
for u in U[1:]:
    m = math.gcd(m, u)

# 4. Temukan a dan c
a = (T[1] * pow(T[0], -1, m)) % m
c = (X[1] - a * X[0]) % m

print(f"[+] Modulus m    : {m}")
print(f"[+] Multiplier a : {a}")
print(f"[+] Increment c  : {c}")

# 5. Hitung angka berikutnya x8
x8 = (a * X[-1] + c) % m
print(f"[+] Tebakan x8   : {x8}")

# 6. Kirim tebakan ke server
team_code = "D35D4ECD"
url = f"http://168.110.219.59:5014/tebak?angka={x8}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')
    match = re.search(r"kunci\s*<code>([^<]+)</code>", html)
    if match:
        kunci = match.group(1).strip()
        print(f"[+] Kunci server : {kunci}")
        flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
        print(f"[+] Flag         : {flag}")
```

---

## Eksekusi & Hasil

Mengirimkan `angka=359657071830169386` ke endpoint `/tebak`:

```http
GET /tebak?angka=359657071830169386 HTTP/1.1
Host: 168.110.219.59:5014
```

Respon server:
```html
<div class="kartu">
  <div class="label">// TERKAIT</div>
  <p>Prediksimu tepat. Mesin mengakui: kunci <code>ramal_lcg_nakal</code></p>
</div>
```

Kunci yang diperoleh: `ramal_lcg_nakal`

Digabungkan dengan format flag dan kode tim `D35D4ECD`:
```text
TechtonicExpoCTF{ramal_lcg_nakal_D35D4ECD}
```
