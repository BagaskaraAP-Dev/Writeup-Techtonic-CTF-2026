import numpy as np
from PIL import Image
import os

out_dir = r"C:\Users\User\Downloads\Techto Foren\Gelombang Berbicara"
c2 = np.array(Image.open(os.path.join(out_dir, "crop_high_enhanced.png")))

# 1. Analisis Sinyal Tinggi (Morse)
best_row = np.argmax(c2.sum(axis=1))
sig = c2[best_row-2 : best_row+3, :].mean(axis=0)

thresh = (np.percentile(sig, 20) + np.percentile(sig, 98)) / 2
binary = (sig > thresh).astype(int)

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

print("=== RUNS IN HIGH FREQUENCY ===")
tones = [length for val, length in runs if val == 1 and length >= 2]
silences = [length for val, length in runs if val == 0 and length >= 2]

print("Tones:", tones)
print("Silences:", silences)

# Dot vs Dash threshold
if tones:
    min_tone = min(tones)
    max_tone = max(tones)
    dot_dash_thresh = (min_tone + max_tone) / 2
    print(f"Dot/Dash threshold: {dot_dash_thresh}")

    # Build morse string
    morse_str = ""
    for val, length in runs:
        if val == 1:
            if length >= 2:
                if length > dot_dash_thresh:
                    morse_str += "-"
                else:
                    morse_str += "."
        else:
            if length > 35:
                morse_str += " / "
            elif length > 12:
                morse_str += " "

    print("\nMorse String:")
    print(morse_str)

    # Morse dictionary
    MORSE_CODE_DICT = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
        '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
        '----.': '9', '.-.-.-': '.', '--..--': ',', '..--..': '?',
        '-....-': '-', '-..-.': '/', '---...': ':', '.----.': "'",
        '-.--.': '(', '-.--.-': ')', '.-...': '&', '---...': ':',
        '-.-.--': '!', '...-..-': '$', '.--.-.': '@'
    }

    words = morse_str.strip().split(" / ")
    decoded_words = []
    for w in words:
        letters = w.strip().split()
        decoded_w = "".join(MORSE_CODE_DICT.get(l, "?") for l in letters)
        decoded_words.append(decoded_w)

    print("Decoded Morse Text:", " ".join(decoded_words))
