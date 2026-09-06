import struct
import urllib.request
import re

BASE_URL = "http://168.110.219.59:5016"
TEAM_CODE = "D35D4ECD"

print("==================================================")
print("     SOLVER: KUBAH TERBALIK (627 PTS)")
print("==================================================")

# ====================================================
# LAPIS 1: Pintu Izin (CBC Bit-Flipping Attack)
# ====================================================
print("\n[+] --- MENYELESAIKAN LAPIS 1: PINTU IZIN ---")
req = urllib.request.Request(f"{BASE_URL}/izin")
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')
    card_hex = html.split('<pre>')[1].split('</pre>')[0].strip()

card = bytearray(bytes.fromhex(card_hex))
print(f"[*] Kartu diperoleh : {card_hex[:32]}...")

# Byte ke-6 di IV (Block 0) mengontrol karakter ke-6 di Block 1 (misal '0' menjadi '1')
card[6] ^= 1
print(f"[*] Membalik bit pada byte ke-6 (IV) -> {card.hex()[:32]}...")

req_izin = urllib.request.Request(f"{BASE_URL}/izin/buka?data={card.hex()}")
with urllib.request.urlopen(req_izin) as resp:
    html = resp.read().decode('utf-8')
    match = re.search(r"Kata lapis pertama:\s*<code>([^<]+)</code>", html)
    if match:
        lapis1 = match.group(1).strip()
        print(f"[+] Kunci Lapis 1: {lapis1}")
    else:
        print("[-] Gagal mendapatkan Lapis 1:", html)
        exit(1)

# ====================================================
# LAPIS 2: Pintu Ulur (SHA-256 Length Extension Attack)
# ====================================================
print("\n[+] --- MENYELESAIKAN LAPIS 2: PINTU ULUR ---")

def ror(x, y):
    return ((x >> y) | (x << (32 - y))) & 0xFFFFFFFF

def sha256_compress(state, block):
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    w = list(struct.unpack('>16I', block)) + [0] * 48
    for i in range(16, 64):
        s0 = ror(w[i-15], 7) ^ ror(w[i-15], 18) ^ (w[i-15] >> 3)
        s1 = ror(w[i-2], 17) ^ ror(w[i-2], 19) ^ (w[i-2] >> 10)
        w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF

    a, b, c, d, e, f, g, h = state
    for i in range(64):
        S1 = ror(e, 6) ^ ror(e, 11) ^ ror(e, 25)
        ch = (e & f) ^ ((~e) & g)
        temp1 = (h + S1 + ch + K[i] + w[i]) & 0xFFFFFFFF
        S0 = ror(a, 2) ^ ror(a, 13) ^ ror(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (S0 + maj) & 0xFFFFFFFF

        h = g
        g = f
        f = e
        e = (d + temp1) & 0xFFFFFFFF
        d = c
        c = b
        b = a
        a = (temp1 + temp2) & 0xFFFFFFFF

    return [
        (state[0] + a) & 0xFFFFFFFF,
        (state[1] + b) & 0xFFFFFFFF,
        (state[2] + c) & 0xFFFFFFFF,
        (state[3] + d) & 0xFFFFFFFF,
        (state[4] + e) & 0xFFFFFFFF,
        (state[5] + f) & 0xFFFFFFFF,
        (state[6] + g) & 0xFFFFFFFF,
        (state[7] + h) & 0xFFFFFFFF,
    ]

def length_extension(orig_hash, orig_data, ext, secret_len):
    pad = b'\x80' + b'\x00' * ((56 - (secret_len + len(orig_data) + 1) % 64) % 64) + struct.pack('>Q', (secret_len + len(orig_data)) * 8)
    new_data = orig_data + pad + ext
    state = list(struct.unpack('>8I', bytes.fromhex(orig_hash)))
    total_len = secret_len + len(new_data)
    ext_data = ext + b'\x80' + b'\x00' * ((56 - (total_len + 1) % 64) % 64) + struct.pack('>Q', total_len * 8)
    for i in range(0, len(ext_data), 64):
        state = sha256_compress(state, ext_data[i:i+64])
    new_hash = ''.join(f'{x:08x}' for x in state)
    return new_data, new_hash

orig_hash = "0be8eb5f8bc38356bbf06ad423ccf71581991159ccf49b133d7f50be0d72431e"
orig_data = b"halaman=utama"
ext = b"&admin=1"
secret_len = 16

new_data, new_hash = length_extension(orig_hash, orig_data, ext, secret_len)
print(f"[*] Mengirim payload length extension (secret_len={secret_len})...")

req_ulur = urllib.request.Request(f"{BASE_URL}/ulur/buka?data={new_data.hex()}&tanda={new_hash}")
with urllib.request.urlopen(req_ulur) as resp:
    html = resp.read().decode('utf-8')
    match = re.search(r"Kata lapis kedua:\s*<code>([^<]+)</code>", html)
    if match:
        lapis2 = match.group(1).strip()
        print(f"[+] Kunci Lapis 2: {lapis2}")
    else:
        print("[-] Gagal mendapatkan Lapis 2:", html)
        exit(1)

# ====================================================
# FLAG GENERATION
# ====================================================
kunci = f"{lapis1}_{lapis2}"
flag = f"TechtonicExpoCTF{{{kunci}_{TEAM_CODE}}}"

print("\n==================================================")
print(f"KUNCI LENGKAP : {kunci}")
print(f"FLAG AKHIR    : {flag}")
print("==================================================")
