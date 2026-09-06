import struct
import base64
import os

img_path = r"C:\Users\User\Downloads\foto_jejak.jpg"
out_dir = r"C:\Users\User\Downloads\Techto Foren\Jejak Metadata"
os.makedirs(out_dir, exist_ok=True)

team_code = "D35D4ECD"

print("==================================================")
print("       SOLVER: JEJAK METADATA (337 PTS)")
print("==================================================")

with open(img_path, "rb") as f:
    data = f.read()

# 1. Analisis APP1 (EXIF)
app1_len = struct.unpack(">H", data[4:6])[0]
app1 = data[6 : 4 + app1_len]
tiff = app1[6:]

# Parsing Tag UserComment (0x9286)
user_comment_pos = tiff.find(b"tersimpan")
if user_comment_pos != -1:
    kata_teks = "tersimpan"
    print(f"[*] Bagian 1 (Tersimpan sebagai teks di EXIF): {kata_teks}")

# Deteksi decoy
if b"kunci_sesungguhnya_ada_disini" in tiff:
    print("[!] Catatan mencolok (Decoy/Jebakan di ImageDescription): kunci_sesungguhnya_ada_disini")

# 2. Analisis COM (Comment Marker - 'Data tanpa nama')
com_pos = data.find(b"\xff\xfe")
if com_pos != -1:
    com_len = struct.unpack(">H", data[com_pos+2 : com_pos+4])[0]
    com_data = data[com_pos+4 : com_pos+2+com_len]
    print(f"[*] Bagian 2 (Menyamar di COM marker tanpa nama): {com_data.decode('ascii')}")
    kata_b64 = base64.b64decode(com_data).decode('ascii')
    print(f"[+] Hasil decode Base64: {kata_b64}")

# 3. Rangkai apa yang saling bersambung
kunci = f"{kata_b64}{kata_teks}"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print("\n==================================================")
print(f"KUNCI LENGKAP : {kunci}")
print(f"FLAG AKHIR    : {flag}")
print("==================================================")
