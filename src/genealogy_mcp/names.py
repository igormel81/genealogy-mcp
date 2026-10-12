"""Name variants for searching: transliterations, old spelling, gendered surname forms, given-name equivalents.

A record may write the same person as Колодин, Колодинъ, Kolodin, Kolodine, Kołodin or Колодина (his wife);
Иван, Іоаннъ, Ян, Іван, Johann, Juan. Databases match letters, not people — search for all of them.
"""
import re

CYR = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяіїєґѣѳѵ"
# Cyrillic → Latin by system; letters missing in a table fall back to the passport one
TRANSLIT = {
    "passport": dict(zip(CYR, "a b v g d e e zh z i i k l m n o p r s t u f kh ts ch sh shch ie y  e iu ia i i ie g e f i".split(" "))),
    "bgn": dict(zip(CYR, "a b v g d e ë zh z i y k l m n o p r s t u f kh ts ch sh shch ” y ’ e yu ya i yi ye g e f i".split(" "))),
    "scholarly": dict(zip(CYR, "a b v g d e ë ž z i j k l m n o p r s t u f x c č š šč ʺ y ʹ è ju ja i ji je g ě f i".split(" "))),
    "german": dict(zip(CYR, "a b w g d e jo sch s i i k l m n o p r s t u f ch z tsch sch schtsch  y  e ju ja i ji je g e f i".split(" "))),
    "french": dict(zip(CYR, "a b v g d e io j z i i k l m n o p r s t ou f kh ts tch ch chtch  y  e iou ia i ii ie g e f i".split(" "))),
    "polish": dict(zip(CYR, "a b w g d e io ż z i j k ł m n o p r s t u f ch c cz sz szcz  y  e iu ia i ji je g e f i".split(" "))),
    "romanian": dict(zip(CYR, "a b v g d e io j z i i c l m n o p r s t u f h ț ci ș șci  î  e iu ia i i ie g e f i".split(" "))),
    "spanish": dict(zip(CYR, "a b v g d e io zh z i i k l m n o p r s t u f j ts ch sh sch  y  e iu ia i i ie g e f i".split(" "))),
    "ukrainian": dict(zip(CYR, "a b v h d e e zh z y i k l m n o p r s t u f kh ts ch sh shch  y  e iu ia i i ie g e f i".split(" "))),
}
TRANSLIT["english"] = TRANSLIT["bgn"]
# word-initial forms of the passport / Ukrainian systems
INITIAL = {"passport": {"е": "e", "ю": "iu", "я": "ia"}, "ukrainian": {"є": "ye", "ї": "yi", "й": "y", "ю": "yu", "я": "ya"},
           "german": {"е": "je"}, "bgn": {"е": "ye"}}

