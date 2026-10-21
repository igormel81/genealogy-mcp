"""Parent hypotheses from a patronymic. A patronymic names the father's given name, not the father: in a village with
three Ivans it does not say which one. But a working hypothesis is how research moves on — so this ranks candidates by
patronymic, place and dates, lists the arguments for and against, says which record would settle it and warns about
namesakes from a neighbouring village. The result is always a hypothesis, never a link in the tree."""
import re

from . import evidence

PATRONYMIC = re.compile(r"(?i)(ович|евич|овна|евна|ична|инична|ич)(?:а|у|ем)?$")


def father_names(patronymic):
    """Петрович → Пётр/Петр; Васильевич → Василий; Андреевич → Андрей; Ильич → Илья; Кузьминична → Кузьма."""
    p = str(patronymic or "").strip()
    if not p:
        return []
    low = p.lower().replace("ё", "е")
    low = re.sub(r"(а|у|ем)$", "", low) if re.search(r"(вича|вичу|вичем)$", low) else low
    out = []
    m = re.match(r"(.+?)(инична|инишна)$", low) or re.match(r"(.+?)(ич|ична|ишна)$", low)
    if m and re.search(r"(ов|ев)$", m[1]):
        m = None
    if m:   # Ильич → Илья, Лукич → Лука, Кузьминична → Кузьма
        s = m[1]
        out.append(s + "я" if s.endswith("ь") else s + "а")
    m = re.match(r"(.+?)(евич|евна)$", low)
    if m:   # Васильевич → Василий, Андреевич → Андрей
        s = m[1]
        out.append(s[:-1] + "ий" if s.endswith("ь") else s + "й" if s[-1:] in "аеиоуэюя" else s)
    elif re.match(r"(.+?)(ович|овна)$", low):   # Петрович → Петр
        out.append(re.match(r"(.+?)(ович|овна)$", low)[1])
    elif re.match(r"(.+?)(ов|ев|ин)(а)?( сын| дочь)?$", low) and not out:   # the old short form: Петров сын
        out.append(re.match(r"(.+?)(ов|ев|ин)", low)[1])
    m = re.match(r"(.+?)(ovich|ovitch|owitsch|ovna|evich|evitch|evna|ich|ichna)$", low)
    if m and not out:   # Latin: Ivanovich → Ivan, Vasilievich → Vasili, Andreevna → Andrei, Ilyich → Ilya
        s = m[1]
        out.append(s + "a" if m[2] in ("ich", "ichna") else s.rstrip("i") + "i" if m[2].startswith("ev") else s)
    out = [x[:1].upper() + x[1:] for x in out if len(x) > 1]
    return list(dict.fromkeys(out))


def _given_match(father_forms, given):
    if not given:
        return None
    g = evidence._forms(given, "given")
    return any(evidence._forms(f, "given") & g for f in father_forms)


def _y(v):
    return evidence._year(v)


def _same_surname(a, b):
    return evidence._name_match(a, b, "surname")


def _place(a, b):
    return evidence._place_match(a, b)


def assess(child, candidate, father_forms, lang="en"):
    ru = lang == "ru"
    pro, con, warn, tags = [], [], [], []
    by = _y(child.get("birth_year"))
    cb, cd = _y(candidate.get("birth_year")), _y(candidate.get("death_year"))
    sex = str(candidate.get("sex", "M")).upper()[:1]

    gm = _given_match(father_forms, candidate.get("given"))
    if gm is True:
        pro.append("the patronymic fits the given name" if not ru else "отчество соответствует имени")
        tags.append("patronymic")
    elif gm is False:
        con.append("the patronymic does not fit the given name" if not ru else "отчество не соответствует имени")
    sm = _same_surname(child.get("surname"), candidate.get("surname"))
    if sm is True:
        pro.append("same surname (in some spelling)" if not ru else "та же фамилия (в каком-то написании)")
        tags.append("surname")
    elif sm is False:
        con.append("another surname — possible only if surnames were not yet fixed or one of them is a nickname"
                   if not ru else "другая фамилия — возможно, только если фамилии ещё не устоялись или одна из них прозвище")
    pm = _place(child.get("place"), candidate.get("place"))
    if pm is True:
        pro.append("same village" if not ru else "то же село")
        tags.append("village")
    elif pm is False:
        warn.append(("a namesake from another village: the same given name and surname in a neighbouring village are common — "
                     "it needs a record that links the villages (a move, a marriage, the same household in a revision list)")
                    if not ru else
                    ("однофамилец из другого села: те же имя и фамилия в соседнем селе — обычное дело; нужна запись, которая "
                     "связывает сёла (переезд, брак, тот же двор в ревизской сказке)"))
    if by and cb:
        gap = by - cb
        lo, hi = (18, 60) if sex != "F" else (16, 46)
        if gap < lo - 2 or gap > hi + 5:
            con.append((f"age at the child's birth: {gap} — outside {lo}–{hi}" if not ru else
                        f"возраст при рождении ребёнка: {gap} — вне {lo}–{hi}"))
        else:
            pro.append((f"age at the child's birth: {gap}" if not ru else f"возраст при рождении ребёнка: {gap}"))
            tags.append("age")
    if by and cd and cd < by - 1:
        con.append((f"died in {cd}, before the child was born ({by})" if not ru else f"умер в {cd} г., до рождения ребёнка ({by})"))
    # naming after the grandfather: a son of the child named like the candidate
    grandsons = [x for x in (child.get("children_given") or []) if x]
    if candidate.get("given") and any(_given_match([candidate["given"]], g) for g in grandsons):
        pro.append(("a son of the child bears the candidate's name (grandsons were often named after a grandfather) — a weak clue"
                    if not ru else "сын ребёнка носит имя кандидата (внуков часто называли в честь деда) — слабый довод"))
        tags.append("grandson")
    # godparents and sureties from the candidate's family
    for role, people in (("godparents", child.get("godparents")), ("sureties", child.get("sureties"))):
        for person in people or []:
            text = str(person).strip()
            if text and candidate.get("surname") and _same_surname(text.split()[-1], candidate["surname"]):
                pro.append((f"{'a godparent' if role == 'godparents' else 'a surety at the marriage'} with the candidate's surname: {text} — families chose their own kin; a weak clue"
                            if not ru else
                            f"{'крёстный' if role == 'godparents' else 'поручитель на свадьбе'} с фамилией кандидата: {text} — брали своих; слабый довод"))
                if "godparent" not in tags:
                    tags.append("godparent")
    kids = candidate.get("children") or []
    if child.get("given") and any(_given_match([k], child["given"]) for k in kids):
        pro.append(("a record of the candidate's household lists a child of this name — the strongest clue here; cite it"
                    if not ru else "в записи о семье кандидата есть ребёнок с этим именем — самый сильный довод; сошлитесь на неё"))
        tags.append("household")
    impossible = gm is False or any(("before the child was born" in c or "до рождения" in c or "outside" in c or "вне " in c)
                                    for c in con)
    weights = {"patronymic": 2, "surname": 1, "village": 2, "age": 1, "grandson": 1, "godparent": 1, "household": 3}
    score = sum(weights[k] for k in tags) - 2 * len(warn)
    level = "against" if impossible else "strong" if score >= 7 and not warn else "moderate" if score >= 4 else "weak"
    return {"candidate": candidate, "level": level, "for": pro, "against": con, "warnings": warn}


