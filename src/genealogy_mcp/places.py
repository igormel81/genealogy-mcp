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
add("kazan", "Казанская губерния|Kazan", RE, "RU:Республика Татарстан;RU:Чувашская Республика;RU:Республика Марий Эл", "Государственный архив Республики Татарстан;Государственный исторический архив Чувашской Республики")
add("kaluga", "Калужская губерния|Kaluga", RE, "RU:Калужская область", GA.format("Калужской"))
add("kostroma", "Костромская губерния|Kostroma", RE, "RU:Костромская область;RU:Ивановская область", GA.format("Костромской"))
add("kursk", "Курская губерния|Kursk", RE, "RU:Курская область;RU:Белгородская область", GA.format("Курской") + ";" + GA.format("Белгородской"))
add("moscow", "Московская губерния|Moscow|Moskva", RE, "RU:Москва;RU:Московская область", "Центральный государственный архив города Москвы (ЦГИАМ, ф. 203 — метрики консистории);Центральный государственный архив Московской области", "Метрики Москвы частично распознаны в Яндекс Архиве.")
add("nizhny", "Нижегородская губерния|Nizhny Novgorod|Nizhegorod", RE, "RU:Нижегородская область", "Центральный архив Нижегородской области")
add("novgorod", "Новгородская губерния|Novgorod", RE, "RU:Новгородская область;RU:Вологодская область;RU:Ленинградская область;RU:Тверская область", GA.format("Новгородской") + ";" + GA.format("Вологодской"), "Череповецкий и Белозерский уезды — в Вологде.")
add("olonets", "Олонецкая губерния|Olonets", RE, "RU:Республика Карелия;RU:Вологодская область;RU:Ленинградская область", "Национальный архив Республики Карелия")
add("orenburg", "Оренбургская губерния|Orenburg", RE, "RU:Оренбургская область;RU:Челябинская область;RU:Республика Башкортостан", "Объединённый государственный архив Оренбургской области;Объединённый государственный архив Челябинской области;Национальный архив Республики Башкортостан")
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
add("ufa", "Уфимская губерния|Ufa", RE, "RU:Республика Башкортостан;RU:Челябинская область", "Национальный архив Республики Башкортостан")
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
add("galicia", "Галиция|Galicia|Galizien|Galicja", "Austria-Hungary", "UA:Львівська область;UA:Тернопільська область;UA:Івано-Франківська область;PL:Małopolskie;PL:Podkarpackie", "ЦДІАЛ України (Львів: греко-католицькі метрики);Archiwum Główne Akt Dawnych (Warszawa: Zabużański zbiór);Archiwa Państwowe w Przemyślu, Rzeszowie, Krakowie", "Римо-католические книги восточной Галиции — в AGAD (Варшава); греко-католические — в ЦДІАЛ (Львов), а также в AGAD (ф. 298).")
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
add("bessarabia", "Бессарабская губерния|Bessarabia|Basarabia", RE, "MD:Moldova;UA:Одеська область", "Agenția Națională a Arhivelor, Chișinău (ф. 211 — Кишинёвская консистория);" + DA.format("Одеської") + " (Ізмаїл, Аккерман)", "Юг (Кагул, Измаил, Болград) в 1857–1878 гг. — в Молдавском княжестве, затем Румынии (Парижский мир 1856 г. — Берлинский конгресс 1878 г.); вся Бессарабия в 1918–1940 и 1941–1944 гг. — под Румынией: записи этих лет — также в румынских архивах. Укажите год (year), чтобы узнать страну и архив.")
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
add("erivan", "Эриванская губерния|Erivan|Yerevan", RE, "AM:Armenia;AZ:Naxçıvan;TR:Iğdır", "Национальный архив Армении (Ереван)")
add("baku", "Бакинская губерния|Baku", RE, "AZ:Azerbaijan", "Государственный исторический архив Азербайджанской Республики (Баку)")

