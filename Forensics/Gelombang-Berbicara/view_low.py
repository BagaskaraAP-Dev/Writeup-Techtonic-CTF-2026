import numpy as np
from PIL import Image
import os

out_dir = r"C:\Users\User\Downloads\Techto Foren\Gelombang Berbicara"
full_spec = Image.open(os.path.join(out_dir, "spectrogram_full.png"))
arr = np.array(full_spec)

# Low frequency rows: 420 to 510, cols 100 to 750
crop_low = arr[430:510, 100:750]

# Normalize to clean binary/grayscale image
p_min = np.percentile(crop_low, 35)
p_max = np.percentile(crop_low, 99)
c_norm = np.clip((crop_low - p_min) / (p_max - p_min) * 255, 0, 255).astype(np.uint8)

img = Image.fromarray(c_norm)
img.save(os.path.join(out_dir, "low_text.png"))

# Print ASCII art with good resolution
# Height 80 rows, width 650 cols
# Sample step x=3, step y=2
for r in range(0, c_norm.shape[0], 2):
    line = ""
    for c in range(0, c_norm.shape[1], 3):
        val = c_norm[r:r+2, c:c+3].mean()
        line += "#" if val > 140 else " "
    if line.strip():
        print(f"{r:02d}: {line}")
