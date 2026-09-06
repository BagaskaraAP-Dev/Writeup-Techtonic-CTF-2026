import math
import urllib.request
import re

# Given sequence from challenge
X = [
    987654321012345678,
    6729977692791834322,
    6578750652915850225,
    16888812019745501733,
    2381187045401728115,
    16223185267011201142,
    249113833186806331,
    7114183187174364876
]

print("[*] Tahap 1: Eliminasi c dengan menghitung selisih t_n = x_{n+1} - x_n")
T = [X[i+1] - X[i] for i in range(len(X)-1)]

print("[*] Tahap 2: Eliminasi a dengan determinan |t_{n+1}*t_{n-1} - t_n^2|")
U = [abs(T[i+1]*T[i-1] - T[i]**2) for i in range(1, len(T)-1)]

print("[*] Tahap 3: Mencari modulus m dengan GCD")
m = U[0]
for u in U[1:]:
    m = math.gcd(m, u)

print(f"[+] Recovered Modulus (m)    : {m}")

print("[*] Tahap 4: Menghitung multiplier a dan increment c")
a = (T[1] * pow(T[0], -1, m)) % m
c = (X[1] - a * X[0]) % m

print(f"[+] Recovered Multiplier (a) : {a}")
print(f"[+] Recovered Increment (c)  : {c}")

# Validasi seluruh deret
valid = all((a * X[i] + c) % m == X[i+1] for i in range(len(X)-1))
if not valid:
    print("[-] Validasi parameter gagal!")
    exit(1)
print("[+] Validasi semua state berurutan: SUKSES")

print("[*] Tahap 5: Prediksi angka berikutnya (x8)")
x8 = (a * X[-1] + c) % m
print(f"[+] Tebakan x8 : {x8}")

print("[*] Tahap 6: Mengirimkan tebakan ke server")
team_code = "D35D4ECD"
url = f"http://168.110.219.59:5014/tebak?angka={x8}"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8')
        match = re.search(r"kunci\s*<code>([^<]+)</code>", html)
        if match:
            kunci = match.group(1).strip()
            print(f"[+] Kunci didapatkan: {kunci}")
            flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
            print(f"\n[+] FLAG: {flag}\n")
        else:
            print("[-] Respon server:", html)
except Exception as e:
    print(f"[-] Error menghubungi server: {e}")