# ---------- Siberia and the Far East
add("transbaikal", "Забайкальская область|Transbaikal|Zabaykalsky", RE, "RU:Забайкальский край;RU:Республика Бурятия", "Государственный архив Забайкальского края;Государственный архив Республики Бурятия", "Забайкальские казаки — в фонде войскового хозяйственного правления.")
add("amur", "Амурская область|Amur", RE, "RU:Амурская область", GA.format("Амурской") + ";Российский государственный исторический архив Дальнего Востока (Владивосток)")
add("primorye", "Приморская область|Primorye|Maritime oblast", RE, "RU:Приморский край;RU:Хабаровский край", "Государственный архив Приморского края;Государственный архив Хабаровского края;Российский государственный исторический архив Дальнего Востока (Владивосток)")
add("yakutsk", "Якутская область|Yakutsk|Yakutia", RE, "RU:Республика Саха (Якутия)", "Национальный архив Республики Саха (Якутия)")
# ---------- Central Asia (Steppe and Turkestan governorates-general)
CA = "Центральный государственный архив Республики {}"
add("akmolinsk", "Акмолинская область|Akmolinsk|Akmola", RE, "KZ:Акмолинская, Северо-Казахстанская, Карагандинская области;RU:Омская область", CA.format("Казахстан") + " (Алматы);Исторический архив Омской области", "Управление Степного генерал-губернаторства было в Омске — часть дел в Омске.")
add("semipalatinsk", "Семипалатинская область|Semipalatinsk|Semey", RE, "KZ:Абайская и Восточно-Казахстанская области", CA.format("Казахстан") + " (Алматы);Государственный архив области Абай (Семей)")
add("turgai", "Тургайская область|Turgai|Torgay", RE, "KZ:Костанайская и Актюбинская области", CA.format("Казахстан") + " (Алматы);Объединённый государственный архив Оренбургской области", "Управление области было в Оренбурге.")
add("uralsk", "Уральская область|Uralsk|Oral", RE, "KZ:Западно-Казахстанская и Атырауская области", CA.format("Казахстан") + " (Алматы);Государственный архив Западно-Казахстанской области", "Уральские казаки — в фондах Уральского казачьего войска.")
add("semirechye", "Семиреченская область|Semirechye|Zhetysu", RE, "KZ:Алматинская и Жетысуская области;KG:Чуйская и Иссык-Кульская области", CA.format("Казахстан") + " (Алматы);Центральный государственный архив Кыргызской Республики (Бишкек)", "Метрики переселенческих сёл частично на FamilySearch.")
add("syr_darya", "Сырдарьинская область|Syr-Darya|Syr Darya", RE, "UZ:Ташкент и Ташкентская область;KZ:Туркестанская и Кызылординская области", "Национальный архив Узбекистана (Ташкент)", "Туркестанская епархия и генерал-губернаторство — в Ташкенте.")
add("fergana", "Ферганская область|Fergana", RE, "UZ:Ферганская долина;KG:Ошская и Джалал-Абадская области;TJ:Согдийская область", "Национальный архив Узбекистана (Ташкент)")
add("samarkand", "Самаркандская область|Samarkand", RE, "UZ:Самаркандская, Джизакская области;TJ:Согдийская область", "Национальный архив Узбекистана (Ташкент)")
add("transcaspian", "Закаспийская область|Transcaspian|Zakaspiyskaya", RE, "TM:Туркменистан;KZ:Мангистауская область", "Центральный государственный архив Туркменистана (Ашхабад);" + "Национальный архив Узбекистана (Ташкент)", "Ашхабадский архив пострадал при землетрясении 1948 г.; ищите дубликаты в Ташкенте и РГВИА.")

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
    if not out:   # a whole country: every province now (partly) in it
        from .sources import COUNTRY_NAMES
        code = COUNTRY_NAMES.get(q) or (q.upper() if re.fullmatch(r"[a-z]{2}", q) else None)
        if code and len(code) == 2:
            out = [e for e in P if any(x["country"] == code for x in e["now"])]
    return out


