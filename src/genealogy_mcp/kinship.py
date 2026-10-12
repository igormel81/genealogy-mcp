"""What one relative is to another, in Russian, English and Romanian: «троюродный брат», "first cousin twice removed".

A relation is counted by generations: `up` from person A to the nearest common ancestor and `down` from it to B.
`path` lets you give it as steps instead: "father mother brother son" / «отец матери брат сын».
"""
import re

STEPS = {   # word → (kind, sex)
    "parent": ("up", "U"), "father": ("up", "M"), "mother": ("up", "F"), "отец": ("up", "M"), "мать": ("up", "F"),
    "родитель": ("up", "U"), "папа": ("up", "M"), "мама": ("up", "F"), "tată": ("up", "M"), "mamă": ("up", "F"),
    "child": ("down", "U"), "son": ("down", "M"), "daughter": ("down", "F"), "сын": ("down", "M"), "дочь": ("down", "F"),
    "ребёнок": ("down", "U"), "fiu": ("down", "M"), "fiică": ("down", "F"),
    "sibling": ("side", "U"), "brother": ("side", "M"), "sister": ("side", "F"), "брат": ("side", "M"), "сестра": ("side", "F"),
    "frate": ("side", "M"), "soră": ("side", "F"),
    "grandfather": ("up2", "M"), "grandmother": ("up2", "F"), "дед": ("up2", "M"), "дедушка": ("up2", "M"), "бабушка": ("up2", "F"),
    "grandson": ("down2", "M"), "granddaughter": ("down2", "F"), "внук": ("down2", "M"), "внучка": ("down2", "F"),
    "uncle": ("uncle", "M"), "aunt": ("uncle", "F"), "дядя": ("uncle", "M"), "тётя": ("uncle", "F"), "тетя": ("uncle", "F"),
    "nephew": ("nephew", "M"), "niece": ("nephew", "F"), "племянник": ("nephew", "M"), "племянница": ("nephew", "F"),
    "cousin": ("cousin", "U"), "husband": ("spouse", "M"), "wife": ("spouse", "F"), "spouse": ("spouse", "U"),
    "муж": ("spouse", "M"), "жена": ("spouse", "F"), "супруг": ("spouse", "M"), "супруга": ("spouse", "F"),
}
# Russian genitive forms: «брат отца матери»
GENITIVE = {"отца": "отец", "матери": "мать", "сына": "сын", "дочери": "дочь", "брата": "брат", "сестры": "сестра", "деда": "дед",
            "дедушки": "дедушка", "бабушки": "бабушка", "внука": "внук", "внучки": "внучка", "дяди": "дядя", "тёти": "тётя",
            "тети": "тётя", "мужа": "муж", "жены": "жена", "племянника": "племянник", "племянницы": "племянница", "родителя": "родитель"}


def rep(s, n):
    return s * n if n > 0 else ""


RU_ADJ = ["", "двоюродн", "троюродн", "четвероюродн", "пятиюродн", "шестиюродн", "семиюродн", "восьмиюродн"]


def _ru_adj(i, sex):
    stem = RU_ADJ[i] if i < len(RU_ADJ) else f"{i + 1}-юродн"
    return stem + ("ая " if sex == "F" else "ый " if sex == "M" else "ый(ая) ")


def ru(up, down, sex="U", half=False, parent_sex=None):
    def w(m, f):
        return m if sex == "M" else f if sex == "F" else f"{m} / {f}"
    if down == 0:
        if up == 1:
            return w("отец", "мать")
        return w(rep("пра", up - 2) + "дед", rep("пра", up - 2) + "бабушка")
    if up == 0:
        if down == 1:
            return w("сын", "дочь")
        return w(rep("пра", down - 2) + "внук", rep("пра", down - 2) + "внучка")
    k, r = min(up, down) - 1, abs(up - down)
    if r == 0:
        if k == 0:
            if half:
                return (w("единокровный брат", "единокровная сестра") if parent_sex == "M" else w("единоутробный брат", "единоутробная сестра")
                        if parent_sex == "F" else w("брат по одному из родителей", "сестра по одному из родителей"))
            return w("брат", "сестра")
        return _ru_adj(k, sex) + w("брат", "сестра")
    if up > down:   # B is of an older generation: uncle, great-uncle…
        noun = w("дядя", "тётя") if r == 1 else w(rep("пра", r - 2) + "дед", rep("пра", r - 2) + "бабушка")
        i = k + (1 if r >= 2 else 0)   # брат деда — двоюродный дед; двоюродный брат деда — троюродный дед
        return _ru_adj(i, sex) + noun if i else noun
    pre = "" if r == 1 else "внучат" if r == 2 else rep("пра", r - 3) + "правнучат"
    nephew = w(pre + "ый племянник", pre + "ая племянница") if pre else w("племянник", "племянница")
    return _ru_adj(k, sex) + nephew if k else nephew


EN_ORD = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]


def en(up, down, sex="U", half=False, parent_sex=None):
    def w(m, f, u):
        return m if sex == "M" else f if sex == "F" else u
    great = lambda n: rep("great-", n)   # noqa: E731
    if down == 0:
        return w("father", "mother", "parent") if up == 1 else great(up - 2) + w("grandfather", "grandmother", "grandparent")
    if up == 0:
        return w("son", "daughter", "child") if down == 1 else great(down - 2) + w("grandson", "granddaughter", "grandchild")
    k, r = min(up, down) - 1, abs(up - down)
    if k == 0:
        if r == 0:
            return ("half-" if half else "") + w("brother", "sister", "sibling")
        g = great(r - 1)
        if up > down:
            return w(g + "uncle", g + "aunt", g + "uncle or " + g + "aunt")
        return w(g + "nephew", g + "niece", g + "nephew or " + g + "niece")
    times = ["", "once", "twice", "three times", "four times", "five times"][r] if r < 6 else f"{r} times"
    return (EN_ORD[k] if k < len(EN_ORD) else f"{k}th") + " cousin" + (f" {times} removed" if r else "")


