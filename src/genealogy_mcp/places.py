"""Where the records of a historical province are kept now. Borders moved (Bessarabia, Galicia, Volhynia, Poland,
the Baltics), so the archive is decided by where the parish, the consistory or the treasury chamber was — not by
today's address. Archive names, not fond numbers: check the fond in the archive's guide (guides.rusarchives.ru,
archives.gov.ua, archives.gov.by) or the FamilySearch catalogue.
"""
import re

P = []   # every entry: id, names (ru, en, other forms), then (empire), now: [(country, region)], archives, note


def add(id, names, then, now, archives, note=""):
    P.append({"id": id, "names": names.split("|"), "then": then, "now": [dict(zip(("country", "region"), x.split(":", 1))) for x in now.split(";")],
              "archives": archives.split(";"), "note": note})


RE = "Russian Empire"
GA = "Государственный архив {} области"
# ---------- European Russia
add("arkhangelsk", "Архангельская губерния|Arkhangelsk|Archangel", RE, "RU:Архангельская область;RU:Республика Коми", GA.format("Архангельской") + ";Национальный архив Республики Коми")
add("astrakhan", "Астраханская губерния|Astrakhan", RE, "RU:Астраханская область;RU:Республика Калмыкия", GA.format("Астраханской"))
add("vladimir", "Владимирская губерния|Vladimir", RE, "RU:Владимирская область;RU:Ивановская область", GA.format("Владимирской") + ";" + GA.format("Ивановской"), "Шуйский, Иваново-Вознесенский и соседние уезды — в Иванове.")
add("vologda", "Вологодская губерния|Vologda", RE, "RU:Вологодская область;RU:Республика Коми;RU:Архангельская область", GA.format("Вологодской") + ";Национальный архив Республики Коми")
add("voronezh", "Воронежская губерния|Voronezh", RE, "RU:Воронежская область;RU:Белгородская область;RU:Липецкая область", GA.format("Воронежской") + ";" + GA.format("Белгородской"))
add("vyatka", "Вятская губерния|Vyatka|Viatka", RE, "RU:Кировская область;RU:Удмуртская Республика", "Центральный государственный архив Кировской области;Центральный государственный архив Удмуртской Республики")
add("don", "Область Войска Донского|Don Host Oblast|Don Cossack", RE, "RU:Ростовская область;RU:Волгоградская область", GA.format("Ростовской") + ";" + GA.format("Волгоградской"), "Казачьи станицы: метрики в фонде Донской духовной консистории (Ростов).")
add("kazan", "Казанская губерния|Kazan", RE, "RU:Республика Татарстан;RU:Чувашская Республика;RU:Республика Марий Эл", "Национальный архив Республики Татарстан;Государственный исторический архив Чувашской Республики")
add("kaluga", "Калужская губерния|Kaluga", RE, "RU:Калужская область", GA.format("Калужской"))
add("kostroma", "Костромская губерния|Kostroma", RE, "RU:Костромская область;RU:Ивановская область", GA.format("Костромской"))
add("kursk", "Курская губерния|Kursk", RE, "RU:Курская область;RU:Белгородская область", GA.format("Курской") + ";" + GA.format("Белгородской"))
add("moscow", "Московская губерния|Moscow|Moskva", RE, "RU:Москва;RU:Московская область", "Центральный государственный архив города Москвы (ЦГИАМ, ф. 203 — метрики консистории);Центральный государственный архив Московской области", "Метрики Москвы частично распознаны в Яндекс Архиве.")
add("nizhny", "Нижегородская губерния|Nizhny Novgorod|Nizhegorod", RE, "RU:Нижегородская область", "Центральный архив Нижегородской области")
add("novgorod", "Новгородская губерния|Novgorod", RE, "RU:Новгородская область;RU:Вологодская область;RU:Ленинградская область;RU:Тверская область", GA.format("Новгородской") + ";" + GA.format("Вологодской"), "Череповецкий и Белозерский уезды — в Вологде.")
add("olonets", "Олонецкая губерния|Olonets", RE, "RU:Республика Карелия;RU:Вологодская область;RU:Ленинградская область", "Национальный архив Республики Карелия")
add("orenburg", "Оренбургская губерния|Orenburg", RE, "RU:Оренбургская область;RU:Челябинская область;RU:Республика Башкортостан", GA.format("Оренбургской") + ";Объединённый государственный архив Челябинской области;Центральный государственный исторический архив Республики Башкортостан")
add("oryol", "Орловская губерния|Oryol|Orel", RE, "RU:Орловская область;RU:Брянская область;RU:Липецкая область", GA.format("Орловской") + ";" + GA.format("Брянской"))
add("penza", "Пензенская губерния|Penza", RE, "RU:Пензенская область;RU:Республика Мордовия", GA.format("Пензенской") + ";Центральный государственный архив Республики Мордовия")
add("perm", "Пермская губерния|Perm", RE, "RU:Пермский край;RU:Свердловская область", "Государственный архив Пермского края;Государственный архив Свердловской области", "Екатеринбургский, Верхотурский, Камышловский, Ирбитский, Шадринский уезды — Екатеринбург (и Курган для Шадринского).")
add("pskov", "Псковская губерния|Pskov", RE, "RU:Псковская область", GA.format("Псковской"))
add("ryazan", "Рязанская губерния|Ryazan", RE, "RU:Рязанская область;RU:Липецкая область", GA.format("Рязанской"))
add("samara", "Самарская губерния|Samara", RE, "RU:Самарская область;RU:Оренбургская область;RU:Ульяновская область", "Центральный государственный архив Самарской области;" + GA.format("Оренбургской"))
add("spb", "Санкт-Петербургская губерния|Saint Petersburg|Petrograd", RE, "RU:Санкт-Петербург;RU:Ленинградская область", "Центральный государственный исторический архив Санкт-Петербурга (ЦГИА СПб, ф. 19 — метрики консистории)")
add("saratov", "Саратовская губерния|Saratov", RE, "RU:Саратовская область;RU:Волгоградская область", GA.format("Саратовской") + ";" + GA.format("Волгоградской"), "Колонии поволжских немцев: метрики лютеранской консистории — ЦГИА СПб и Энгельс (филиал саратовского архива).")
add("simbirsk", "Симбирская губерния|Simbirsk", RE, "RU:Ульяновская область;RU:Чувашская Республика", GA.format("Ульяновской"))
add("smolensk", "Смоленская губерния|Smolensk", RE, "RU:Смоленская область", GA.format("Смоленской"))
add("tambov", "Тамбовская губерния|Tambov", RE, "RU:Тамбовская область;RU:Липецкая область;RU:Республика Мордовия", GA.format("Тамбовской") + ";" + GA.format("Липецкой"))
add("tver", "Тверская губерния|Tver", RE, "RU:Тверская область", GA.format("Тверской"))
add("tula", "Тульская губерния|Tula", RE, "RU:Тульская область", GA.format("Тульской") + " (ГАТО)", "Ревизские сказки Богородицкого уезда расшифрованы энтузиастами (petrovy.su).")
add("ufa", "Уфимская губерния|Ufa", RE, "RU:Республика Башкортостан;RU:Челябинская область", "Центральный государственный исторический архив Республики Башкортостан")
add("yaroslavl", "Ярославская губерния|Yaroslavl", RE, "RU:Ярославская область", GA.format("Ярославской"))
add("stavropol", "Ставропольская губерния|Stavropol", RE, "RU:Ставропольский край", "Государственный архив Ставропольского края")
add("kuban", "Кубанская область|Kuban", RE, "RU:Краснодарский край;RU:Республика Адыгея", "Государственный архив Краснодарского края")
add("tobolsk", "Тобольская губерния|Tobolsk", RE, "RU:Тюменская область;RU:Курганская область;RU:Омская область", "Государственный архив в г. Тобольске;" + GA.format("Курганской") + ";Исторический архив Омской области")
add("tomsk", "Томская губерния|Tomsk", RE, "RU:Томская область;RU:Новосибирская область;RU:Алтайский край;RU:Кемеровская область", GA.format("Томской") + ";Государственный архив Алтайского края")
add("yeniseisk", "Енисейская губерния|Yeniseysk|Yenisei", RE, "RU:Красноярский край;RU:Республика Хакасия", "Государственный архив Красноярского края")
add("irkutsk", "Иркутская губерния|Irkutsk", RE, "RU:Иркутская область", GA.format("Иркутской"))
# ---------- Ukraine
DA = "Державний архів {} області"
add("kiev", "Киевская губерния|Kiev|Kyiv", RE, "UA:Київська область;UA:Черкаська область;UA:Київ", "ЦДІАК України (Київ: метрики консисторії, ревізькі казки);" + DA.format("Київської") + ";" + DA.format("Черкаської"))
add("chernigov", "Черниговская губерния|Chernigov|Chernihiv", RE, "UA:Чернігівська область;UA:Сумська область;RU:Брянская область", DA.format("Чернігівської") + ";" + GA.format("Брянской"), "Стародубский, Новозыбковский, Мглинский, Суражский уезды — сейчас Брянская область.")
add("poltava", "Полтавская губерния|Poltava", RE, "UA:Полтавська область;UA:Черкаська область;UA:Сумська область", DA.format("Полтавської"))
add("kharkov", "Харьковская губерния|Kharkov|Kharkiv", RE, "UA:Харківська область;UA:Сумська область;RU:Белгородская область", DA.format("Харківської"))
add("ekaterinoslav", "Екатеринославская губерния|Ekaterinoslav|Yekaterinoslav|Dnipro", RE, "UA:Дніпропетровська область;UA:Запорізька область;UA:Донецька область", DA.format("Дніпропетровської") + ";" + DA.format("Запорізької") + ";" + DA.format("Донецької"))
add("kherson", "Херсонская губерния|Kherson", RE, "UA:Херсонська область;UA:Миколаївська область;UA:Одеська область;UA:Кіровоградська область", DA.format("Херсонської") + ";" + DA.format("Одеської") + ";" + DA.format("Миколаївської") + ";" + DA.format("Кіровоградської"), "Одесса и немецкие колонии — Одесса.")
add("taurida", "Таврическая губерния|Taurida|Tavria|Crimea", RE, "UA:Автономна Республіка Крим;UA:Запорізька область;UA:Херсонська область", "Державний архів Автономної Республіки Крим;" + DA.format("Запорізької") + ";" + DA.format("Херсонської"))
add("podolia", "Подольская губерния|Podolia|Podillia", RE, "UA:Хмельницька область;UA:Вінницька область;MD:Придністров'я", DA.format("Хмельницької") + ";" + DA.format("Вінницької"), "Подольская консистория была в Каменце-Подольском — метрики в Хмельницком.")
add("volhynia", "Волынская губерния|Volhynia|Volyn", RE, "UA:Житомирська область;UA:Рівненська область;UA:Волинська область;UA:Хмельницька область", DA.format("Житомирської") + ";" + DA.format("Рівненської") + ";" + DA.format("Волинської"), "Волынская консистория — в Житомире; западные уезды в 1921–1939 гг. были в Польше.")
add("galicia", "Галиция|Galicia|Galizien|Galicja", "Austria-Hungary", "UA:Львівська область;UA:Тернопільська область;UA:Івано-Франківська область;PL:Małopolskie;PL:Podkarpackie", "ЦДІАЛ України (Львів: греко-католицькі метрики);Archiwum Główne Akt Dawnych (Warszawa: Zabużański zbiór);Archiwa Państwowe w Przemyślu, Rzeszowie, Krakowie", "Римо-католические книги восточной Галиции — в AGAD (Варшава); греко-католические — в Львове.")
add("bukovina", "Буковина|Bukovina|Bukowina", "Austria-Hungary", "UA:Чернівецька область;RO:Suceava", DA.format("Чернівецької") + ";Arhivele Naționale, Suceava")
add("transcarpathia", "Закарпатье|Подкарпатская Русь|Transcarpathia|Subcarpathian Ruthenia", "Austria-Hungary", "UA:Закарпатська область", DA.format("Закарпатської"), "Записи на венгерском и латыни; см. также Hungaricana.")
# ---------- Belarus, Lithuania, Latvia, Estonia, Moldova
add("minsk", "Минская губерния|Minsk", RE, "BY:Минская область;BY:Гомельская область;BY:Брестская область", "Национальный исторический архив Беларуси (Минск)")
add("vitebsk", "Витебская губерния|Vitebsk|Viciebsk", RE, "BY:Витебская область;LV:Latgale;RU:Псковская область", "Национальный исторический архив Беларуси (Минск);Latvijas Valsts vēstures arhīvs (Rīga) — Латгалия", "Двинский, Режицкий, Люцинский уезды — Латвия (raduraksti).")
add("mogilev", "Могилёвская губерния|Mogilev|Mahilyow", RE, "BY:Могилёвская область;BY:Гомельская область;RU:Смоленская область;RU:Брянская область", "Национальный исторический архив Беларуси (Минск)")
add("grodno", "Гродненская губерния|Grodno|Hrodna", RE, "BY:Гродненская область;BY:Брестская область;PL:Podlaskie", "Национальный исторический архив Беларуси в г. Гродно;Archiwum Państwowe w Białymstoku")
add("vilna", "Виленская губерния|Vilna|Wilno|Vilnius", RE, "LT:Vilniaus apskritis;BY:Гродненская область;BY:Минская область;BY:Витебская область", "Lietuvos valstybės istorijos archyvas (LVIA, Vilnius);Национальный исторический архив Беларуси")
add("kovno", "Ковенская губерния|Kovno|Kaunas", RE, "LT:Lietuva", "Lietuvos valstybės istorijos archyvas (LVIA, Vilnius);Kauno regioninis valstybės archyvas", "Метрики — epaveldas.lt.")
add("courland", "Курляндская губерния|Courland|Kurland", RE, "LV:Kurzeme;LV:Zemgale", "Latvijas Valsts vēstures arhīvs (Rīga)", "Лютеранские и католические книги — raduraksti.arhivi.lv.")
add("livonia", "Лифляндская губерния|Livonia|Livland", RE, "LV:Vidzeme;EE:Lõuna-Eesti", "Latvijas Valsts vēstures arhīvs (Rīga);Rahvusarhiiv (Tartu)", "Северная (эстонская) часть — архив в Тарту (ais.ra.ee).")
add("estland", "Эстляндская губерния|Estland|Estonia", RE, "EE:Eesti", "Rahvusarhiiv (Tallinn, Tartu)")
add("bessarabia", "Бессарабская губерния|Bessarabia|Basarabia", RE, "MD:Moldova;UA:Одеська область", "Agenția Națională a Arhivelor, Chișinău (ф. 211 — Кишинёвская консистория);" + DA.format("Одеської") + " (Ізмаїл, Аккерман)", "В 1918–1940 гг. под Румынией: тогдашние записи гражданского состояния — также румынские архивы.")
# ---------- Kingdom of Poland and other Polish lands
for gid, ru, en, ap in (("warsaw", "Варшавская", "Warsaw", "Warszawie"), ("lublin", "Люблинская", "Lublin", "Lublinie"), ("radom", "Радомская", "Radom", "Radomiu"),
                        ("kielce", "Келецкая", "Kielce", "Kielcach"), ("piotrkow", "Петроковская", "Piotrków", "Piotrkowie Trybunalskim"),
                        ("kalisz", "Калишская", "Kalisz", "Kaliszu"), ("plock", "Плоцкая", "Płock", "Płocku"), ("lomza", "Ломжинская", "Łomża", "Łomży"),
                        ("siedlce", "Седлецкая", "Siedlce", "Siedlcach"), ("suwalki", "Сувалкская", "Suwałki", "Suwałkach")):
    add(gid, f"{ru} губерния|{en}", RE + " (Kingdom of Poland)", "PL:Polska" + (";LT:Lietuva" if gid == "suwalki" else ""),
        f"Archiwum Państwowe w {ap};parish archives (the second copy)" + (";Lietuvos valstybės istorijos archyvas" if gid == "suwalki" else ""),
        "Акты гражданского состояния с 1808/1826 г. ведали священники — две копии: в приходе и в государственном архиве. Индекс — Geneteka, сканы — szukajwarchiwach.gov.pl.")
