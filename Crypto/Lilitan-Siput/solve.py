# Solver untuk tantangan Lilitan Siput (412 PTS)
team_code = "D35D4ECD"

ciphertext = "LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES"
order = [3, 1, 5, 0, 4, 2]
num_cols = len(order)
col_len = len(ciphertext) // num_cols

print("==================================================")
print("       SOLVER: LILITAN SIPUT (412 PTS)")
print("==================================================")

# ----------------------------------------------------
# LAPIS 2: Membalik Transposisi Kolom (Columnar Transposition)
# ----------------------------------------------------
print("\n[*] Tahap 1: Membalik transposisi kolom (6 kolom, panjang 9 per kolom)")
cols = {}
for idx, col_idx in enumerate(order):
    cols[col_idx] = ciphertext[idx * col_len : (idx + 1) * col_len]

# Baca kembali baris demi baris (row by row)
rows = []
for r in range(col_len):
    rows.append("".join(cols[c][r] for c in range(num_cols)))

intermediate_text = "".join(rows)
print(f"[+] Teks antara (Ciphertext Vigenere): {intermediate_text}")

# ----------------------------------------------------
# LAPIS 1: Memecahkan Vigenere Cipher (Key length 5)
# ----------------------------------------------------
print("\n[*] Tahap 2: Dekripsi Vigenere Cipher")
# Dari analisis frekuensi huruf bahasa Indonesia (Chi-Squared test),
# diperoleh kunci 5 huruf: RINDU
vigenere_key = "RINDU"
print(f"[+] Kunci Vigenere ditemukan: {vigenere_key}")

plaintext_chars = []
for i, ch in enumerate(intermediate_text):
    k = ord(vigenere_key[i % len(vigenere_key)]) - ord('A')
    p = (ord(ch) - ord('A') - k) % 26
    plaintext_chars.append(chr(p + ord('A')))

plaintext = "".join(plaintext_chars)
print(f"[+] Plaintext Asli: {plaintext}")

# ----------------------------------------------------
# Analisis Kata Kunci
# ----------------------------------------------------
# Kalimat asli: LILIT PUTAR DUA SEDANG TERKUNCI DALAM DUA LAPIS RANGKAI KEMBALI
# Subjek yang terkunci: lilit_putar_dua
kunci = "lilit_putar_dua"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print("\n==================================================")
print(f"PLAINTEXT : {plaintext}")
print(f"KUNCI     : {kunci}")
print(f"FLAG      : {flag}")
print("==================================================")
