# Tabung Tembaga

- **Kategori:** Cryptography (Eliminasi)
- **Poin:** 522 PTS (12 Solves)
- **Format Flag:** `TechtonicExpoCTF{kunci_KODETIM}`
- **Kode Tim:** `D35D4ECD`
- **Target URL:** `http://168.110.219.59:5015/`
- **Flag:** `TechtonicExpoCTF{kembar_terkait_D35D4ECD}`

---

## Deskripsi Soal

> Dua pesan terlahir dari akar yang sama. Pesan kedua hanya berselisih satu langkah dari yang pertama, dan keduanya dipanggang dengan pangkat tiga di dalam tabung yang sama.
>
> Dengan eksponen sekecil itu, dua teks sandi yang saling berkerabat bisa diadu hingga saling menguak. Selisih satu langkah sudah cukup untuk merobek keduanya.
>
> Bedah polinomnya, cari akar bersama, dan pesan pertama akan menampakkan diri.

### Parameter yang Diberikan:

```text
n = 12752605662767444895866579287960777789318627294248168165314966739607248639070627805346692824964414894160242179846035320605271053968305677721912938315972969682829530076042008000810331790914532615137698957274243227802734182844706843939381724419242965776820109091967949994499069570291372848893553392892886955521
e = 3
c1 = 10335354943553817684128269459125640869543408673459156221113376806064396203025084848809372118592586048
c2 = 10335354943553817684128269459125655103911277562519634088612780080817002159742722129877229347027178317
```

---

## Analisis & Konsep Kriptografi

Nama challenge *"Tabung Tembaga"* merujuk pada **Coppersmith Attack** dan petunjuk *"dua pesan saling berkerabat berselisih satu langkah dengan eksponen 3"* merujuk pada **Franklin-Reiter Related Message Attack**.

Diketahui dua ciphertext RSA dengan modulus $n$ dan eksponen $e = 3$:
$$c_1 \equiv m^3 \pmod n$$
$$c_2 \equiv (m + 1)^3 \pmod n$$

### Metode 1: Franklin-Reiter Attack (Polynomial GCD Modulo $n$)
Bentuk dua polinomial:
$$f_1(x) = x^3 - c_1 \pmod n$$
$$f_2(x) = (x + 1)^3 - c_2 = x^3 + 3x^2 + 3x + (1 - c_2) \pmod n$$

Kedua polinomial memiliki akar sekutu $x = m \pmod n$. Menggunakan algoritma Euclidean untuk mencari pembagi persekutuan terbesar polinomial (polynomial GCD) dalam ring $\mathbb{Z}_n[x]$:
$$\gcd(f_1(x), f_2(x)) = (x - m) \pmod n$$
Sehingga nilai $m$ dapat langsung diperoleh dari koefisien konstan polinomial hasil bagi.

---

### Metode 2: Solusi Kuadratik Langsung (No Modulo Wrap)
Karena pesan $m$ relatif pendek (hanya ~14 karakter) dan $e = 3$, nilai $m^3 < n$ dan $(m + 1)^3 < n$, sehingga enkripsi tidak mengalami pembagian sisa (modulo tidak pernah wrap):
$$c_1 = m^3$$
$$c_2 = (m + 1)^3 = m^3 + 3m^2 + 3m + 1$$

Selisih keduanya:
$$\Delta = c_2 - c_1 = 3m^2 + 3m + 1$$

Persamaan kuadrat sederhana:
$$3m^2 + 3m + (1 - \Delta) = 0$$

Dengan rumus diskriminan:
$$D = 3^2 - 4(3)(1 - \Delta) = 12\Delta - 3$$
$$m = \frac{-3 + \sqrt{D}}{6}$$

---

## Script Penyelesaian (`solve.py`)

```python
import math

n = 12752605662767444895866579287960777789318627294248168165314966739607248639070627805346692824964414894160242179846035320605271053968305677721912938315972969682829530076042008000810331790914532615137698957274243227802734182844706843939381724419242965776820109091967949994499069570291372848893553392892886955521
e = 3
c1 = 10335354943553817684128269459125640869543408673459156221113376806064396203025084848809372118592586048
c2 = 10335354943553817684128269459125655103911277562519634088612780080817002159742722129877229347027178317
team_code = "D35D4ECD"

# Selisih kuadratik langsung
diff = c2 - c1
D = 12 * diff - 3
sqrt_D = math.isqrt(D)

m = (-3 + sqrt_D) // 6
kunci = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode('utf-8')
flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"

print(f"[+] Nilai m : {m}")
print(f"[+] Kunci   : {kunci}")
print(f"[+] Flag    : {flag}")
```

---

## Hasil Eksekusi

```text
[+] Nilai m : 2178253724805649638202285427353972
[+] Kunci   : kembar_terkait
[+] Flag    : TechtonicExpoCTF{kembar_terkait_D35D4ECD}
```

Format flag: `TechtonicExpoCTF{kunci_KODETIM}`
$$\implies \mathbf{TechtonicExpoCTF\{kembar\_terkait\_D35D4ECD\}}$$
