"""Moldovan and Bessarabian surnames in Russian, Soviet and Romanian records.

One family may be written Călugăreanu, Calugareanu, Călugărean in Romanian, Калугарян, Калугаряну, Калугоряну in
Russian imperial registers, Кэлугэряну in Soviet Moldavian Cyrillic (1938–1989), and Калгаран by a clerk who heard
it fast. Pleș is Плеш, Плешъ (pre-1918) or Плешу (Pleșu). A register may give two surnames at once — «Мокану, он же
Плеш», "Mocanu zis Pleș" — a second surname or a nickname that became one. And a similar form may be another family:
«Плеско» in an index turned out to be «Попеско» on the scan.
"""
import re

RO_LETTERS = "ăâîșşțţ"
RO_ENDINGS = ("eanu", "ianu", "anu", "escu", "ean", "ache", "iuc", "aşu", "așu")
RU_ENDINGS = ("яну", "ану", "ян", "еску", "эску", "еско", "аке", "юк", "ару", "уца", "ица")
ALIAS = re.compile(r"\s*(?:,\s*)?(?:\bон же\b|\bона же\b|\bони же\b|\bон-же\b|\bиначе\b|\bпо прозвищу\b|\bпрозванием\b|\bили\b|"
                   r"\bzis[ăa]?\b|\bzisă\b|\bzișii\b|\balias\b|\bvel\b|\bsive\b|\bdit\b|\baka\b|/|\()\s*", re.I)
FALSE_FRIENDS = [   # pairs met in real searches: alike in an index or recognised text, different on the scan
    ("Плеско", "Попеско"), ("Plesco", "Popescu"),
]
# letters that handwriting and text recognition confuse in Cyrillic records
OCR_PAIRS = [("р", "м"), ("ш", "щ"), ("ш", "т"), ("и", "н"), ("и", "п"), ("л", "м"), ("а", "о"), ("е", "с"), ("в", "б"),
             ("ц", "щ"), ("я", "л")]
VOWELS_RU = "аеёиоуыэюя"


def _cyr(s):
    return bool(re.search(r"[а-яё]", s.lower()))


def looks_moldovan(name):
    low = name.lower().strip()
    if ALIAS.search(" " + low + " ") and len(split_alias(name)) > 1:
        return True
    if any(c in low for c in RO_LETTERS):
        return True
    w = low.split()[-1] if low.split() else ""
    return w.endswith(RU_ENDINGS if _cyr(w) else RO_ENDINGS)


def split_alias(text):
    """«Мокану, он же Плеш» → ['Мокану', 'Плеш']; 'Mocanu zis Pleș' → ['Mocanu', 'Pleș']."""
    parts = [p.strip(" ,.;)") for p in ALIAS.split(str(text or "")) if p and p.strip(" ,.;)")]
    return parts if len(parts) > 1 else [str(text or "").strip()]


# ---------------------------------------------------------------- Romanian → Cyrillic

RO_DIGRAPHS = [("che", "ке"), ("chi", "ки"), ("ghe", "ге"), ("ghi", "ги"), ("ce", "че"), ("ci", "чи"),
               ("ge", "дже"), ("gi", "джи"), ("ea", "я"), ("iu", "ю"), ("ia", "ия"), ("io", "ио")]
RO_LETTER = {"a": "а", "â": "ы", "î": "ы", "b": "б", "c": "к", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "х", "i": "и",
             "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "ș": "ш",
             "ş": "ш", "t": "т", "ț": "ц", "ţ": "ц", "u": "у", "v": "в", "w": "в", "x": "кс", "y": "и", "z": "з"}


def _ro_to_cyr(word, a_breve):
    """One rendering: ă as given (а, э or о)."""
    w = word.lower()
    out, i = [], 0
    while i < len(w):
        for ro, ru in RO_DIGRAPHS:
            if w.startswith(ro, i):
                if ro == "ia" and i > 0 and w[i - 1] not in "aeiouăâî":
                    ru = "я"
                if ro == "ce" and i + 2 < len(w) and w[i + 2] == "a":   # cea → ча
                    ro, ru = "cea", "ча"
                if ro == "ge" and i + 2 < len(w) and w[i + 2] == "a":
                    ro, ru = "gea", "джа"
                out.append(ru)
                i += len(ro)
                break
        else:
            ch = w[i]
            out.append(a_breve if ch == "ă" else RO_LETTER.get(ch, ch))
            i += 1
    res = "".join(out)
    return res[:1].upper() + res[1:]