# ---------------------------------------------------------------- Bessarabia: whose land it was in a given year
# Treaty of Paris (30 March 1856): the south of Bessarabia went to the Principality of Moldavia (handed over in 1857),
# from 1859 the United Principalities, later Romania; Treaty of Berlin (13 July 1878): back to Russia (taken over in
# October 1878). Bessarabia as a whole: Romania 1918–1940 and 1941–1944, the USSR from 28 June 1940 and from 1944.
ANRM = "Agenția Națională a Arhivelor — Arhiva Națională a Republicii Moldova (Chișinău): fond of the Kishinev consistory (f. 211), uezd and volost fonds"
IZMAIL = "Izmail branch of the State Archive of Odesa Region (Ізмаїл; the former archive of Izmail oblast, 1940–1954)"
ODESA = "Державний архів Одеської області (Odesa)"
RO_ARCH = "Arhivele Naționale ale României — county directorates (Galați for the Lower Danube diocese, Iași for the central institutions of Moldavia)"
CIVIL_MD = "Civil registry (stare civilă) of the Republic of Moldova — records younger than about 100 years"
CIVIL_UA = "Civil registry offices of Ukraine (відділи ДРАЦС) — records younger than about 75–100 years"

SOUTH = {   # district → names, today, archives now
    "cahul": ("Cahul|Кагул|Кагульский|Кагульский уезд|Kagul|Кахул", "MD", "Cahul district, Moldova", [ANRM]),
    "ismail": ("Ismail|Izmail|Измаил|Измаильский|Измаильский уезд|Ізмаїл|Ізмаїльський|Reni|Рени|Рені|Kiliya|Chilia|Килия|Кілія|Vylkove|Вилково",
               "UA", "Izmail district, Odesa region, Ukraine", [IZMAIL, ANRM]),
    "bolgrad": ("Bolgrad|Bolhrad|Болград|Болградский|Болградський", "UA", "Bolhrad district, Odesa region, Ukraine", [IZMAIL, ODESA, ANRM]),
}
PERIODS = [   # (from, to, south only, state, unit in the south, unit elsewhere in Bessarabia, note)
    (1812, 1856, False, "Russian Empire", "Bessarabia oblast", "Bessarabia oblast",
     "Orthodox registers: the Kishinev consistory. The Bulgarian and Gagauz colonies of the south (Bolgrad and its colonies) "
     "were run by the Guardianship Committee for Foreign Settlers of Southern Russia, whose papers are in Odesa."),
    (1857, 1878, True, "Principality of Moldavia (1857–1859), then the United Principalities / Romania",
     "counties of Cahul and Ismail, from the 1860s also Bolgrad", "",
     "Ceded by the Treaty of Paris (1856), handed over in 1857, returned to Russia by the Treaty of Berlin (1878; taken over "
     "in October 1878). The churches came under the Moldavian church, from 1864 the Diocese of the Lower Danube (seat in "
     "Ismail, after 1878 in Galați); civil registration by the town halls began with the Romanian Civil Code (December 1865). "
     "Registers of these years are usually not in the Kishinev consistory's fond: look in the archives of the territory "
     "(Chișinău, Izmail) and in the Romanian National Archives."),
    (1857, 1917, False, "Russian Empire", "", "Bessarabia oblast, from 1873 Bessarabia governorate",
     "Orthodox registers: the second copies in the Kishinev consistory's fond."),
    (1878, 1917, True, "Russian Empire", "Izmail uezd of Bessarabia governorate (Cahul and Bolgrad were in it)", "",
     "Orthodox registers: the second copies in the Kishinev consistory's fond; the first copies stayed in the churches."),
    (1918, 1940, False, "Romania", "counties of Cahul and Ismail (Bolgrad in Ismail county)", "Romanian counties (județe) of Bessarabia",
     "Romanian civil registration (stare civilă) at the town halls, in Romanian; the churches kept registers too. Part of "
     "the archives was evacuated to Romania in 1940 and 1944."),
    (1940, 1941, False, "USSR (from 28 June 1940)",
     "Cahul: Moldavian SSR; Izmail and Bolgrad: Akkerman oblast, renamed Izmail oblast in December 1940 (Ukrainian SSR)",
     "Moldavian SSR; the north (Khotin) and the south (Akkerman, Izmail): Ukrainian SSR",
     "Soviet civil registration (ZAGS); the deportations of June 1941."),
    (1941, 1944, False, "Romania", "counties of Cahul and Ismail (Governorate of Bessarabia)", "Governorate of Bessarabia (Romanian counties)",
     "Romanian civil registration again; for war losses look in Romanian as well as Soviet military records."),
    (1944, 1991, False, "USSR", "Cahul: Moldavian SSR; Izmail and Bolgrad: Izmail oblast (to 1954), then Odesa oblast (Ukrainian SSR)",
     "Moldavian SSR; the north and the south: Ukrainian SSR", "Soviet civil registration (ZAGS); the deportations of 1949 and 1951."),
    (1992, 2100, False, "Moldova / Ukraine", "Cahul: Republic of Moldova; Izmail and Bolgrad: Odesa region of Ukraine",
     "Republic of Moldova; the north and the south: Ukraine", ""),
]
BORDER_YEARS = {1856: "the Treaty of Paris (30 March 1856); the handover came in 1857",
                1857: "the south was handed over to Moldavia during 1857",
                1878: "the Treaty of Berlin (13 July 1878); Russia took the south over in October 1878",
                1918: "union with Romania (spring 1918)", 1940: "the Soviet annexation on 28 June 1940",
                1941: "Romanian rule again from July 1941", 1944: "the Soviet army returned in spring–summer 1944"}


