"""Church Slavonic (Cyrillic) numerals: а҃ = 1, ѳі = 19, ҂аѡ҃п = 1880 — dates and page numbers in old registers."""
import re

VALUES = {
    "а": 1, "в": 2, "г": 3, "д": 4, "є": 5, "е": 5, "ѕ": 6, "s": 6, "з": 7, "ꙁ": 7, "и": 8, "ѳ": 9, "ө": 9, "ф": 500,
    "і": 10, "i": 10, "ї": 10, "к": 20, "л": 30, "м": 40, "н": 50, "ѯ": 60, "о": 70, "ѻ": 70, "п": 80, "ч": 90, "ҁ": 90,
    "р": 100, "с": 200, "т": 300, "у": 400, "ѵ": 400, "ꙋ": 400, "х": 600, "ѱ": 700, "ѡ": 800, "ѿ": 800, "ꙍ": 800, "ц": 900,
}
MARKS = "҃҄҅҆҇҈҉́̀̑ˇ~"   # titlo and other overline marks
UNITS = ["", "а", "в", "г", "д", "є", "ѕ", "з", "и", "ѳ"]
TENS = ["", "і", "к", "л", "м", "н", "ѯ", "ѻ", "п", "ч"]
HUNDREDS = ["", "р", "с", "т", "у", "ф", "х", "ѱ", "ѡ", "ц"]


def parse(text):
    """'҂аѡ҃п' → 1880. Letters are summed; ҂ multiplies the next letter by 1000. Returns None when it is not a numeral."""
    t = "".join(ch for ch in str(text).lower() if ch not in MARKS and not ch.isspace() and ch not in ".,")
    if not t or any(ch not in VALUES and ch != "҂" for ch in t):
        return None
    total, mult = 0, 1
    for ch in t:
        if ch == "҂":
            mult *= 1000
            continue
        total += VALUES[ch] * mult
        mult = 1
    return total


def _below_1000(n):
    h, rest = divmod(n, 100)
    out = HUNDREDS[h]
    if 11 <= rest <= 19:
        out += UNITS[rest - 10] + "і"   # 11–19 are written units first: ѕі = 16
    else:
        out += TENS[rest // 10] + UNITS[rest % 10]
    return out


def format(n):
    """1880 → '҂аѡ҃п' (titlo over the last-but-one letter, or the only one)."""
    n = int(n)
    if not 0 < n < 1_000_000:
        raise ValueError("1 … 999999")
    th, rest = divmod(n, 1000)
    body = ("҂" + "҂".join(_below_1000(th)) if th else "") + _below_1000(rest)   # each thousands letter takes ҂
    letters = [i for i, ch in enumerate(body) if ch != "҂"]
    at = letters[-2] if len(letters) > 1 else letters[0]
    return body[: at + 1] + "҃" + body[at + 1:]


def find_all(text):
    """Every numeral-looking group with a titlo in a transcription: [('҂аѡ҃п', 1880), …]."""
    out = []
    for m in re.finditer(r"҂?[" + "".join(VALUES) + r"҂]*҃[" + "".join(VALUES) + r"]*", text.lower()):
        v = parse(m[0])
        if v:
            out.append((m[0], v))
    return out