def romanian_to_russian(word):
    """Călugăreanu → Калугаряну, Калугарян, Калугоряну…; Pleș → Плеш, Плешъ; Popescu → Попеску, Попеско."""
    base = _ro_to_cyr(word, "а")
    out = [base]
    if "ă" in word.lower():
        # one ă heard as о (Калугоряну), each in turn
        for m in re.finditer("ă", word.lower()):
            alt = word[:m.start()] + "ŏ" + word[m.end():]
            out.append(_ro_to_cyr(alt.replace("ŏ", "o"), "а"))
    forms = []
    for f in out:
        forms.append(f)
        low = f.lower()
        if low.endswith(("яну", "ану", "ину", "ую")):
            forms.append(f[:-1])                       # Калугаряну → Калугарян
        if low.endswith("еску"):
            forms.append(f[:-1] + "о")                 # Попеску → Попеско
        if low[-1:] not in VOWELS_RU + "йь":
            forms.append(f + "ъ")                      # Плеш → Плешъ (before 1918)
    return list(dict.fromkeys(forms))


def soviet_moldavian(word):
    """Moldavian Cyrillic of 1938–1989: ă → э, â/î → ы, ge/gi → ӂе/ӂи: Călugăreanu → Кэлугэряну."""
    w = re.sub(r"g(?=[ei])", "ӂ", word.lower())
    res = _ro_to_cyr(w, "э").replace("ӂ", "ӂ")
    return res[:1].upper() + res[1:]


# ---------------------------------------------------------------- Cyrillic → Romanian

def russian_to_romanian(word):
    """Калугарян → Călugărean, Călugăreanu, Calugareanu; Плеш → Pleș, Pleșu; Попеско → Popescu."""
    w = word.lower().replace("ъ", "").replace("ё", "io")
    if w.endswith("еско"):
        w = w[:-1] + "у"
    out, i = [], 0
    while i < len(w):
        ch = w[i]
        nxt = w[i + 1] if i + 1 < len(w) else ""
        prev = w[i - 1] if i else ""
        if w.startswith("дж", i):
            out.append("g" if w[i + 2:i + 3] in ("е", "и") else "gi")
            i += 2
            continue
        if ch == "ч":
            out.append("c" if nxt in "еи" else "ce" if nxt == "а" else "ci")
        elif ch == "к":
            out.append("ch" if nxt in "еи" else "c")
        elif ch == "г":
            out.append("gh" if nxt in "еи" else "g")
        elif ch == "я":
            out.append("ea" if prev and prev not in VOWELS_RU else "ia")
        elif ch == "ю":
            out.append("iu")
        else:
            out.append({"а": "a", "б": "b", "в": "v", "д": "d", "е": "e", "ж": "j", "з": "z", "и": "i", "й": "i", "л": "l",
                        "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h",
                        "ц": "ț", "ш": "ș", "щ": "șt", "ы": "î", "ь": "", "э": "ă"}.get(ch, ch))
        i += 1
    base = "".join(out)
    forms = [base]
    if re.search(r"(ean|ian|an)$", base):
        forms.append(base + "u")                       # Калугарян → Călugărean(u)
    elif base[-1:] and base[-1] not in "aeiouăîâ":
        forms.append(base + "u")                       # Плеш → Pleș, Pleșu
    if base.endswith("u") and len(base) > 4 and base[-2] not in "aeiouăîâ":
        forms.append(base[:-1])                        # Плешу → Pleș
    breve = []
    for f in forms:   # unstressed a in the stem is often ă in Romanian: Calugarean → Călugărean
        m = re.search(r"(eanu|ianu|anu|ean|ian|an|escu|u)$", f)
        stem_end = len(f) - (len(m[1]) if m else 0)
        if len(re.findall(r"[aeiouy]", f[:stem_end])) < 3:   # short stems: the a is usually stressed (Mocanu)
            continue
        alt = f[:1] + re.sub(r"(?<![eiaou])a(?![aeiou])", "ă", f[1:stem_end]) + f[stem_end:]
        if alt != f:
            breve.append(alt)
    forms = forms + breve
    out = []
    for f in forms:
        cap = f[:1].upper() + f[1:]
        out += [cap, cap.replace("ș", "ş").replace("ț", "ţ")]
        plain = cap
        for a, b in (("ă", "a"), ("â", "a"), ("î", "i"), ("ș", "s"), ("ț", "t")):
            plain = plain.replace(a, b)
        out.append(plain)
    return list(dict.fromkeys(out))