add("posen", "Познанская провинция|Posen|Poznań", "Prussia", "PL:Wielkopolskie", "Archiwum Państwowe w Poznaniu;Archiwum Archidiecezjalne w Poznaniu", "Индекс браков — Poznań Project.")
add("east_prussia", "Восточная Пруссия|East Prussia|Ostpreußen", "Prussia", "RU:Калининградская область;PL:Warmińsko-mazurskie;LT:Klaipėdos apskritis", "Evangelisches Zentralarchiv in Berlin (церковные книги, Archion);Geheimes Staatsarchiv Preußischer Kulturbesitz;Archiwum Państwowe w Olsztynie", "Многие книги вывезены в Германию; ищите в Archion и каталоге FamilySearch.")
# ---------- Caucasus
add("tiflis", "Тифлисская губерния|Tiflis|Tbilisi", RE, "GE:Georgia", "Национальный архив Грузии (Центральный исторический архив, Тбилиси)", "Метрики армянских церквей — также Национальный архив Армении.")
add("erivan", "Эриванская губерния|Erivan|Yerevan", RE, "AM:Armenia;TR:Iğdır", "Национальный архив Армении (Ереван)")
add("baku", "Бакинская губерния|Baku", RE, "AZ:Azerbaijan", "Государственный исторический архив Азербайджанской Республики (Баку)")

INDEX = {}
for e in P:
    for n in e["names"] + [x["region"] for x in e["now"]]:
        INDEX.setdefault(n.lower(), []).append(e)


def _norm(s):
    s = s.lower().replace("ё", "е").strip()
    s = re.sub(r"\b(губерния|губ\.|gubernia|guberniya|governorate|province|область|обл\.|oblast|край|республика|voivodeship)\b", "", s)
    return " ".join(s.split())


def find(place):
    """'Тульская губерния', 'Tula', 'Бессарабия', 'Хмельницька область' → matching entries."""
    q = _norm(place)
    if not q:
        return []
    out = []
    for e in P:
        keys = [_norm(n) for n in e["names"]] + [_norm(x["region"]) for x in e["now"]]
        if any(q == k or (len(q) >= 4 and (k.startswith(q[:max(4, len(q) - 3)]) or q.startswith(k[:max(4, len(k) - 3)]))) for k in keys if k):
            out.append(e)
    return out
