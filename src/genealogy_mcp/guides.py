"""How to read the records: what each kind of document holds, where it is kept, how to find it and its traps.
Plus a glossary of the old Russian terms that stop people reading their own ancestors' documents."""

GUIDES = {
    "metric_book": {
        "title": ("Parish registers of the Russian Empire (метрические книги)", "Метрические книги"),
        "en": """**What:** the yearly parish register of births/baptisms, marriages and deaths/burials, kept from the 1720s (widely from
the 1780s) until 1918–1920 by every Orthodox parish; Catholic, Lutheran, Jewish (from 1835), Old Believer and Muslim
communities kept their own. Two copies: one stayed in the church, the other went to the consistory — that copy is the
one usually surviving in the regional archive.

**Columns.** Births: number, date of birth and baptism (both Julian), name of the child, parents with estate and place
(«Тульской губернии, Богородицкого уезда, села Сынкова крестьянин Петр Иванов и законная жена его Анна Васильева» —
the mother's patronymic only, not her maiden name), godparents (often relatives!), who baptised. Marriages: groom and
bride with estate, age and «которым браком» (first or second marriage), witnesses («поручители»). Deaths: name, age,
cause, where buried. Illegitimate children: «незаконнорожденный», mother only.

**Where:** the regional state archive (fond of the spiritual consistory; for Moscow — ЦГИАМ ф. 203), FamilySearch
images (catalogue by place), Yandex Archive for Moscow region, local ZAGS archives for 1918+.

**How:** find the parish first (one parish covered several villages: «приход» lists in the memorial books of the
province). Then read every year around the expected date: the child's age in later records drifts by years. Write
down godparents and witnesses: they show the family's circle and often are siblings.

**Traps:** the surname is often missing in villages before the 1860s — people are «Петр Иванов» (son of Ivan); the
village and the household tell who is who. Ages at death are rounded. Dates are Julian (+12 days in the 19th century).""",
        "ru": """**Что это:** ежегодная церковная книга о рождениях и крещениях, браках, смертях и погребениях. Велась с 1720-х (повсеместно
с 1780-х) до 1918–1920 гг. каждым православным приходом; свои книги вели католики, лютеране, иудеи (с 1835 г.),
старообрядцы и мусульмане. Два экземпляра: один в церкви, второй — в консистории; сохранился чаще всего второй, он в
областном архиве.

**Графы.** Рождения: номер, дата рождения и крещения (обе по старому стилю), имя младенца, родители с сословием и местом
(«Тульской губернии, Богородицкого уезда, села Сынкова крестьянин Петр Иванов и законная жена его Анна Васильева» — у
матери только отчество, девичьей фамилии нет), восприемники (часто родственники!), кто крестил. Браки: жених и невеста
с сословием, возрастом и «которым браком», поручители. Смерти: имя, возраст, причина, где погребён.
Незаконнорождённые — «незаконнорожденный», указана только мать.

**Где:** областной госархив (фонд духовной консистории; для Москвы — ЦГИАМ ф. 203), сканы на FamilySearch
(каталог по месту), Яндекс Архив для Москвы и области, архивы ЗАГС для 1918 г. и позже.

**Как:** сначала найдите приход (к одной церкви относились несколько деревень — списки приходов в памятных книжках
губерний). Потом читайте все годы вокруг ожидаемой даты: возраст в поздних документах «гуляет» на годы. Выписывайте
восприемников и поручителей — это круг семьи, часто братья и сёстры.

**Ловушки:** у крестьян до 1860-х часто нет фамилии — «Петр Иванов» значит «сын Ивана»; кто есть кто, видно по деревне
и двору. Возраст умерших округлён. Даты по старому стилю (в XIX веке +12 дней).""",
    },
    "confession_list": {
        "title": ("Confession lists (исповедные ведомости)", "Исповедные ведомости"),
        "en": """**What:** a yearly list of every parishioner, household by household, made for Lent confession (1700s–1917).
Each household: the head, wife, children, daughters-in-law, grandchildren, with ages and marks «был/не был у исповеди».

**Why it matters:** it reconstructs whole households across years even where the parish register is lost; the
daughter-in-law's place in the household shows a marriage; a person disappearing between two years points to a death or
a move. Ages are approximate.

**Where:** regional archives, consistory fond; FamilySearch has many (catalogue → place → «Исповедные ведомости»).

**How:** go year by year (or every 5 years) and track one household; compare with revision lists for the same years.""",
        "ru": """**Что это:** ежегодный список всех прихожан по дворам, составлявшийся к Великому посту (XVIII в. — 1917 г.). Для каждого
двора — глава, жена, дети, снохи, внуки с возрастом и пометками «был/не был у исповеди».

**Зачем:** восстанавливает дворы целиком за много лет, даже если метрики пропали; сноха во дворе показывает брак;
человек, исчезнувший между двумя годами, — смерть или переезд. Возраст приблизительный.

**Где:** областные архивы, фонд консистории; многое есть на FamilySearch (каталог → место → «Исповедные ведомости»).

**Как:** идите год за годом (или через 5 лет) за одним двором; сверяйте с ревизскими сказками тех же лет.""",
    },
    "revision_list": {
        "title": ("Revision lists of the Russian Empire (ревизские сказки), 1719–1858", "Ревизские сказки (1719–1858)"),
        "en": """**What:** ten tax censuses (revisions): 1719, 1744–1747, 1762–1763, 1782, 1795, 1811, 1815–1816, 1833–1834, 1850, 1857–1858. Each lists the
taxable population of a village household by household: men with ages «at the last revision» and now, who died or left
and when; women are recorded from the 3rd revision (1762–1763), except the 6th (1811).
These are commonly cited dates; individual books and supplementary returns can have later dates.

**Why it matters:** the only source that links a family across a century: «Иван Петров, 40, at the last revision 32;
his son Семен, 12». With revisions you can go from the 1858 village back to the 1700s.

**Where:** regional archives (fond of the treasury chamber, «казенная палата»), RGADA for 1719–1763; FamilySearch
collection 2432393 (unindexed images by district). Volunteer transcriptions exist for some districts (e.g. petrovy.su
for Bogoroditsk district, Tula).

**How:** know the owner (landlord) or category (state peasants) of the village in that year — the books are arranged
by owner, not by village. Landlord villages often changed owners; memorial books and «Списки населённых мест» help.

**Traps:** ages are given «at the last revision», so subtract the right interval. Surnames of serfs are rare before 1858.""",
        "ru": """**Что это:** десять податных переписей (ревизий): 1719, 1744–1747, 1762–1763, 1782, 1795, 1811, 1815–1816, 1833–1834, 1850, 1857–1858 гг.
Население деревни по дворам: мужчины с возрастом «по прошлой ревизии» и теперь, кто и когда умер или выбыл; женщины —
с 3-й ревизии (1762–1763), кроме 6-й (1811).
Здесь приведены основные даты; отдельные книги и дополнительные сказки могут быть датированы позже.

**Зачем:** единственный источник, связывающий семью через столетие: «Иван Петров, 40, по прошлой ревизии 32; у него сын
Семен, 12». По ревизиям можно пройти от деревни 1858 г. до XVIII века.

**Где:** областные архивы (фонд казённой палаты), РГАДА для 1719–1763 гг.; FamilySearch, коллекция 2432393 (сканы
без индекса, по уездам). Для некоторых уездов есть расшифровки энтузиастов (petrovy.su — Богородицкий уезд).

**Как:** узнайте владельца (помещика) или категорию (государственные крестьяне) деревни на тот год — книги разложены
по владельцам, а не по деревням. Владельцы менялись; помогают памятные книжки и «Списки населённых мест».

**Ловушки:** возраст «по прошлой ревизии» — вычитайте верный промежуток. Фамилий у крепостных до 1858 г. почти нет.""",
    },
    "household_book": {
        "title": ("Soviet household books (похозяйственные книги), 1934–", "Похозяйственные книги (с 1934 г.)"),
        "en": """**What:** village-council registers of every rural household, renewed every 3–5 years: members with birth years,
relation to the head, departures (army, town, death) with dates, land and livestock. Earlier analogues: 1920s
household cards and the 1917 agricultural census cards (подворные карточки).

**Where:** municipal (district) archives, sometimes regional; 1917 cards — regional archives (e.g. GATO fond of the
statistics department); not online as a rule.

**How:** request by village council and years; they are the best source for rural families 1930s–1990s, including who
went to war.""",
        "ru": """**Что это:** книги сельсовета по каждому двору, обновлялись раз в 3–5 лет: члены семьи с годами рождения, родство с главой,
выбытие (армия, город, смерть) с датами, земля и скот. Раньше — подворные карточки 1920-х и карточки
сельскохозяйственной переписи 1917 г.

**Где:** муниципальные (районные) архивы, иногда областные; карточки 1917 г. — областные архивы (например, ГАТО, фонд
статистического отдела). В сети, как правило, нет.

**Как:** запрос по сельсовету и годам; лучший источник по сельским семьям 1930–1990-х, в том числе кто ушёл на фронт.""",
    },
    "wwi": {
        "title": ("First World War records (Russia)", "Первая мировая война (Россия)"),
        "en": """**What:** casualty lists (killed, wounded, missing, captured), card files of losses, POW records, awards (St George
crosses). Online: gwar.mil.ru (Памяти героев Великой войны), RIA-1914 (ria1914.info) indexes, the ICRC POW archive
(grandeguerre.icrc.org) for prisoners on both sides.

**How:** search by surname with the province and district: soldiers are recorded with «уезд, волость, деревня».
Spelling varies a lot — use name variants. A loss card often gives the regiment, which leads to its records in RGVIA.""",
        "ru": """**Что это:** списки потерь (убитые, раненые, пропавшие, пленные), картотека потерь, документы о пленных, награды (Георгиевские
кресты). В сети: gwar.mil.ru («Памяти героев Великой войны»), указатели ria1914.info, архив МККК о пленных
(grandeguerre.icrc.org) — по пленным обеих сторон.

**Как:** ищите по фамилии вместе с губернией и уездом — солдат записан с «уездом, волостью, деревней». Написание
очень разное, используйте варианты. Карточка потерь часто называет полк, а по нему — документы в РГВИА.""",
    },
    "wwii": {
        "title": ("Second World War records (USSR)", "Великая Отечественная война (СССР)"),
        "en": """**What:** «Память народа» (pamyat-naroda.ru): award records, unit documents, call-up lists, losses, POW cards,
hospital records; «ОБД Мемориал» (obd-memorial.ru): reports of irrecoverable losses and burial records; «Подвиг народа»
merged into Память народа. TsAMO (Podolsk) holds the originals and answers requests.

**How:** search by surname + given name + birth year ±2; then by place of birth and by the military commissariat
(«призван … РВК»). A missing-in-action report often has the family's address — a link to relatives.

**Traps:** clerks wrote names by ear; patronymics are often wrong; one person may have 3–5 records under different
spellings — check every one, they add details. Soviet POW cards (from German records) are in ОБД too.""",
        "ru": """**Что это:** «Память народа» (pamyat-naroda.ru): наградные документы, документы частей, списки призыва, потери, карточки
военнопленных, госпитали; «ОБД Мемориал» (obd-memorial.ru): донесения о безвозвратных потерях и захоронения.
«Подвиг народа» влит в «Память народа». ЦАМО (Подольск) хранит оригиналы и отвечает на запросы.

**Как:** ищите по фамилии, имени и году рождения ±2, затем по месту рождения и военкомату («призван … РВК»). В донесении о
пропавших часто есть адрес семьи — ниточка к родным.

**Ловушки:** писари записывали на слух; отчества бывают перепутаны; на одного человека 3–5 записей с разным написанием —
проверьте все, они дополняют друг друга. Карточки советских военнопленных (из немецких документов) тоже в ОБД.""",
    },
    "repression": {
        "title": ("Victims of political repression (USSR): investigation files", "Репрессии в СССР: следственные дела"),
        "en": """**What:** investigation files (arrest, interrogations, verdict, rehabilitation), «dekulakisation» and deportation
files, special settler registers. The files are kept by the FSB/SBU/KGB archives or passed to state archives; access depends on the country.
In Russia, relatives can request access with proof of kinship; personal/family privacy restrictions normally last
75 years from document creation, but expiry does not automatically lift other restrictions. In Ukraine, the 2015 law
opens the archives of repressive bodies of 1917–1991 to everyone, without proof of kinship (subject to the law’s exceptions).

**Online:** «Открытый список» (ru.openlist.wiki), «Жертвы политического террора» (lists.memo.ru, Memorial),
«Возвращённые имена», «Бессмертный барак», regional Books of Memory; Ukraine — SBU archive (HDA SBU) catalogues.

**How:** find the name in the online lists (they give the date of arrest, article, verdict and archive), then write to
the archive named there; attach proof of kinship where the country’s access rules require it. Ask for the whole file, including photos.""",
        "ru": """**Что это:** следственные дела (арест, допросы, приговор, реабилитация), дела о раскулачивании и выселении, учёт
спецпоселенцев. Хранятся в архивах ФСБ/СБУ/КГБ или переданы в госархивы; доступ зависит от страны.
В России родственники запрашивают доступ с подтверждением родства; ограничение по личной и семейной тайне обычно
действует 75 лет со дня создания документа, но истечение срока не снимает автоматически другие ограничения.
В Украине закон 2015 г. открывает архивы репрессивных органов 1917–1991 гг. всем, без подтверждения родства
(с предусмотренными законом исключениями).

**В сети:** «Открытый список» (ru.openlist.wiki), «Жертвы политического террора» (lists.memo.ru, «Мемориал»),
«Возвращённые имена», «Бессмертный барак», региональные Книги памяти; Украина — архив СБУ (ГДА СБУ).

**Как:** найдите имя в базах (там дата ареста, статья, приговор и архив), затем напишите в указанный архив с копиями
документов о родстве там, где этого требуют правила страны. Просите дело целиком, включая фотографии.""",
    },
    "passenger_list": {
        "title": ("Passenger lists and emigration (USA, Canada, Argentina, Brazil)", "Списки пассажиров и эмиграция"),
        "en": """**What:** ship manifests of arrivals (USA 1820–1957: Ellis Island and other ports; Canada; Argentina — CEMLA;
Brazil — Hospedaria/Museu da Imigração in São Paulo), departures (Hamburg 1850–1934, Bremen fragments), naturalisation
files (US: declaration and petition with place of birth), consular registers.

**How:** search with every spelling and with Latin transliterations in German, Polish, Yiddish and Spanish forms;
the US manifests from 1907 give the nearest relative left behind and the town of origin — the link back to Europe.
For Latin America, search immigrant hostels (hospedarias, hotel de inmigrantes) and the parish register of the
first years: baptisms of children name the parents' home town.

**Traps:** «Russia» on a manifest means the Empire — Poles, Lithuanians, Jews, Germans, Ukrainians. Names were not
changed at Ellis Island; they changed later, at naturalisation.""",
        "ru": """**Что это:** списки пассажиров прибывших судов (США 1820–1957: Эллис-Айленд и другие порты; Канада; Аргентина — CEMLA;
Бразилия — «Hospedaria», Museu da Imigração в Сан-Паулу), списки отправлений (Гамбург 1850–1934, фрагменты Бремена),
дела о натурализации (в США — заявление и прошение с местом рождения), консульские книги.

**Как:** ищите во всех написаниях, включая немецкую, польскую, идиш и испанскую транслитерацию; в списках США с 1907 г.
указан ближайший родственник на родине и город — ниточка обратно в Европу. Для Латинской Америки — книги иммигрантских
приютов и метрики первых лет: в записях о крещении детей названо место, откуда родители.

**Ловушки:** «Russia» в списке — это империя: поляки, литовцы, евреи, немцы, украинцы. Фамилии не меняли на
Эллис-Айленде; их меняли позже, при натурализации.""",
    },
    "census": {
        "title": ("Censuses: Russian Empire 1897, USSR 1926–1939, Europe and the Americas", "Переписи населения"),
        "en": """**Russian Empire 1897:** the only general census; most household forms were destroyed, survivors are in regional
archives (some on FamilySearch). **USSR 1926, 1937, 1939:** the
individual forms are almost entirely lost; only statistics survive. **Elsewhere:** US federal censuses 1790–1950 (1950
open since 2022), UK 1841–1921, Ireland 1901 and 1911 (free), Canada, Argentina 1869/1895, Brazil — municipal lists;
many on FamilySearch for free.

**How:** a census places a whole household in one place and year with ages and relations — use it to plan the
search of parish and civil registers.""",
        "ru": """**Российская империя, 1897:** единственная всеобщая перепись; переписные листы в основном уничтожены, уцелевшие — в
областных архивах (часть — на FamilySearch). **СССР, 1926, 1937, 1939:** листы
почти не сохранились, есть только статистика. **В других странах:** переписи США 1790–1950 (1950 открыта с 2022 г.),
Великобритании 1841–1921, Ирландии 1901 и 1911 (бесплатно), Канады, Аргентины 1869/1895, Бразилии — муниципальные списки;
многое бесплатно на FamilySearch.

**Как:** перепись привязывает весь двор к месту и году с возрастом и родством — по ней планируйте поиск в метриках и
актах гражданского состояния.""",
    },
    "civil_registration_europe": {
        "title": ("Civil registration in Europe", "Гражданская регистрация в Европе"),
        "en": """**When it began:** France 1792, Belgium and the Netherlands 1796–1811 (French rule), Italy regionally from 1797 (e.g. Cremona), generally from 1866–1871 (Trentino/South Tyrol from 1918),
Germany 1874–1876 (Prussia 1874), England and Wales 1837, Scotland 1855, Ireland 1864 (non-Catholic marriages 1845),
Spain 1871, Portugal 1911, Hungary 1895, Austria 1938–1939 (Burgenland from 1895; civil marriage from 1938; births and deaths from 1939; earlier parish registers served as civil records), Poland — civil-religious registers from 1808/1826 (the parish
priest was the registrar), Romania 1865, the USSR (ZAGS) 1918–1920.

**Where:** municipal and state archives; many online: Antenati (Italy, free images), FranceArchives and departmental
archives (free), Openarchieven / WieWasWie (Netherlands), Arch.be (Belgium), PARES and municipal archives (Spain),
Geneteka (Poland index) and Szukajwarchiwach (scans), ScotlandsPeople (paid), FreeBMD (England index).

**Traps:** before civil registration you need parish registers (often in diocesan archives, Matricula for
Austria/Germany/Poland/Slovenia). Registers from the period of French rule may use the French Republican calendar
(an II, etc.); it was abolished from 1 January 1806.""",
        "ru": """**С какого года:** Франция 1792, Бельгия и Нидерланды 1796–1811 (при французах), Италия местами с 1797 г. (например, Кремона), в целом с 1866–1871 гг. (Трентино/Южный Тироль с 1918 г.), Германия
1874–1876 (Пруссия 1874), Англия и Уэльс 1837, Шотландия 1855, Ирландия 1864 (некатолические браки — 1845), Испания 1871,
Португалия 1911, Венгрия 1895, Австрия 1938–1939 (Бургенланд с 1895 г.; гражданские браки с 1938 г., рождения и смерти с 1939 г.; ранее церковные книги имели силу гражданских), Польша — гражданско-церковные книги с 1808/1826 (ксёндз был регистратором),
Румыния 1865, СССР (ЗАГС) 1918–1920.

**Где:** муниципальные и государственные архивы; многое в сети: Antenati (Италия, бесплатные сканы), FranceArchives и
архивы департаментов (бесплатно), Openarchieven / WieWasWie (Нидерланды), Arch.be (Бельгия), PARES и муниципальные архивы
(Испания), Geneteka (указатель по Польше) и Szukajwarchiwach (сканы), ScotlandsPeople (платно), FreeBMD (указатель по
Англии).

**Ловушки:** до гражданской регистрации нужны церковные книги (часто в епархиальных архивах; Matricula — Австрия,
Германия, Польша, Словения). В книгах периода французского господства может встречаться французский республиканский
календарь; он отменён с 1 января 1806 г.""",
    },
    "latin_america": {
        "title": ("Latin America: parish and civil records, immigration", "Латинская Америка: церковные и гражданские записи, иммиграция"),
        "en": """**Parish registers** (bautismos, matrimonios, defunciones; Portuguese batismos, casamentos, óbitos) from the 16th
century onward — the largest part is filmed by FamilySearch (free images, often indexed). Marriage files
(«expedientes matrimoniales», «informaciones matrimoniales») give the parents and birthplaces of both spouses, often
in Spain, Italy or Portugal — the key to the European origin.

**Civil registration:** Mexico 1859, Argentina 1880s (Buenos Aires 1886), Brazil 1889, Chile 1885, Uruguay 1879;
elsewhere later and unevenly — parish registers stay the main source into the 20th century. Records are in civil registries; FamilySearch holds large sets.

**Immigration:** Argentina — CEMLA (arrivals from 1882, paid search), Hotel de Inmigrantes; Brazil — Museu da Imigração
(São Paulo, free digitised hostel registers, 1882–1958), Arquivo Nacional (ship lists for Rio); Chile — Archivo Nacional;
Mexico — Archivo General de la Nación (migration cards 1926–1951).

**Traps:** Hispanic names carry two surnames (father's + mother's): «Juan Pérez García» is the son of a Pérez and a
García; women keep their surnames after marriage («de» + husband's surname may be added). Portuguese order is
mother's + father's. Italian, German and Slavic surnames were Hispanicised (Kowalski → Covalski).""",
        "ru": """**Церковные книги** (bautismos, matrimonios, defunciones; по-португальски batismos, casamentos, óbitos) — с XVI века;
большая часть снята FamilySearch (бесплатные сканы, часто с индексом). Брачные дела («expedientes matrimoniales») называют
родителей и места рождения обоих супругов, часто в Испании, Италии или Португалии — ключ к европейским корням.

**Гражданская регистрация:** Мексика 1859, Аргентина 1880-е (Буэнос-Айрес 1886), Бразилия 1889, Чили 1885, Уругвай 1879;
в других странах позже и неравномерно — церковные книги остаются главным источником и в XX веке. Записи в органах регистрации; крупные массивы на FamilySearch.

**Иммиграция:** Аргентина — CEMLA (прибытия с 1882 г., платный поиск), Hotel de Inmigrantes; Бразилия — Museu da
Imigração (Сан-Паулу, бесплатные оцифрованные книги приюта 1882–1958 гг.), Arquivo Nacional (судовые списки Рио); Чили — Archivo
Nacional; Мексика — Archivo General de la Nación (миграционные карточки 1926–1951).

**Ловушки:** у испаноязычных две фамилии (отца + матери): «Хуан Перес Гарсия» — сын Переса и Гарсии; женщины сохраняют
свои фамилии после брака (может добавляться «de» + фамилия мужа). У португальцев порядок: фамилия матери + отца.
Итальянские, немецкие и славянские фамилии испанизировались (Kowalski → Covalski).""",
    },
    "evidence": {
        "title": ("Evaluating evidence: when a find is proof", "Как оценивать находку"),
        "en": """1. **A name is not a person.** A namesake is not a relative; a patronymic does not give you the father's identity.
2. **Two independent facts** beyond the name (parents, spouse, children, village and household, estate, year ±3) make a
   match; one fact makes it «probable»; a conflict needs a third document.
3. **Original > copy > index.** An index or a transcription is a pointer: open the image and cite it (archive, fond,
   opis, delo, folio — or the film and frame).
4. **Primary information** (a witness at the time: a baptism record for the date of birth) outweighs secondary (the
   age at death for the year of birth).
5. **Keep conflicts:** record both versions with their sources; do not average them.
6. **Negative results count:** «searched the 1880–1890 registers of the parish, no birth» saves the next search.
7. **Mark the doubtful as doubtful:** «probably», a research lead, never a silent link in the tree.""",
        "ru": """1. **Имя — ещё не человек.** Однофамилец — не родственник; отчество не говорит, кто именно отец.
2. **Два независимых факта** кроме имени (родители, супруг, дети, деревня и двор, сословие, год ±3) — совпадение; один
   факт — «вероятно»; противоречие — нужен третий документ.
3. **Подлинник > копия > индекс.** Индекс и расшифровка — указатель: откройте снимок и ссылайтесь на него (архив, фонд,
   опись, дело, лист — или плёнка и кадр).
4. **Первичные сведения** (записаны в момент события: дата рождения в записи о крещении) весомее вторичных (год
   рождения по возрасту умершего).
5. **Противоречия храните:** обе версии со своими источниками; не усредняйте.
6. **Отрицательный результат — тоже результат:** «просмотрены метрики прихода за 1880–1890 гг., рождения нет» экономит
   следующий поиск.
7. **Сомнительное помечайте:** «вероятно», наводка — но не молчаливая связь в древе.""",
    },
}