def romanian_endings(word):
    """Călugăreanu ↔ Călugărean ↔ Călugăranu ↔ Călugăran: the -eanu/-ean/-anu/-an family."""
    m = re.match(r"(.+?)(eanu|ianu|anu|ean|ian|an)$", word, re.I)
    if not m:
        return []
    stem, end = m[1], m[2].lower()
    pair = {"eanu": "ean", "ean": "eanu", "ianu": "ian", "ian": "ianu", "anu": "an", "an": "anu"}[end]
    return [stem + pair]


def contractions(word):
    """What a clerk who heard the name fast may write: -ян heard as -ан, one unstressed vowel of the stem dropped
    (Калугарян → Калугаран → Калгаран)."""
    out = []
    words = [word]
    if re.search(r"яну?$", word):
        words.append(re.sub(r"яну?$", "ан", word))
        out.append(words[-1])
    for w in words:
        out += _drop_vowel(w)
    return list(dict.fromkeys(out))[:6]


def _drop_vowel(word):
    out = []
    low = word.lower()
    for m in re.finditer(r"(?<=[бвгджзклмнпрстфхцчшщ])[аоуеиыэ](?=[бвгджзклмнпрстфхцчшщ][аоуеиыэяю])", low):
        if 1 < m.start() < len(low) - 3:
            out.append(word[:m.start()] + word[m.end():])
    return out


def ocr_forms(word, limit=10):
    out = []
    low = word.lower()
    for a, b in OCR_PAIRS:
        for x, y in ((a, b), (b, a)):
            i = low.find(x, 1)
            if i > 0:
                out.append(word[:i] + y + word[i + 1:])
    return list(dict.fromkeys(out))[:limit]


def false_friends(word):
    low = word.lower()
    return [b if a.lower() == low else a for a, b in FALSE_FRIENDS if low in (a.lower(), b.lower())]


def variants(name):
    """All of the above for one surname (or an alias pair)."""
    parts = split_alias(name)
    if len(parts) > 1:
        return {"alias": {"surnames": parts, "flag": "possible second surname",
                          "note": ("A register that writes two surnames («Мокану, он же Плеш», 'Mocanu zis Pleș') records a second "
                                   "surname or a nickname that became one. Search both; the person's children, siblings or later "
                                   "records may carry either. It is not a sign of two people — but check it on the scan.")},
                "each": {p: variants(p) for p in parts}}
    w = name.strip()
    out = {}
    if _cyr(w):
        ro = russian_to_romanian(w)
        best = next((x for x in ro if "ă" in x), ro[0]) if ro else ""
        ro = list(dict.fromkeys(([best] if best else []) + ro))
        ru_back = romanian_to_russian(best) if best else []
        out["romanian"] = ro
        out["russian"] = [x for x in dict.fromkeys([w] + ru_back + [f[:-1] for f in [w] if f.lower().endswith(("яну", "ану"))]
                                                   + [w + "у" for _ in [0] if w.lower().endswith(("ян", "ан", "ш", "ж"))]) if x]
        out["soviet_moldavian"] = soviet_moldavian(best) if best else None
    else:
        out["romanian"] = list(dict.fromkeys([w] + romanian_endings(w) + [w.replace("ș", "ş").replace("ț", "ţ")]
                                             + [re.sub("[ăâ]", "a", w).replace("î", "i").replace("ș", "s").replace("ş", "s")
                                                .replace("ț", "t").replace("ţ", "t")]))
        out["russian"] = list(dict.fromkeys(f for r in [w] + romanian_endings(w)[:1] for f in romanian_to_russian(r)))
        out["soviet_moldavian"] = soviet_moldavian(w)
    base_ru = out["russian"][0] if out["russian"] else w
    out["clerk_contractions"] = contractions(base_ru)
    out["ocr_hints"] = ocr_forms(base_ru)
    ff = false_friends(w) or [x for f in out["russian"] for x in false_friends(f)]
    out["false_friends"] = ff
    out["warning"] = ("Similar is not the same: an index or recognised-text form may belong to another family "
                      "(«Плеско» in an index was «Попеско» on the scan). Contractions and recognition hints are for searching "
                      "only — read the scan before linking a record, and confirm it with check_match.")
    return out


__all__ = ["variants", "looks_moldovan", "split_alias", "romanian_to_russian", "russian_to_romanian", "soviet_moldavian"]