def _plain(s):
    s = str(s or "").lower().replace("ё", "е")
    for a, b in (("ă", "a"), ("â", "a"), ("î", "i"), ("ș", "s"), ("ş", "s"), ("ț", "t"), ("ţ", "t")):
        s = s.replace(a, b)
    return s


def south_district(*texts):
    """'Болград', 'Izmail district', 'Кагульский уезд' → 'bolgrad' / 'ismail' / 'cahul' (or None)."""
    words = re.findall(r"\w+", " ".join(_plain(t) for t in texts))
    for key, (names, *_rest) in SOUTH.items():
        for n in names.split("|"):
            name = _plain(n).split()[0]
            stem = name[:-1] if len(name) >= 6 else name
            if any(w.startswith(stem) and len(w) <= len(name) + 7 for w in words):
                return key
    return None


def bessarabia_in(year, district=None):
    """Whose land a place of Bessarabia was in a year, its unit then, and the archives to look in now."""
    y = int(year)
    if y < 1812:
        return {"year": y, "state": "Principality of Moldavia (the Budjak in the south: Ottoman)",
                "note": "Before 1812: Moldavian and Ottoman administration; the earliest name lists are the Moldavian "
                        "censuses of 1772–1774 (find_sources: dmitriev_1772)."}
    south = district in SOUTH
    rows = [r for r in PERIODS if r[0] <= y <= r[1]]
    special = [r for r in rows if r[2]]
    general = [r for r in rows if not r[2]]
    r = special[0] if south and special else general[-1]
    out = {"year": y, "state": r[3], "unit": r[4] if south else r[5], "note": r[6]}
    if y in BORDER_YEARS and (south or y not in (1856, 1857, 1878)):
        out["border_year"] = (f"{y} is a border year — {BORDER_YEARS[y]}. Check in the record itself which authority, "
                              "language and calendar it uses.")
    if south:
        names, country, now, archives = SOUTH[district]
        arch = list(archives)
        if 1857 <= y <= 1878:
            arch.append(RO_ARCH)
        if 1918 <= y <= 1944:
            arch.append("Arhivele Naționale ale României (records evacuated in 1940 and 1944)")
        if y >= 1920:
            arch.append(CIVIL_MD if country == "MD" else CIVIL_UA)
        out.update({"district": names.split("|")[0], "now": now, "archives": arch})
    elif 1918 <= y <= 1944:
        out["archives"] = [ANRM, "Arhivele Naționale ale României (records evacuated in 1940 and 1944)"]
    return out