GLOSSARY = {   # term → (English explanation, Russian explanation)
    "фонд": ("fond: the records of one institution or family in an archive; part of a citation (ф. 1)", "совокупность документов одного учреждения или семьи; часть ссылки (ф. 1)"),
    "опись": ("opis: the inventory of a fond; citation part (оп. 2)", "перечень дел фонда; часть ссылки (оп. 2)"),
    "дело": ("delo: a file, the unit of storage; citation part (д. 345)", "единица хранения; часть ссылки (д. 345)"),
    "лист": ("list: a folio; «об.» = verso (л. 12 об.)", "лист дела; «об.» — оборот (л. 12 об.)"),
    "губерния": ("guberniya: province of the Russian Empire", "крупнейшая административная единица империи"),
    "уезд": ("uezd: district of a province", "часть губернии"),
    "волость": ("volost: rural township (several villages), 1861–1929", "сельская административная единица, несколько деревень (1861–1929)"),
    "приход": ("parish: the villages served by one church", "деревни, относившиеся к одной церкви"),
    "погост": ("pogost: a church settlement with a graveyard, often the parish centre", "селение при церкви с кладбищем, часто центр прихода"),
    "село": ("selo: a village with a church", "селение с церковью"),
    "деревня": ("derevnya: a village without a church", "селение без церкви"),
    "сельцо": ("seltso: a village with a landowner's manor, without a church", "селение с помещичьей усадьбой без церкви"),
    "слобода": ("sloboda: a settlement of free (often privileged) people", "поселение вольных, часто льготных людей"),
    "крестьянин": ("peasant (state, landlord's, appanage, economic)", "земледельческое сословие (государственные, помещичьи, удельные, экономические)"),
    "мещанин": ("meshchanin: town dweller of the lower urban estate", "городское податное сословие"),
    "купец": ("merchant of the 1st/2nd/3rd guild", "торговое сословие, 1-я/2-я/3-я гильдия"),
    "однодворец": ("odnodvorets: descendant of military servitors, free farmer in the south", "потомок служилых людей, свободный землепашец на юге"),
    "дворовый": ("household serf", "крепостной, служивший в помещичьем доме"),
    "солдатка": ("a soldier's wife", "жена солдата"),
    "отставной": ("retired (soldier)", "уволенный со службы"),
    "бессрочноотпускной": ("a soldier on indefinite leave (reserve)", "солдат в бессрочном отпуске (запас)"),
    "временнообязанный": ("a former serf still owing duties after 1861", "бывший крепостной, ещё несущий повинности после 1861 г."),
    "казённая палата": ("treasury chamber of a province: keeps the revision lists", "губернское финансовое ведомство: в его фонде ревизские сказки"),
    "консистория": ("the diocesan consistory: keeps copies of parish registers and confession lists", "епархиальное ведомство: в его фонде вторые экземпляры метрик и исповедных"),
    "восприемники": ("godparents", "крёстные родители"),
    "поручители": ("witnesses (sureties) at a marriage", "свидетели при венчании"),
    "законная жена": ("lawful wife (marks a legitimate birth)", "законная жена — знак законного рождения"),
    "незаконнорожденный": ("illegitimate", "рождённый вне брака"),
    "первым браком": ("in his/her first marriage", "вступает в брак впервые"),
    "вдовец": ("widower", "вдовец"),
    "вдова": ("widow", "вдова"),
    "сноха": ("daughter-in-law (son's wife)", "жена сына"),
    "невестка": ("sister-in-law (brother's wife) or daughter-in-law", "жена брата (или сына)"),
    "зять": ("son-in-law or brother-in-law (sister's husband)", "муж дочери или сестры"),
    "шурин": ("wife's brother", "брат жены"),
    "деверь": ("husband's brother", "брат мужа"),
    "золовка": ("husband's sister", "сестра мужа"),
    "свояченица": ("wife's sister", "сестра жены"),
    "свояк": ("husband of the wife's sister", "муж сестры жены"),
    "сват": ("father of one's son- or daughter-in-law", "отец зятя или снохи"),
    "пасынок": ("stepson", "сын жены или мужа от другого брака"),
    "падчерица": ("stepdaughter", "дочь жены или мужа от другого брака"),
    "единокровный": ("half-sibling by the father", "брат или сестра по отцу"),
    "единоутробный": ("half-sibling by the mother", "брат или сестра по матери"),
    "ревизская душа": ("a male taxable person counted in a revision", "податная мужская душа в ревизии"),
    "выбыл в рекруты": ("conscripted into the army (left the household)", "взят в рекруты, выбыл из двора"),
    "старый стиль": ("Julian calendar; Russia until 1 (14) Feb 1918", "юлианский календарь; в России до 1 (14) февраля 1918 г."),
    "РВК": ("district military commissariat (call-up office)", "районный военный комиссариат"),
    "ЗАГС": ("Soviet civil registry office (1918–)", "органы записи актов гражданского состояния (с 1918 г.)"),
    "похозяйственная книга": ("Soviet rural household register", "книга учёта дворов сельсовета"),
    "ъ": ("hard sign at the end of words in pre-1918 spelling (Иванъ); drop it when searching modern indexes", "твёрдый знак на конце слов до 1918 г. (Иванъ); в современных указателях его нет"),
    "ѣ": ("yat: pre-1918 letter, now е (Алексѣй → Алексей)", "ять: дореформенная буква, теперь е"),
    "і": ("pre-1918 letter before vowels, now и (Георгій → Георгий)", "і десятеричное перед гласными, теперь и"),
}


LANGS = ("en", "ru", "uk", "es", "pt", "pl", "de")


def _extra(lang):
    """Translations beyond English and Russian: genealogy_mcp/i18n/guides_<lang>.py."""
    if lang not in LANGS[2:]:
        return {}
    import importlib
    return importlib.import_module(f".i18n.guides_{lang}", __package__).GUIDES


def guide(topic, lang="en"):
    g = GUIDES.get(topic)
    if not g:
        return None
    extra = _extra(lang).get(topic)
    if extra:
        return f"# {extra[0]}\n\n{extra[1]}"
    ru = lang == "ru"
    text = f"# {g['title'][1 if ru else 0]}\n\n{g['ru' if ru else 'en']}"
    if lang not in ("en", "ru"):
        text += f"\n\n_(No {lang} translation of this guide yet: shown in English.)_"
    return text


def topics(lang="en"):
    extra = _extra(lang)
    return {k: (extra[k][0] if k in extra else v["title"][1 if lang == "ru" else 0]) for k, v in GUIDES.items()}


def glossary(term="", lang="en"):
    t = term.strip().lower()
    i = 1 if lang == "ru" else 0
    items = {k: v[i] for k, v in GLOSSARY.items() if not t or t in k.lower() or t in v[0].lower()}
    return items
