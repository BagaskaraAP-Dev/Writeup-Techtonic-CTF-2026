# Lilitan Siput

- **Kategori:** Cryptography (Eliminasi)
- **Poin:** 412 PTS (3 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **Target URL:** `http://168.110.219.59:5013/`
- **Flag:** `TechtonicExpoCTF{lilit_putar_dua_D35D4ECD}`

---

## Deskripsi Soal

> Jejak siput berputar dua kali. Lapisan pertama menggeser tiap huruf mengikuti irama lima ketukan. Lapisan kedua membungkus hasilnya dalam enam kolom yang dibaca dengan urutan ganjil.
>
> Urutan pembacaan kolom sudah diumumkan, dan panjang irama juga bukan rahasia. Yang tersisa hanyalah membalik dua lapisan itu dengan teliti.
>
> Kalimat asli memakai huruf besar tanpa spasi, dan di dalamnya terselip kata kunci yang sedang kamu cari.

### Parameter yang Diberikan:

```text
Ciphertext: LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES
Panjang Vigenere: 5 huruf
Urutan kolom: 3-1-5-0-4-2 (6 kolom)
```

---

## Analisis & Konsep Kriptografi

Proses enkripsi terdiri dari 2 lapisan:
1. **Lapisan 1 (Substitusi):** Vigenère Cipher dengan kunci berpanjang 5 huruf.
2. **Lapisan 2 (Transposisi):** Columnar Transposition Cipher dengan 6 kolom, di mana kolom dibaca sesuai urutan `[3, 1, 5, 0, 4, 2]`.

Untuk mendekripsinya, kita harus membalik urutan langkah tersebut:
1. Membalik **Transposisi Kolom** untuk mendapatkan teks antara.
2. Memecahkan **Vigenère Cipher** menggunakan analisis frekuensi bahasa Indonesia.

---

## Langkah Penyelesaian

### 1. Membalik Transposisi Kolom
Panjang ciphertext adalah 54 huruf. Karena terdapat 6 kolom:
$$\text{Panjang tiap kolom} = \frac{54}{6} = 9 \text{ karakter}$$

Urutan pembacaan adalah `[3, 1, 5, 0, 4, 2]`:
- Kolom 3: `ct[0:9]` $\implies$ `LLUZQXMRI`
- Kolom 1: `ct[9:18]` $\implies$ `QGVNTUCJG`
- Kolom 5: `ct[18:27]` $\implies$ `GCAXFCIXL`
- Kolom 0: `ct[27:36]` $\implies$ `CCNJHRIAH`
- Kolom 4: `ct[36:45]` $\implies$ `NUIXDUIQY`
- Kolom 2: `ct[45:54]` $\implies$ `YDYVQQLES`

Membaca baris demi baris (dari baris 0 sampai 8):
```text
CQYLNGCGDLUCNVYUIAJNVZXXHTQQDFRUQXUCICLMIIAJERQXHGSIYL
```

---

### 2. Kriptanalisis Vigenère Cipher (Panjang Kunci = 5)
Pisahkan teks antara ke dalam 5 stream (karakter pada indeks $i \pmod 5$).
Lakukan uji **Chi-Squared ($\chi^2$)** terhadap frekuensi huruf bahasa Indonesia (di mana huruf A, N, E, I, T memiliki frekuensi tertinggi):

$$\chi^2 = \sum_{c=\text{'A'}}^{\text{'Z'}} \frac{(O_c - E_c)^2}{E_c}$$

Hasil skor terbaik untuk masing-masing stream:
- Stream 0: **`R`** ($\chi^2 = 26.1$)
- Stream 1: **`I`** ($\chi^2 = 17.6$)
- Stream 2: **`N`** ($\chi^2 = 23.6$)
- Stream 3: **`D`** ($\chi^2 = 20.9$)
- Stream 4: **`U`** ($\chi^2 = 10.1$)

Kunci Vigenère yang ditemukan adalah kata bermakna dalam bahasa Indonesia: **`RINDU`**.

---

### 3. Dekripsi Plaintext
Mendekripsi teks antara dengan kunci `RINDU`:
```text
LILITPUTARDUASEDANGTERKUNCIDALAMDUALAPISRANGKAIKEMBALI
```

Jika dipisahkan dengan spasi:
> *"LILIT PUTAR DUA SEDANG TERKUNCI DALAM DUA LAPIS RANGKAI KEMBALI"*

Subjek yang terkunci di dalam dua lapis adalah:
$$\mathbf{lilit\_putar\_dua}$$

Sesuai pola flag pada soal-soal sebelumnya (`ramal_lcg_nakal`, `balik_ulur_panjang`, `kembar_terkait`), format kunci menggunakan huruf kecil dengan pemisah *underscore*:

$$\text{Kunci} = \mathbf{lilit\_putar\_dua}$$
$$\text{Kode Tim} = \mathbf{D35D4ECD}$$

---

## Script Eksploitasi (`solve.py`)

```python
team_code = "D35D4ECD"
ciphertext = "LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES"
order = [3, 1, 5, 0, 4, 2]
num_cols = len(order)
col_len = len(ciphertext) // num_cols

# 1. Balik Transposisi Kolom
cols = {}
for idx, col_idx in enumerate(order):
  cols[col_idx] = ciphertext[idx * col_len : (idx + 1) * col_len]

rows = []
for r in range(col_len):
  rows.append("".join(cols[c][r] for c in range(num_cols)))

intermediate_text = "".join(rows)

# 2. Dekripsi Vigenere (Kunci: RINDU)
key = "RINDU"
plaintext = "".join(
    chr((ord(ch) - ord("A") - (ord(key[i % 5]) - ord("A"))) % 26 + ord("A"))
    for i, ch in enumerate(intermediate_text)
)

print(f"[+] Plaintext : {plaintext}")
# Plaintext: LILITPUTARDUASEDANGTERKUNCIDALAMDUALAPISRANGKAIKEMBALI

kunci = "lilit_putar_dua"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
print(f"[+] Flag      : {flag}")
```

---

## Flag

```text
TechtonicExpoCTF{lilit_putar_dua_D35D4ECD}
```

*(Catatan opsi alternatif jika platform meminta frasa lain dari kalimat tersebut: `TechtonicExpoCTF{rangkai_kembali_D35D4ECD}` atau `TechtonicExpoCTF{sedang_terkunci_D35D4ECD}`)*.