GIVEN = [   # equivalents of one given name across languages and church forms
    "Иван Іоаннъ Иоанн Іван Ян Jan Johann Johannes John Ivan Iwan Ioan Ion Juan João Giovanni Jean Jonas Ioannes Janis Jānis Jonas",
    "Пётр Петр Петръ Пётр Петро Piotr Peter Pierre Pedro Pietro Petrus Petru Pēteris Petras",
    "Павел Павелъ Павло Paweł Paul Pablo Paulo Paolo Paulus Pavel Pavlo Paulius",
    "Михаил Михаилъ Михайло Michał Michael Michel Miguel Michele Michael Mihai Mihail Mykhailo Mykolas",
    "Николай Николай Микола Mikołaj Nikolaus Nicholas Nicolas Nicolás Nicola Nicolae Mykola Nikolai Mikalojus",
    "Георгий Георгій Юрий Егор Юрій Jerzy Georg George Georges Jorge Giorgio Gheorghe Yurii Yuri Jurgis",
    "Андрей Андрей Андрій Andrzej Andreas Andrew André Andrés Andrea Andrei Andrii Andrius",
    "Алексей Алексѣй Олексій Aleksy Alexis Alejo Alessio Alexei Oleksii",
    "Александр Александръ Олександр Aleksander Alexander Alexandre Alejandro Alessandro Alexandru Oleksandr Aleksandras",
    "Василий Василій Василь Bazyli Basilius Basil Basile Basilio Vasile Vasyl Vasilii",
    "Фёдор Федор Феодоръ Хведір Федір Teodor Theodor Theodore Théodore Teodoro Fiodor Fedir Fyodor",
    "Яков Іаковъ Яків Jakub Jakob Jacob Jacques Jaime Santiago Giacomo Iacob Yakiv Jokūbas",
    "Иосиф Іосифъ Осип Йосип Józef Joseph Josef José Giuseppe Iosif Yosyp Juozapas",
    "Григорий Григорій Григорій Grzegorz Gregor Gregory Grégoire Gregorio Grigore Hryhorii",
    "Стефан Степан Стефанъ Степан Szczepan Stefan Stephan Stephen Étienne Esteban Stefano Ștefan Stepan Steponas",
    "Матвей Матфей Матвій Mateusz Matthäus Matthew Mathieu Mateo Matteo Matei Matvii",
    "Даниил Данила Данило Daniel Daniele Danylo Danielius",
    "Марк Mark Marek Markus Marc Marcos Marco Marcu",
    "Анна Ганна Hanna Anna Anne Ana Anne Anica",
    "Мария Марія Марья Маріа Maria Marie Mary María Marija Marya Mariia",
    "Екатерина Екатерина Катерина Katarzyna Katharina Catherine Catalina Caterina Ecaterina Kateryna Kotryna",
    "Елизавета Елисавета Єлизавета Elżbieta Elisabeth Elizabeth Élisabeth Isabel Elisabetta Elisabeta Yelyzaveta",
    "Евдокия Авдотья Явдоха Eudokia Eudoxia Evdokiia Yevdokiia",
    "Пелагея Палагея Пелагія Pelagia Pélagie Pelagia",
    "Агафья Агафія Ганна Agata Agathe Agatha Ágata Agata",
    "Ксения Аксинья Оксана Ксенія Ksenia Xenia Oksana Kseniia",
    "Софья София Софія Zofia Sophie Sophia Sofía Sofia",
    "Татьяна Татіана Тетяна Tatiana Tatjana Tetiana",
    "Наталья Наталия Наталія Natalia Natalie Nathalie Natália Natalia",
    "Ольга Ольга Olga Olha Olga",
    "Евфросиния Ефросинья Фрося Єфросинія Eufrozyna Euphrosyne Eufrosina",
    "Параскева Прасковья Параска Paraskewa Paraschiva Parascovia",
]
GIVEN_INDEX = {}
for i, row in enumerate(GIVEN):
    for w in row.split():
        GIVEN_INDEX.setdefault(w.lower(), set()).add(i)

# Russian surname endings: male → female (and back)
SURNAME_FORMS = [("ский", "ская"), ("цкий", "цкая"), ("ской", "ская"), ("ый", "ая"), ("ов", "ова"), ("ев", "ева"),
                 ("ёв", "ёва"), ("ин", "ина"), ("ын", "ына"), ("ой", "ая")]
LATIN_FORMS = [("dzki", "dzka"), ("ski", "ska"), ("cki", "cka"), ("ský", "ská"), ("ý", "á"),   # Polish, Czech, Slovak
               ("as", "ienė"), ("as", "aitė"), ("is", "ienė"), ("is", "ytė"), ("us", "ienė"), ("us", "ūtė"),   # Lithuanian
               ("š", "a"), ("s", "a")]                                           # Latvian (Bērziņš → Bērziņa)


def translit(text, system="passport"):
    """Cyrillic → Latin by the named system; Latin text is returned unchanged."""
    table = TRANSLIT.get(system, TRANSLIT["passport"])
    base = TRANSLIT["passport"]
    out = []
    for i, ch in enumerate(text):
        low = ch.lower()
        if low not in base:
            out.append(ch)
            continue
        first = i == 0 or not text[i - 1].isalpha() or text[i - 1].lower() in "аеёиоуыэюяъьіїє"
        v = INITIAL.get(system, {}).get(low) if first else None
        v = v if v is not None else table.get(low, base[low])
        out.append(v.capitalize() if ch.isupper() and v else v)
    res = "".join(out)
    if system in ("german", "french"):   # one s between vowels reads as z there
        res = re.sub(r"(?<=[aeiouyAEIOUY])s(?=[aeiouy])", "ss", res)
    return res


def old_orthography(word):
    """The pre-1918 spelling a record (and a full-text search over it) may use: Колодинъ, Сынковскій, Іоаннъ."""
    w = word
    w = re.sub(r"([бвгджзклмнпрстфхцчшщ])$", r"\1ъ", w)
    w = re.sub(r"ий$", "ій", w)
    w = re.sub(r"и(?=[аеёиоуыэюяй])", "і", w)
    return w


def _cyr(word):
    return bool(re.search(r"[а-яёіїєґ]", word.lower()))


