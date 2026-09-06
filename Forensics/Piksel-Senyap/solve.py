import os
from PIL import Image

# Path gambar
img_path = r"C:\Users\User\Downloads\piksel_senyap.png"
out_dir = r"C:\Users\User\Downloads\Techto Foren\Piksel Senyap"
os.makedirs(out_dir, exist_ok=True)

team_code = "D35D4ECD"

print("==================================================")
print("       SOLVER: PIKSEL SENYAP (317 PTS)")
print("==================================================")

im = Image.open(img_path)
w, h = im.size
pixels = list(im.getdata())

# 1. Analisis Lapis Pertama (Decoy / Jebakan di R bit 0)
r_bit0 = [(p[0] & 1) for p in pixels]
r_bytes = bytearray()
for i in range(0, len(r_bit0), 8):
    byte = 0
    for b in r_bit0[i:i+8]:
        byte = (byte << 1) | b
    r_bytes.append(byte)

decoy = r_bytes[:21].decode('ascii', errors='ignore')
print(f"[*] Deteksi R bit 0 (Lapisan yang 'berbohong'): {decoy}")

# 2. Analisis Lapis Sebenarnya (Blue bit 1 - digeser 1 bit)
print("[*] Mengekstrak Blue bit 1 (Lapisan asli setelah digeser)...")
b_bit1 = [((p[2] >> 1) & 1) * 255 for p in pixels]
plane_img = Image.new('L', (w, h))
plane_img.putdata(b_bit1)
plane_path = os.path.join(out_dir, "blue_bit_1.png")
plane_img.save(plane_path)
print(f"[+] Gambar bit plane disimpan di: {plane_path}")

# Karakter visual yang terbaca pada y=228..276: lsb_tersembunyi
kunci = "lsb_tersembunyi"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print("\n==================================================")
print(f"KUNCI ASLI : {kunci}")
print(f"FLAG       : {flag}")
print("==================================================")