def hypothesis(child, candidates=None, lang="en"):
    ru = lang == "ru"
    child = dict(child or {})
    father_forms = father_names(child.get("patronymic"))
    if child.get("father_given"):
        father_forms = list(dict.fromkeys([child["father_given"]] + father_forms))
    if not father_forms:
        raise ValueError("give the child's patronymic (Петрович, Ivanovna) or the father's given name as recorded")
    rows = [assess(child, c, father_forms, lang) for c in (candidates or [])]
    order = {"strong": 0, "moderate": 1, "weak": 2, "against": 3}
    rows.sort(key=lambda r: (order[r["level"]], -len(r["for"])))
    viable = [r for r in rows if r["level"] != "against"]
    notes = []
    if len(viable) > 1 and viable[0]["level"] == viable[1]["level"]:
        notes.append(("Several candidates fit equally: the name and the place cannot choose between them. Keep all as open leads."
                      if not ru else "Несколько кандидатов подходят одинаково: имя и место не выбирают между ними. Держите всех как открытые наводки."))
    settle = ([
        "The child's birth or baptism record: it names the father (and usually the mother) — the record that settles it.",
        "A revision list, confession list or census where the child is listed in the candidate's household as a son or daughter.",
        "The child's marriage record if it names the father ('son of …'), and the sureties — often the groom's or bride's kin.",
        "Records of the candidate's other children: the same mother and the same household confirm the family.",
    ] if not ru else [
        "Запись о рождении или крещении ребёнка: в ней назван отец (и обычно мать) — она и решит вопрос.",
        "Ревизская сказка, исповедная ведомость или перепись, где ребёнок записан в дворе кандидата сыном или дочерью.",
        "Запись о браке ребёнка, если в ней назван отец («сын такого-то»), и поручители — часто родня жениха или невесты.",
        "Записи о других детях кандидата: та же мать и тот же двор подтверждают семью.",
    ])
    rule = ("A hypothesis, not a link: do not attach the parent in the tree. Save it as an open lead (project_save kind='lead') "
            "or write 'probably' in the notes, with the arguments, until a record above confirms it (check_match)."
            if not ru else
            "Это гипотеза, а не связь: не связывайте родителя в древе. Сохраните её открытой наводкой (project_save kind='lead') "
            "или с пометкой «вероятно» в заметках, с доводами, пока запись из списка выше её не подтвердит (check_match).")
    out = {"status": "hypothesis", "father_given_from_patronymic": father_forms, "candidates": rows, "settle_with": settle,
           "rule": rule}
    if not candidates:
        out["find_candidates"] = (
            f"Look for men named {' / '.join(father_forms[:3])} in the same village (and the next ones) who were 18–60 when "
            "the child was born: revision lists, confession lists, the baptisms of the child's siblings. Then call again with "
            "them as candidates." if not ru else
            f"Ищите мужчин по имени {' / '.join(father_forms[:3])} в том же селе (и соседних), которым при рождении ребёнка "
            "было 18–60 лет: ревизские сказки, исповедные ведомости, крещения братьев и сестёр ребёнка. Потом вызовите снова "
            "с ними как кандидатами.")
    if viable:
        best = viable[0]
        c = best["candidate"]
        who = " ".join(x for x in (c.get("given"), c.get("surname")) if x) or c.get("id", "?")
        out["lead"] = {"title": (f"Is {who} the father of {child.get('given', '')} {child.get('surname', '')}? (hypothesis: {best['level']})"
                                 if not ru else f"{who} — отец {child.get('given', '')} {child.get('surname', '')}? (гипотеза: {best['level']})").replace("  ", " "),
                       "record": settle[0], "next": settle[0], "checked": None, "status": "open",
                       **({"person_id": child["id"]} if child.get("id") else {})}
    if notes:
        out["notes"] = notes
    return out


__all__ = ["hypothesis", "father_names"]
