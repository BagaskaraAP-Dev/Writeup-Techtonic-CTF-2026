import math

# Parameter RSA dari soal
n = 12752605662767444895866579287960777789318627294248168165314966739607248639070627805346692824964414894160242179846035320605271053968305677721912938315972969682829530076042008000810331790914532615137698957274243227802734182844706843939381724419242965776820109091967949994499069570291372848893553392892886955521
e = 3
c1 = 10335354943553817684128269459125640869543408673459156221113376806064396203025084848809372118592586048
c2 = 10335354943553817684128269459125655103911277562519634088612780080817002159742722129877229347027178317
team_code = "D35D4ECD"

print("==================================================")
print("     SOLVER: TABUNG TEMBAGA (522 PTS)")
print("==================================================")

# Metode 1: Franklin-Reiter Related Message Attack / Selisih Kuadratik Langsung
# Karena c2 = (m + 1)^3 dan c1 = m^3:
# c2 - c1 = (m + 1)^3 - m^3 = 3*m^2 + 3*m + 1 (karena m^3 < n tanpa pembagian modulo)
# Persamaan kuadratik: 3*m^2 + 3*m + (1 - (c2 - c1)) = 0
diff = c2 - c1
D = 12 * diff - 3
sqrt_D = math.isqrt(D)

if sqrt_D * sqrt_D == D:
    m = (-3 + sqrt_D) // 6
    kunci = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode('utf-8')
    flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
    
    print(f"[+] Nilai m numerik : {m}")
    print(f"[+] Plaintext/Kunci : {kunci}")
    print(f"[+] FLAG            : {flag}")
else:
    # Metode 2: Polynomial GCD Modulo n (Franklin-Reiter Standar)
    def poly_clean(p, mod):
        p = [x % mod for x in p]
        while len(p) > 1 and p[0] == 0:
            p.pop(0)
        return p

    def poly_divmod(p1, p2, mod):
        p1 = poly_clean(p1, mod)
        p2 = poly_clean(p2, mod)
        inv_lead = pow(p2[0], -1, mod)
        while len(p1) >= len(p2) and not (len(p1) == 1 and p1[0] == 0):
            deg_diff = len(p1) - len(p2)
            coeff = (p1[0] * inv_lead) % mod
            for i in range(len(p2)):
                p1[i] = (p1[i] - coeff * p2[i]) % mod
            p1 = poly_clean(p1, mod)
        return p1

    def poly_gcd(p1, p2, mod):
        while p2 != [0]:
            p1, p2 = p2, poly_divmod(p1, p2, mod)
        inv = pow(p1[0], -1, mod)
        return [(c * inv) % mod for c in p1]

    p1 = [1, 0, 0, -c1]
    p2 = [1, 3, 3, 1 - c2]
    g = poly_gcd(p1, p2, n)
    m = (-g[1]) % n
    kunci = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode('utf-8')
    flag = f"TechtonicExpoCTF{{{kunci}_{team_code}}}"
    print(f"[+] Plaintext via GCD : {kunci}")
    print(f"[+] FLAG              : {flag}")

print("==================================================")
