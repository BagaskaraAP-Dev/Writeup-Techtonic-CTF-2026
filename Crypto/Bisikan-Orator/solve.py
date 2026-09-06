def oracle(payload):
    url = BASE_URL + payload.hex()
    try:
        r = session.get(url, timeout=3)
        return "mengangguk" in r.text
    except Exception:
        return False

# Karakter yang paling mungkin muncul diprioritaskan
likely_chars = (
    [ord(c) for c in " etaoinshrdlcumwfgypbvkjxqz_"] +
    list(range(1, 17)) +
    [ord(c) for c in string.digits + string.ascii_uppercase + "{}-:!?,."]
)
remaining = [b for b in range(256) if b not in likely_chars]
ordered_guesses = likely_chars + remaining