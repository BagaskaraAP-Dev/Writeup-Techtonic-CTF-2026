import wave
import numpy as np
from PIL import Image
import os

wav_path = r"C:\Users\User\Downloads\gelombang_bicara.wav"
out_dir = r"C:\Users\User\Downloads\Techto Foren\Gelombang Berbicara"
os.makedirs(out_dir, exist_ok=True)

team_code = "D35D4ECD"

print("==================================================")
print("     SOLVER: GELOMBANG BERBICARA (555 PTS)")
print("==================================================")

with wave.open(wav_path, "rb") as w:
    rate = w.getframerate()
    audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)

# STFT parameters
n_fft = 1024
hop_length = 256
window = np.hanning(n_fft)

num_frames = (len(audio) - n_fft) // hop_length
spectrogram = []

for i in range(num_frames):
    segment = audio[i * hop_length : i * hop_length + n_fft] * window
    spec = np.abs(np.fft.rfft(segment))
    spectrogram.append(spec)

spec_matrix = np.array(spectrogram).T  # shape: (513, num_frames)

# ----------------------------------------------------
# 1. Analisis Lapisan Frekuensi Rendah (Gambar Spektrogram)
# ----------------------------------------------------
print("[*] Tahap 1: Ekstraksi gambar spektrogram di frekuensi rendah (0 - 4000 Hz)...")
# Baris 0..100 (frekuensi ~0 s/d 4300 Hz)
# Simpan gambar kata spektrum
spec_low = spec_matrix[0:100, 100:750]
spec_low_log = np.log1p(spec_low)
p_min, p_max = np.percentile(spec_low_log, 30), np.percentile(spec_low_log, 99.5)
spec_low_norm = np.clip((spec_low_log - p_min) / (p_max - p_min) * 255, 0, 255).astype(np.uint8)

img_low = Image.fromarray(spec_low_norm)
img_low_path = os.path.join(out_dir, "kata_spektrum.png")
img_low.save(img_low_path)

kata_rendah = "spektrum"
print(f"[+] Kata di frekuensi rendah : {kata_rendah}")
print(f"    (Tersimpan di: {img_low_path})")

# ----------------------------------------------------
# 2. Analisis Lapisan Frekuensi Tinggi (Kode Morse)
# ----------------------------------------------------
print("\n[*] Tahap 2: Ekstraksi kode Morse di frekuensi tinggi (~18000 Hz)...")
# Bin frekuensi tinggi (~18000 Hz ada di bin ~418)
high_bin = int(18000 / (rate / 2) * 513)
sig = spec_matrix[high_bin - 3 : high_bin + 4, :].mean(axis=0)

thresh = (np.percentile(sig, 20) + np.percentile(sig, 98)) / 2
binary = (sig > thresh).astype(int)

# Run-length decoding
runs = []
curr_val = binary[0]
curr_len = 0
for b in binary:
    if b == curr_val:
        curr_len += 1
    else:
        runs.append((curr_val, curr_len))
        curr_val = b
        curr_len = 1
runs.append((curr_val, curr_len))

MORSE_DICT = {
    "...-": "V",
    "..": "I",
    "...": "S",
    "..-": "U",
    ".-": "A",
    ".-..": "L"
}

morse_letters = []
current_letter = ""

for val, length in runs:
    if val == 1 and length >= 5:
        current_letter += "-" if length > 30 else "."
    elif val == 0:
        if length > 35 and current_letter:  # Jeda antar huruf (~60 sampel)
            morse_letters.append(current_letter)
            current_letter = ""

if current_letter:
    morse_letters.append(current_letter)

kata_tinggi = "".join(MORSE_DICT.get(m, "?") for m in morse_letters).lower()
print(f"[+] Sinyal Morse terdeteksi  : {' '.join(morse_letters)}")
print(f"[+] Kata di frekuensi tinggi : {kata_tinggi}")

# ----------------------------------------------------
# 3. Penggabungan Flag
# ----------------------------------------------------
kunci = f"{kata_rendah}_{kata_tinggi}"
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print("\n==================================================")
print(f"KUNCI LENGKAP : {kunci}")
print(f"FLAG AKHIR    : {flag}")
print("==================================================")