# ---------------------------------------------------------------- which church kept a village's books
# Only attachments with a source. A village without its own church was recorded in a neighbouring village's church,
# and the attachment changed when churches were built or parishes reorganised: always give the years and the source.
PARISHES = [
    {"village": ["Porumbești", "Porumbeşti", "Porumbesti", "Порумбешть"], "church_village": "Leca", "church_village_ru": "Лека",
     "years": None, "region": "Bessarabia",
     "source": "Registers of the church of Leca record Porumbești (found in research for genealogy-mcp issue #8)",
     "note": "Years not established: check the clergy registers and the consistory inventory for the period you need."},
    {"village": ["Sadâc", "Sadîc", "Sadac", "Садык"], "church_village": "Capaclia Nouă", "church_village_ru": "Капаклия-Ноуэ",
     "years": None, "region": "Bessarabia",
     "source": "Registers of the church of Capaclia Nouă record Sadâc (found in research for genealogy-mcp issue #8)",
     "note": "Years not established: check the clergy registers and the consistory inventory for the period you need."},
]


def parish_of(village, year=None):
    """Recorded attachments of a village to a church (with years and source)."""
    q = _plain(village).strip()
    q = re.sub(r"^(с\.|село|д\.|деревня|satul|village of)\s+", "", q)
    q = q.split(",")[0].split()[0] if q else ""
    out = []
    for e in PARISHES:
        if any(_plain(n) == q for n in e["village"]):
            y = e.get("years")
            if year and y and not (y[0] <= int(year) <= y[1]):
                continue
            out.append(e)
    return out


def parish_guide(lang="en"):
    if lang == "ru":
        return [
            "Метрики ведёт церковь, а не село: в селе без своего храма записи — в книгах церкви соседнего села (приписное село), "
            "и приписка менялась, когда строили церкви или перекраивали приходы. Ищите приход на нужный год.",
            "Клировые ведомости: за каждый год — церковь и все приписанные к ней сёла.",
            "Описи фонда духовной консистории (для Бессарабии — Национальный архив Молдовы, ф. 211, описи по уездам): книги "
            "по церквям с перечнем сёл.",
            "Справочники: «Списки населённых мест», епархиальные справочники и «Кишинёвские епархиальные ведомости», "
            "работы И. Н. Халиппы о сёлах Бессарабии.",
            "Сама книга: в итоговой ведомости в конце года и в каждой записи названо село родителей — читайте записи "
            "приписного села в книге соседней церкви.",
            "Запишите приписку с годами и источником (project_coverage: поле villages у книги прихода).",
        ]
    return [
        "Registers were kept by the church, not the village: a village without its own church was recorded in the books of a "
        "neighbouring village's church, and the attachment changed as churches were built and parishes reorganised. Find the "
        "parish for the year you need.",
        "Clergy registers (клировые ведомости) list, year by year, each church and the villages attached to it.",
        "Inventories of the consistory fond (for Bessarabia: National Archives of Moldova, f. 211, inventories by uezd) list "
        "the books by church with their villages.",
        "Gazetteers: lists of settlements (Списки населённых мест), diocesan reference books and the Kishinev diocesan gazette, "
        "I. N. Halippa's works on the villages of Bessarabia.",
        "The book itself: the end-of-year summary and every entry name the parents' village — read the attached village's "
        "entries in the neighbouring church's book.",
        "Record the attachment with its years and source (project_coverage: the villages field of the parish's book).",
    ]
