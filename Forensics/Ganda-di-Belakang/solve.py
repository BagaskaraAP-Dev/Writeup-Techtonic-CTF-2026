import zipfile
import io
import base64
import os

img_path = r"C:\Users\User\Downloads\ganda_dibelakang.png"
out_dir = r"C:\Users\User\Downloads\Techto Foren\Ganda di Belakang"
os.makedirs(out_dir, exist_ok=True)

team_code = "D35D4ECD"

print("==================================================")
print("     SOLVER: GANDA DI BELAKANG (498 PTS)")
print("==================================================")

with open(img_path, "rb") as f:
    data = f.read()

# ----------------------------------------------------
# 1. Temukan Password di Chunk tEXt PNG
# ----------------------------------------------------
# Chunk tEXt 'pesan': cGludHUyMDI2
pesan_pos = data.find(b"tEXtpesan\x00")
if pesan_pos != -1:
    b64_pass = data[pesan_pos + 10 : pesan_pos + 22].decode("ascii")
    password = base64.b64decode(b64_pass).decode("ascii")
    print(f"[+] Password tersembunyi di tEXt chunk: {password}")

# ----------------------------------------------------
# 2. Ekstrak Trailing Data (ZIP Layer 1) setelah IEND
# ----------------------------------------------------
iend_pos = data.find(b"IEND")
iend_end = iend_pos + 8  # 4 bytes IEND + 4 bytes CRC
zip_data = data[iend_end:]
print(f"[*] Menemukan trailing ZIP di belakang PNG ({len(zip_data)} bytes)")

# Buka Layer 1 ZIP dengan password
zf1 = zipfile.ZipFile(io.BytesIO(zip_data))
print(f"[*] Berkas dalam ZIP Layer 1: {zf1.namelist()}")
arsip_zip_bytes = zf1.read("arsip.zip", pwd=password.encode("ascii"))

# ----------------------------------------------------
# 3. Buka arsip.zip (ZIP Layer 2)
# ----------------------------------------------------
zf2 = zipfile.ZipFile(io.BytesIO(arsip_zip_bytes))
print(f"[*] Berkas dalam ZIP Layer 2: {zf2.namelist()}")

catatan = zf2.read("catatan.txt").decode("utf-8")
print(f"[!] Pesan di catatan.txt: '{catatan}' (Decoy)")

tanda_bytes = zf2.read("tanda.bin")

# ----------------------------------------------------
# 4. Buka tanda.bin (ZIP Layer 3)
# ----------------------------------------------------
zf3 = zipfile.ZipFile(io.BytesIO(tanda_bytes))
print(f"[*] Berkas dalam tanda.bin (ZIP Layer 3): {zf3.namelist()}")

kunci_raw = zf3.read("kunci.txt").decode("utf-8").strip()
print(f"[+] Isi kunci.txt: {kunci_raw}")

kunci = kunci_raw
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print("\n==================================================")
print(f"KUNCI LENGKAP : {kunci}")
print(f"FLAG AKHIR    : {flag}")
print("==================================================")
