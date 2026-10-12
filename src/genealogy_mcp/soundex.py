"""Daitch–Mokotoff Soundex: the phonetic code JewishGen, the Ellis Island search (stevemorse.org) and many Eastern
European indexes use. Names that sound alike get the same six-digit code: Moskowitz = Moskovitz = Moskovic → 645740.
Some letters can sound two ways (CH, CK, J, RS, RZ), so a name may have several codes.
"""
import re
import unicodedata

# rule → (at the start of a name, before a vowel, elsewhere); "|" separates alternatives, "" = not coded
RULES = {
    "a": ("0", "", ""), "ai": ("0", "1", ""), "aj": ("0", "1", ""), "ay": ("0", "1", ""), "au": ("0", "7", ""),
    "e": ("0", "", ""), "ei": ("0", "1", ""), "ej": ("0", "1", ""), "ey": ("0", "1", ""), "eu": ("1", "1", ""),
    "i": ("0", "", ""), "ia": ("1", "", ""), "ie": ("1", "", ""), "io": ("1", "", ""), "iu": ("1", "", ""),
    "o": ("0", "", ""), "oi": ("0", "1", ""), "oj": ("0", "1", ""), "oy": ("0", "1", ""),
    "u": ("0", "", ""), "ue": ("0", "", ""), "ui": ("0", "1", ""), "uj": ("0", "1", ""), "uy": ("0", "1", ""),
    "y": ("1", "", ""), "j": ("1|4", "|4", "|4"),
    "b": ("7", "7", "7"), "c": ("5|4", "5|4", "5|4"), "ch": ("5|4", "5|4", "5|4"), "chs": ("5", "54", "54"),
    "ck": ("5|45", "5|45", "5|45"), "cs": ("4", "4", "4"), "csz": ("4", "4", "4"), "cz": ("4", "4", "4"), "czs": ("4", "4", "4"),
    "d": ("3", "3", "3"), "drs": ("4", "4", "4"), "drz": ("4", "4", "4"), "ds": ("4", "4", "4"), "dsh": ("4", "4", "4"),
    "dsz": ("4", "4", "4"), "dt": ("3", "3", "3"), "dz": ("4", "4", "4"), "dzh": ("4", "4", "4"), "dzs": ("4", "4", "4"),
    "f": ("7", "7", "7"), "fb": ("7", "7", "7"), "g": ("5", "5", "5"), "h": ("5", "5", ""),
    "k": ("5", "5", "5"), "kh": ("5", "5", "5"), "ks": ("5", "54", "54"), "l": ("8", "8", "8"),
    "m": ("6", "6", "6"), "mn": ("66", "66", "66"), "n": ("6", "6", "6"), "nm": ("66", "66", "66"),
    "p": ("7", "7", "7"), "pf": ("7", "7", "7"), "ph": ("7", "7", "7"), "q": ("5", "5", "5"),
    "r": ("9", "9", "9"), "rs": ("94|4", "94|4", "94|4"), "rz": ("94|4", "94|4", "94|4"),
    "s": ("4", "4", "4"), "sc": ("2", "4", "4"), "sch": ("4", "4", "4"), "schd": ("2", "43", "43"), "scht": ("2", "43", "43"),
    "schtch": ("2", "4", "4"), "schtsch": ("2", "4", "4"), "schtsh": ("2", "4", "4"), "sd": ("2", "43", "43"),
    "sh": ("4", "4", "4"), "shch": ("2", "4", "4"), "shd": ("2", "43", "43"), "sht": ("2", "43", "43"),
    "shtch": ("2", "4", "4"), "shtsh": ("2", "4", "4"), "st": ("2", "43", "43"), "stch": ("2", "4", "4"),
    "strs": ("2", "4", "4"), "strz": ("2", "4", "4"), "stsch": ("2", "4", "4"), "stsh": ("2", "4", "4"),
    "sz": ("4", "4", "4"), "szcz": ("2", "4", "4"), "szd": ("2", "43", "43"), "szt": ("2", "43", "43"),
    "t": ("3", "3", "3"), "tc": ("4", "4", "4"), "tch": ("4", "4", "4"), "th": ("3", "3", "3"), "trs": ("4", "4", "4"),
    "trz": ("4", "4", "4"), "ts": ("4", "4", "4"), "tsch": ("4", "4", "4"), "tsh": ("4", "4", "4"), "tsz": ("4", "4", "4"),
    "ttch": ("4", "4", "4"), "tts": ("4", "4", "4"), "ttsch": ("4", "4", "4"), "ttsz": ("4", "4", "4"), "ttz": ("4", "4", "4"),
    "tz": ("4", "4", "4"), "tzs": ("4", "4", "4"), "v": ("7", "7", "7"), "w": ("7", "7", "7"), "x": ("5", "54", "54"),
    "z": ("4", "4", "4"), "zd": ("2", "43", "43"), "zdz": ("2", "4", "4"), "zdzh": ("2", "4", "4"), "zh": ("4", "4", "4"),
    "zhd": ("2", "43", "43"), "zhdzh": ("2", "4", "4"), "zs": ("4", "4", "4"), "zsch": ("4", "4", "4"), "zsh": ("4", "4", "4"),
}
LONGEST = max(map(len, RULES))
VOWELS = set("aeiou")
FORCE = {"mn", "nm"}   # both letters are coded even though the codes repeat
FOLD = str.maketrans({"ł": "l", "ß": "s", "ø": "o", "æ": "e", "œ": "e", "đ": "d", "ı": "i"})


def _clean(name):
    s = name.lower().translate(FOLD)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s)


def dm_soundex(name):
    """All Daitch–Mokotoff codes of a Latin-script name, e.g. 'Peters' → ['739400', '734000']."""
    s = _clean(name)
    branches = [("", None)]   # (code so far, last replacement)
    i = 0
    while i < len(s):
        for n in range(min(LONGEST, len(s) - i), 0, -1):
            rule = s[i:i + n]
            if rule in RULES:
                break
        else:
            i += 1
            continue
        start, vowel, other = RULES[rule]
        nxt = s[i + n] if i + n < len(s) else ""
        options = (start if i == 0 else vowel if nxt in VOWELS else other).split("|")
        new = []
        for code, last in branches:
            for rep in options:
                if rep == last and rule not in FORCE:
                    new.append((code, rep))
                else:
                    new.append((code + rep, rep))
        branches = list(dict.fromkeys(new))[:32]
        i += n
    codes = [(c + "000000")[:6] for c, _ in branches]
    return list(dict.fromkeys(codes))


def codes_for(name):
    """For Cyrillic names: the codes of the German, Polish and passport transliterations together."""
    from . import names
    forms = [name]
    if names._cyr(name):
        forms = [names.translit(name, s) for s in ("passport", "german", "polish")]
    out = []
    for f in forms:
        out += dm_soundex(f)
    return list(dict.fromkeys(out))