def gendered(surname):
    """Колодин → Колодина; Сынковская → Сынковский; Kowalski → Kowalska; Kazlauskas → Kazlauskienė, Kazlauskaitė."""
    w = surname
    low = w.lower()
    pairs = SURNAME_FORMS if _cyr(w) else LATIN_FORMS
    out = []
    for _, f_end in pairs:   # a female form → the male ones
        if f_end != "a" and low.endswith(f_end):
            out = [w[: len(w) - len(f_end)] + m for m, f in pairs if f == f_end]
            break
    if not out:
        for m_end, _ in pairs:
            if low.endswith(m_end):
                out = [w[: len(w) - len(m_end)] + f for m, f in pairs if m == m_end]
                break
    return list(dict.fromkeys(x for x in out if x and x != w))


SPELLING = [("ё", "е"), ("е", "и"), ("о", "а"), ("ы", "и"), ("ский", "цкий"), ("ов", "ев"), ("г", "х"), ("и", "і"),
            ("ий", "ой"), ("е", "э"), ("ья", "ия"), ("ьев", "иев")]
DOUBLES = ("нн", "сс", "лл", "мм", "тт", "рр")   # only dropped, never added


def spelling(word, limit=12):
    """Spellings a priest or a clerk may have used (one change at a time): Колодин → Калодин, Коладин…"""
    out = []
    low = word.lower()
    for a, b in SPELLING:
        for x, y in ((a, b), (b, a)):
            for m in re.finditer(re.escape(x), low):
                cand = low[: m.start()] + y + low[m.end():]
                if cand != low:
                    out.append(cand)
    for d in DOUBLES:
        if d in low:
            out.append(low.replace(d, d[0]))
    cap = [c[:1].upper() + c[1:] if word[:1].isupper() else c for c in out]
    return list(dict.fromkeys(cap))[:limit]


def given_equivalents(name):
    rows = GIVEN_INDEX.get(name.lower().strip(), set())
    out = []
    for i in sorted(rows):
        out += GIVEN[i].split()
    return list(dict.fromkeys(x for x in out if x.lower() != name.lower()))


PATRONYMIC = [("ович", "овна"), ("евич", "евна"), ("ич", "ична")]


def patronymic_forms(p):
    """Отчество: Петрович / Петровна / Петров (in old records) / Петров сын."""
    low = p.lower()
    out = []
    for m_end, f_end in PATRONYMIC:
        if low.endswith(m_end):
            stem = p[: -len(m_end)]
            short = stem + m_end[:2] if m_end != "ич" else ""   # Петрович → Петров (the old short form)
            out += [stem + f_end] + ([short, short + " сын"] if short else [])
            break
        if low.endswith(f_end):
            stem = p[: -len(f_end)]
            short = stem + f_end[:2] if f_end != "ична" else ""
            out += [stem + m_end] + ([short + "а", short + "а дочь"] if short else [])
            break
    return [x for x in dict.fromkeys(out) if x.strip() and x != p]


def variants(name, kind="surname"):
    """Everything to search for: {"spelling", "old_orthography", "gendered", "latin": {system: form}, "equivalents"}."""
    name = name.strip()
    words = name.split()
    out = {"input": name}
    if kind == "given":
        out["equivalents"] = given_equivalents(name)
    elif kind == "patronymic":
        out["forms"] = patronymic_forms(name)
    else:
        out["gendered"] = gendered(name)
        if _cyr(name):
            out["spelling"] = spelling(name)
    if _cyr(name):
        out["old_orthography"] = " ".join(old_orthography(w) for w in words)
        latin = {}
        forms = [name] + out.get("gendered", [])[:1]
        for system in ("passport", "bgn", "german", "french", "polish", "romanian", "spanish", "ukrainian", "scholarly"):
            latin[system] = " / ".join(dict.fromkeys(translit(f, system) for f in forms))
        out["latin"] = latin
        out["search_tip"] = ("Search the Latin forms in Western databases (FamilySearch, Ellis Island, Arolsen) and "
                             "the old spelling in full-text searches of pre-1918 books.")
    return out


def all_forms(name, kind="surname", limit=30):
    """A flat list for search engines."""
    v = variants(name, kind)
    out = [name]
    for k in ("gendered", "spelling", "equivalents", "forms"):
        out += v.get(k, [])
    if v.get("old_orthography"):
        out.append(v["old_orthography"])
    for x in v.get("latin", {}).values():
        out += x.split(" / ")
    return list(dict.fromkeys(out))[:limit]


__all__ = ["variants", "all_forms", "translit", "old_orthography", "gendered", "spelling", "given_equivalents", "patronymic_forms"]