def ro(up, down, sex="U", half=False, parent_sex=None):
    def w(m, f):
        return m if sex == "M" else f if sex == "F" else f"{m} / {f}"
    stra = lambda n: rep("stră", n)   # noqa: E731
    if down == 0:
        return w("tată", "mamă") if up == 1 else w(stra(up - 2) + "bunic", stra(up - 2) + "bunică")
    if up == 0:
        return w("fiu", "fiică") if down == 1 else w(stra(down - 2) + "nepot", stra(down - 2) + "nepoată")
    k, r = min(up, down) - 1, abs(up - down)
    if k == 0:
        if r == 0:
            return w("frate", "soră") + (" (după un singur părinte)" if half else "")
        if up > down:
            return w("unchi", "mătușă") if r == 1 else w("fratele", "sora") + " " + stra(r - 2) + "bunicului"
        return w("nepot de frate", "nepoată de frate") if r == 1 else w(stra(r - 1) + "nepot de frate", stra(r - 1) + "nepoată de frate")
    cousin = w("văr primar", "vară primară") if k == 1 else w(f"văr de gradul {k}", f"vară de gradul {k}")
    return cousin + (f", cu {r} " + ("generație" if r == 1 else "generații") + (" mai sus" if up > down else " mai jos") if r else "")


def name(up, down, sex="U", lang="ru", half=False, parent_sex=None):
    return {"en": en, "ro": ro}.get(lang, ru)(up, down, sex, half, parent_sex)


def parse_path(text):
    """'father's mother's brother's son' / 'отец матери брат' / «сын брата отца» → list of (kind, sex), from A outward."""
    t = text.lower().replace("’", "'").replace("'s", " ")
    words = [x for x in re.split(r"[\s,;→>\-/]+", t) if x and x not in ("of", "the", "my", "мой", "моя", "моего", "моей", "a")]
    genitive = any(x in GENITIVE for x in words)
    if genitive or " of " in f" {text.lower()} ":
        words = list(reversed(words))   # «сын брата отца» = отец → брат → сын
    out = []
    for x in words:
        x = GENITIVE.get(x, x)
        if x not in STEPS:
            raise ValueError(f"unknown step {x!r}; use father/mother/son/daughter/brother/sister/husband/wife (or Russian)")
        out.append(STEPS[x])
    return out


def from_path(steps):
    """Steps → (up, down, sex of the last person, via_spouse). A spouse is allowed only as the first or last step."""
    up = down = 0
    sex = blood_sex = "U"
    spouse_first = spouse_last = False
    for i, (kind, s) in enumerate(steps):
        if kind != "spouse":
            blood_sex = s
        sex = s
        if kind == "spouse":
            if i == 0:
                spouse_first = True
            elif i == len(steps) - 1:
                spouse_last = True
            else:
                raise ValueError("a spouse in the middle of a path: name the in-law step by step instead")
            continue
        if down and kind in ("up", "up2", "side", "uncle"):
            raise ValueError("going up after going down leads to in-laws or step-relations: count from the common ancestor")
        if kind == "up":
            up += 1
        elif kind == "up2":
            up += 2
        elif kind == "down":
            down += 1
        elif kind == "down2":
            down += 2
        elif kind == "side":
            up += 1
            down += 1
        elif kind == "uncle":
            up += 2
            down += 1
        elif kind == "nephew":
            if not (up or down):
                up += 1
            down += 2
        elif kind == "cousin":
            up += 2
            down += 2
    return up, down, (sex, blood_sex), spouse_first, spouse_last


def describe(up=None, down=None, sex="U", path="", half=False, parent_sex=None):
    """The name of the relation in three languages, with the generation numbers and a DNA estimate."""
    spouse_first = spouse_last = False
    blood_sex = sex
    if path:
        up, down, (sex, blood_sex), spouse_first, spouse_last = from_path(parse_path(path))
    up, down = int(up or 0), int(down or 0)
    sex = (sex or "U").upper()[:1]
    if not up and not down:
        return {"error": "the same person"}
    if spouse_last:   # the spouse of a blood relative: name the relative, then 'his/her wife'
        rel = {lang: name(up, down, blood_sex, lang, half, parent_sex) for lang in ("ru", "en", "ro")}
        sp = {"M": ("муж", "husband", "soțul"), "F": ("жена", "wife", "soția")}.get(sex, ("супруг(а)", "spouse", "soțul / soția"))
        out = {"ru": f"{sp[0]} родственника, который приходится: {rel['ru']}", "en": f"{sp[1]} of your {rel['en']}",
               "ro": f"{sp[2]} rudei care vă este {rel['ro']}"}
    else:
        out = {lang: name(up, down, sex, lang, half, parent_sex) for lang in ("ru", "en", "ro")}
        if spouse_first:
            out = {"ru": out["ru"] + " супруга(и)", "en": out["en"] + " of the spouse (in-law)", "ro": out["ro"] + " al soțului / soției"}
    shared = 0.0 if spouse_first or spouse_last else (100.0 / 2 ** (up + down - 1) if up and down else 100.0 / 2 ** max(up, down))
    if half and up and down:
        shared /= 2
    out.update({"up": up, "down": down, "degree_civil": up + down, 
                "dna_shared_percent_expected": round(shared, 3),
                "dna_note": "Expected autosomal DNA in common; real values vary widely (third cousins can share 0%). "
                            "For blood relatives beyond 4th cousins, DNA matches are not proof of the line." if shared else ""})
    return out
