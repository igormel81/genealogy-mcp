"""Writes src/genealogy_mcp/data/sources.json. Edit the list here, then: python3 tools/make_sources.py

Every entry: id, name, url, countries (ISO codes, "*" = worldwide), years [from, to], records (kinds),
access (free | free_account | paid | request | mixed), about / about_ru (what it is), how / how_ru (how to search
it well, pitfalls), search (optional URL template: {q} {given} {surname} {year_from} {year_to} {place}).
"""
import json
from pathlib import Path

S = []


def add(id, name, url, countries, years, records, access, about, about_ru, how, how_ru, search=None):
    S.append({"id": id, "name": name, "url": url, "countries": countries.split(), "years": list(years),
              "records": records.split(), "access": access, "about": about, "about_ru": about_ru,
              "how": how, "how_ru": how_ru, **({"search": search} if search else {})})


# ---------- worldwide
add("familysearch", "FamilySearch (records)", "https://www.familysearch.org/search", "*", (1500, 2000),
    "church vital census revision emigration military trees", "free_account",
    "The largest free genealogy database: billions of indexed records and images from almost every country.",
    "Крупнейшая бесплатная генеалогическая база: миллиарды записей и снимков почти из всех стран.",
    "Search the index by name, but never stop there: much is not indexed. Open the image of every hit and cite the image, not the index.",
    "Ищите по индексу, но не останавливайтесь: многое не проиндексировано. Открывайте снимок каждой находки и ссылайтесь на снимок, а не на индекс.",
    "https://www.familysearch.org/search/record/results?q.givenName={given}&q.surname={surname}&q.birthLikeDate.from={year_from}&q.birthLikeDate.to={year_to}&q.birthLikePlace={place}")
add("familysearch_catalog", "FamilySearch Catalog (unindexed images)", "https://www.familysearch.org/search/catalog", "*", (1500, 1950),
    "church revision confession census catalogs", "free_account",
    "Millions of filmed register books not covered by the name index: parish registers, confession lists, revision lists.",
    "Миллионы снятых на плёнку книг, которых нет в поиске по именам: метрические книги, исповедные ведомости, ревизские сказки.",
    "Search the catalogue by place (country → province → district → town), open the film for the right years and browse it frame by frame. Many films open only after signing in or in a FamilySearch centre.",
    "Ищите в каталоге по месту (страна → губерния → уезд → село), откройте плёнку за нужные годы и листайте кадр за кадром. Многие плёнки открываются только после входа или в центре FamilySearch.")
add("archive_org", "Internet Archive — full-text search", "https://archive.org", "*", (1700, 1960),
    "directories newspapers books places", "free",
    "Digitised books searchable by their recognised text: provincial memorial books, address calendars, lists of settlements, regimental histories, newspapers.",
    "Оцифрованные книги с поиском по распознанному тексту: памятные книжки губерний, адрес-календари, списки населённых мест, истории полков, газеты.",
    "Choose 'Search text contents'. Old orthography is recognised poorly: search in the old spelling too (Сынковскій, Колодинъ) and by a short unusual fragment.",
    "Выберите поиск по тексту. Старую орфографию распознаёт плохо: ищите и в старом написании (Сынковскій, Колодинъ), и по короткому необычному куску.",
    "https://archive.org/search?query={q}&sin=TXT")
add("myheritage", "MyHeritage", "https://www.myheritage.com", "*", (1600, 2025), "trees vital census newspapers", "paid",
    "Family trees and record collections with automatic Smart Matches and Record Matches.",
    "Семейные деревья и коллекции записей с автоматическими совпадениями (Smart Matches, Record Matches).",
    "Upload your tree (GEDCOM) and review the matches: most are namesakes. Treat other people's trees as leads, never as proof.",
    "Загрузите своё древо (GEDCOM) и разберите совпадения: большинство — однофамильцы. Чужие деревья — только наводки, не доказательства.")
add("geni", "Geni", "https://www.geni.com", "*", (1500, 2025), "trees", "mixed",
    "One shared world tree: a profile per person, merged between families.",
    "Единое мировое древо: один профиль на человека, общий для разных семей.",
    "Good for finding the other branches of your family. Check what sources a profile cites before trusting it.",
    "Помогает найти другие ветви семьи. Прежде чем верить профилю, посмотрите, на какие источники он ссылается.")
add("wikitree", "WikiTree", "https://www.wikitree.com", "*", (1500, 2025), "trees", "free",
    "A free collaborative world tree that requires sources for every profile.",
    "Бесплатное общее мировое древо, где у каждого профиля должны быть источники.",
    "Search by name and dates; profiles list their sources, so check them first.",
    "Ищите по имени и датам; у профилей перечислены источники — проверяйте их в первую очередь.")
add("findagrave", "Find a Grave", "https://www.findagrave.com", "*", (1600, 2025), "graves", "free",
    "Hundreds of millions of grave memorials with photos of headstones, contributed by volunteers.",
    "Сотни миллионов записей о захоронениях с фотографиями надгробий от добровольцев.",
    "Search by name and cemetery or place; check the photograph of the stone, not just the transcription.",
    "Ищите по имени и кладбищу или месту; сверяйтесь с фотографией камня, а не только с расшифровкой.",
    "https://www.findagrave.com/memorial/search?firstname={given}&lastname={surname}")
add("billiongraves", "BillionGraves", "https://billiongraves.com", "*", (1700, 2025), "graves", "free",
    "GPS-tagged photographs of headstones with transcriptions.",
    "Фотографии надгробий с GPS-метками и расшифровками.",
    "Useful when Find a Grave has nothing; transcriptions are done by volunteers — read the photo yourself.",
    "Полезно, если на Find a Grave ничего нет; расшифровки делают добровольцы — читайте снимок сами.")
add("arolsen", "Arolsen Archives", "https://collections.arolsen-archives.org", "* DE PL UA RU BY", (1933, 1960),
    "holocaust deportation forced_labour displaced", "free",
    "The archive on victims of Nazi persecution: concentration camps, forced labourers taken to Germany, displaced persons after the war.",
    "Архив о жертвах нацистских преследований: концлагеря, угнанные на работы в Германию, перемещённые лица после войны.",
    "Try spellings as a German clerk heard them (Kubekow, Kubekoff, Melnikow) and search by date of birth.",
    "Пробуйте написания, как их слышал немецкий писарь (Kubekow, Kubekoff, Melnikow), и ищите по дате рождения.",
    "https://collections.arolsen-archives.org/en/search?s={q}")
add("yad_vashem", "Yad Vashem — Central Database of Shoah Victims' Names", "https://yvng.yadvashem.org", "*", (1933, 1945),
    "holocaust", "free",
    "Names of Jewish victims of the Holocaust from pages of testimony, lists and documents.",
    "Имена евреев — жертв Холокоста по листам свидетельских показаний, спискам и документам.",
    "Pages of testimony often name parents and spouses and were filled in by relatives — contact details may lead to living family.",
    "В листах свидетельских показаний часто названы родители и супруги, их заполняли родственники — это путь к живой родне.")
add("jewishgen", "JewishGen", "https://www.jewishgen.org", "* RU UA BY PL LT LV MD RO", (1700, 1945), "vital census directories trees", "free_account",
    "Databases, town pages and discussion groups for Jewish genealogy of Eastern Europe.",
    "Базы, страницы местечек и группы обсуждения по еврейской генеалогии Восточной Европы.",
    "Start from the JewishGen Communities page of the town: it lists what records survive and where.",
    "Начните со страницы местечка в JewishGen Communities: там сказано, какие записи сохранились и где.")
add("matricula", "Matricula", "https://data.matricula-online.eu", "AT DE PL SI RS CZ", (1600, 1940), "church", "free",
    "Catholic parish registers of Austria, Germany, Poland, Slovenia, Serbia and other dioceses, as images.",
    "Католические метрические книги Австрии, Германии, Польши, Словении, Сербии и других епархий — снимками.",
    "Browse by diocese and parish; there is no name index, so know the parish first.",
    "Листайте по епархии и приходу; поиска по именам нет, приход нужно знать заранее.")
add("geneanet", "Geneanet", "https://www.geneanet.org", "* FR", (1600, 2025), "trees church graves", "mixed",
    "Family trees and indexed records, strongest for France and Western Europe.",
    "Семейные деревья и индексы записей, лучше всего по Франции и Западной Европе.",
    "Use as a source of leads; follow the cited records.",
    "Используйте как источник наводок; переходите к указанным документам.")
add("wikipedia", "Wikipedia and Wikimedia Commons", "https://www.wikipedia.org", "*", (1000, 2025), "places", "free",
    "History of villages, districts, parishes, regiments; old photographs and maps in the public domain.",
    "История сёл, районов, приходов, полков; старые фотографии и карты в общественном достоянии.",
    "Read the village article in the local language Wikipedia: it often names the old parish and district.",
    "Читайте статью о селе в Википедии на местном языке: там часто указаны прежний приход и уезд.")

# ---------- Russian Empire and USSR
add("yandex_archive", "Yandex Archive", "https://yandex.ru/archive", "RU", (1800, 1930), "church confession newspapers", "free",
    "Handwritten parish registers, confession lists and old newspapers recognised by Yandex; strongest for Moscow and the Moscow region.",
    "Распознанные Яндексом рукописные метрические книги, исповедные ведомости и старые газеты; больше всего по Москве и Подмосковью.",
    "It searches the handwriting itself, so it finds what no index has. Recognition errs: try spelling variants and check every hit on the image.",
    "Ищет по самому рукописному тексту и находит то, чего нет в индексах. Распознавание ошибается: пробуйте варианты написания и проверяйте каждую находку по снимку.")
add("rusarchives_guides", "Guides to the fonds of Russian archives", "https://guides.rusarchives.ru", "RU", (1700, 2000), "catalogs", "free",
    "Which archive and which fonds holds the books of a given church, volost or institution.",
    "В каком архиве и фонде лежат книги нужной церкви, волости, учреждения.",
    "A fonds number is not a file number: inventories are often only in the reading room or on the archive's own site.",
    "Номер фонда — ещё не номер дела: описи часто только в читальном зале или на сайте самого архива.")
add("vgd", "VGD forum (All-Russian Family Tree)", "https://forum.vgd.ru", "RU UA BY", (1700, 2000), "trees catalogs", "free",
    "The largest Russian-language genealogy forum: threads per district and village, archive fonds numbers, news of digitisation.",
    "Крупнейший русскоязычный генеалогический форум: ветки по уездам и сёлам, номера фондов, новости оцифровки.",
    "Find the thread of your district: people post what survives and where. Treat posts as leads and check the documents.",
    "Найдите ветку своего уезда: там пишут, что сохранилось и где. Сообщения — наводки, проверяйте по документам.")
add("pamyat_naroda", "Memory of the People (Pamyat Naroda)", "https://pamyat-naroda.ru", "RU UA BY MD *", (1941, 1945), "military", "free",
    "Second World War records of the Soviet army from the Central Archive of the Ministry of Defence: registration cards, award sheets, casualty reports, hospital records, unit routes.",
    "Документы Красной армии времён Великой Отечественной из ЦАМО: учётные карточки, наградные листы, донесения о потерях, госпитали, боевой путь частей.",
    "Search without the patronymic and with a birth year range; open the document scan — the index often misreads villages. The unit's route shows where the person fought.",
    "Ищите без отчества и с диапазоном года рождения; открывайте скан — в индексе часто искажены сёла. Боевой путь части показывает, где воевал человек.")
add("obd_memorial", "OBD Memorial", "https://obd-memorial.ru", "RU UA BY MD *", (1941, 1945), "military graves", "free",
    "The database of Soviet soldiers killed and missing in 1941–1945, prisoners of war and burials.",
    "База погибших и пропавших без вести в 1941–1945, военнопленных и захоронений.",
    "A person often has several records (report of loss, POW card, burial); compare all of them.",
    "У человека часто несколько записей (донесение, карточка военнопленного, захоронение) — сравните все.")
add("gwar", "Heroes of the Great War 1914–1918", "https://gwar.mil.ru", "RU UA BY PL LT", (1914, 1918), "military", "free",
    "First World War records of the Russian army: casualty lists, hospitals, prisoners of war, awards.",
    "Первая мировая: списки потерь, госпитали, военнопленные, награды русской армии.",
    "Search is capricious: try without the patronymic, by year and by province; the home volost in the card is the best clue.",
    "Поиск капризен: пробуйте без отчества, по году и губернии; волость в карточке — лучшая зацепка.")
add("openlist", "Open List", "https://ru.openlist.wiki", "RU UA BY *", (1917, 1991), "repression", "free",
    "An open wiki of victims of political repression in the USSR, compiled from regional books of memory.",
    "Открытая вики-база жертв политических репрессий в СССР, собранная из региональных книг памяти.",
    "Absence proves nothing: many regions are incomplete. A record gives the archive and the case number for a request.",
    "Отсутствие ничего не доказывает: многие регионы неполны. Запись даёт архив и номер дела для запроса.",
    "https://ru.openlist.wiki/index.php?search={q}")
add("bessmertny_barak", "Immortal Barrack", "https://bessmertnybarak.ru", "RU *", (1917, 1991), "repression", "free",
    "Victims of repression with biographies, photographs and documents added by relatives.",
    "Жертвы репрессий с биографиями, фотографиями и документами от родственников.",
    "Check alongside Open List: the bases overlap but are not the same.",
    "Проверяйте вместе с «Открытым списком»: базы пересекаются, но не совпадают.")
add("vozvrashchennye_imena", "Returned Names", "https://visz.nlr.ru", "RU", (1917, 1991), "repression", "free",
    "Books of memory of victims of political repression collected by the National Library of Russia.",
    "Книги памяти жертв политических репрессий, собранные Российской национальной библиотекой.",
    "Search by surname across all regional books at once.",
    "Ищите по фамилии сразу по всем региональным книгам.")
add("pstgu_martyrs", "New Martyrs and Confessors (PSTGU)", "https://martyrs.pstbi.ru", "RU", (1917, 1991), "repression clergy", "free",
    "Clergy and lay people who suffered for their faith in the Soviet period, with case details.",
    "Духовенство и миряне, пострадавшие за веру в советское время, с подробностями дел.",
    "Essential for families of priests, deacons and psalm-readers.",
    "Незаменимо для семей священников, диаконов, псаломщиков.")
add("prlib", "Presidential Library", "https://www.prlib.ru", "RU", (1700, 1950), "directories books", "free",
    "Digitised memorial books of provinces, directories, provincial gazettes.",
    "Оцифрованные памятные книжки губерний, справочники, губернские ведомости.",
    "Some items open only in reading rooms; search the catalogue by province and year.",
    "Часть материалов — только в читальных залах; ищите в каталоге по губернии и году.")
add("rusneb", "National Electronic Library (NEB)", "https://rusneb.ru", "RU", (1700, 2000), "directories books", "free",
    "Scans of books, directories and dissertations from Russian libraries.",
    "Сканы книг, справочников и диссертаций из библиотек России.",
    "Full text is available for public-domain books; for others only the catalogue entry.",
    "Полный текст — для книг в общественном достоянии, для остальных только описание.")
add("shpl", "State Public Historical Library — e-library", "https://elib.shpl.ru", "RU", (1700, 1950), "directories books", "free",
    "Address calendars, memorial books, lists of settlements, pre-revolutionary reference books.",
    "Адрес-календари, памятные книжки, списки населённых мест, дореволюционные справочники.",
    "Lists of settlements give the volost and parish of a village — the key to finding its registers.",
    "Списки населённых мест дают волость и приход села — ключ к поиску метрик.")
add("etomesto", "Etomesto — old maps", "https://www.etomesto.ru", "RU UA BY", (1700, 1990), "maps places", "free",
    "Old maps (Schubert, Mende, Red Army and other surveys) laid over a modern map.",
    "Старые карты (Шуберт, Менде, РККА и др.), наложенные на современную.",
    "Find vanished villages and see which church a village belonged to.",
    "Найдите исчезнувшие деревни и посмотрите, к какой церкви относилось село.")
add("sobory", "Churches of Russia (sobory.ru)", "https://sobory.ru", "RU", (1600, 2025), "places church", "free",
    "History, photographs and coordinates of churches.",
    "История, фотографии и координаты храмов.",
    "Use it to find the parish of a village and the years the church existed.",
    "По нему находят приход села и годы существования храма.")
add("ria1914", "Officers of the Russian Imperial Army", "https://ria1914.info", "RU", (1850, 1920), "military", "free",
    "Biographical reference on officers of the Russian army before 1917 compiled from orders and lists.",
    "Биографический справочник по офицерам русской армии до 1917 г. из приказов и списков.",
    "Good for officers; for soldiers use gwar.mil.ru.",
    "Хорош для офицеров; для солдат — gwar.mil.ru.")
add("regional_archives_ru", "Regional state archives (Russia)", "https://rusarchives.ru", "RU", (1700, 1991),
    "church confession revision census catalogs household", "request",
    "The main holdings: parish registers, confession and revision lists, zemstvo household cards, Soviet household books of village councils.",
    "Главное хранилище: метрические книги, исповедные ведомости и ревизские сказки, земские подворные карточки, похозяйственные книги сельсоветов.",
    "Many regional archives now publish scans or catalogues online; otherwise send a written request with the church, years and names (see draft_archive_request).",
    "Многие областные архивы выкладывают сканы или описи на сайт; иначе — письменный запрос с церковью, годами и именами (см. draft_archive_request).")
add("zags_ru", "Civil registry offices (ZAGS)", "", "RU UA BY MD", (1918, 2025), "vital", "request",
    "Birth, marriage and death records since 1918 (older ones are mostly in state archives).",
    "Записи о рождении, браке и смерти с 1918 г. (старые в основном переданы в госархивы).",
    "Archival copies are issued to relatives who prove the relationship; records under 100 years old are restricted.",
    "Архивные справки выдают родственникам, подтвердившим родство; записи моложе 100 лет — ограниченного доступа.")
add("tsamo", "Central Archive of the Ministry of Defence (TsAMO)", "", "RU", (1941, 1991), "military", "request",
    "Personnel files and records of the Soviet army after 1941; much is online via Pamyat Naroda.",
    "Личные дела и документы Советской армии после 1941 г.; многое уже на «Памяти народа».",
    "Check Pamyat Naroda first; request what is not there with full name, birth year and unit.",
    "Сначала проверьте «Память народа»; чего там нет — запрашивайте с ФИО, годом рождения и частью.")
add("rgvia", "Russian State Military History Archive (RGVIA)", "https://rgvia.ru", "RU", (1700, 1918), "military", "request",
    "Service records of officers and military officials before 1918, regimental records.",
    "Послужные списки офицеров и военных чиновников до 1918 г., документы полков.",
    "Service records survive mainly for officers; for soldiers look at regimental lists and gwar.mil.ru.",
    "Послужные списки сохранились в основном у офицеров; для солдат — полковые списки и gwar.mil.ru.")
add("rgia", "Russian State Historical Archive (RGIA)", "https://fgurgia.ru", "RU", (1700, 1917), "catalogs clergy nobility", "request",
    "Records of ministries and the Synod: clergy, nobility, officials, institutions of the Empire.",
    "Фонды министерств и Синода: духовенство, дворянство, чиновники, учреждения Империи.",
    "Search the online catalogue of inventories before writing a request.",
    "Перед запросом поищите в онлайн-каталоге описей.")
add("garf", "State Archive of the Russian Federation (GARF)", "https://statearchive.ru", "RU", (1800, 1991), "catalogs emigration repression", "request",
    "Records of the emigration, Soviet institutions and the police of the Russian Empire.",
    "Документы эмиграции, советских учреждений и полиции Российской империи.",
    "Useful for emigrants after 1917 and for political cases before 1917.",
    "Полезен для эмигрантов после 1917 г. и политических дел до 1917 г.")
# ---------- Ukraine, Belarus, Moldova, Romania, Poland, Baltics
add("archives_ua", "State Archival Service of Ukraine", "https://archives.gov.ua", "UA", (1700, 1991), "church census catalogs", "mixed",
    "Portal of Ukrainian state archives; many regional archives publish scans of parish registers and revision lists.",
    "Портал архивов Украины; многие областные архивы выкладывают сканы метрик и ревизских сказок.",
    "Go to the site of the regional archive: scans are usually listed by fonds and inventory.",
    "Идите на сайт областного архива: сканы обычно разложены по фондам и описям.")
add("cdiak", "Central State Historical Archive of Ukraine in Kyiv (TsDIAK)", "https://cdiak.archives.gov.ua", "UA", (1700, 1920),
    "church catalogs", "mixed",
    "Parish registers of Kyiv and other provinces, records of imperial institutions in Ukraine.",
    "Метрические книги Киева и других губерний, фонды учреждений Империи на Украине.",
    "Many registers are also filmed on FamilySearch; the archive site may not open from some countries.",
    "Многие книги есть и на FamilySearch; сайт архива открывается не из всех стран.")
add("archives_by", "Archives of Belarus", "https://archives.gov.by", "BY", (1700, 1991), "church census catalogs", "mixed",
    "Portal of Belarusian state archives with guides and databases.",
    "Портал государственных архивов Беларуси с путеводителями и базами.",
    "Parish registers of Belarus are also widely filmed on FamilySearch.",
    "Метрики Беларуси также широко есть на FamilySearch.")
add("arhiva_md", "National Archives Agency of Moldova", "https://arhiva.gov.md", "MD", (1812, 1991), "church census repression deportation", "mixed",
    "Church books of Bessarabia, a database of the repressed and deported, guides to the fonds.",
    "Церковные книги Бессарабии, база репрессированных и депортированных, путеводители по фондам.",
    "Names appear in Russian and Romanian forms (Василий / Vasile, Плешу / Pleșu): search both.",
    "Имена встречаются по-русски и по-румынски (Василий / Vasile, Плешу / Pleșu): ищите в обоих видах.")
add("arhive_ro", "National Archives of Romania", "http://arhivelenationale.ro", "RO MD", (1800, 1990), "church vital catalogs", "request",
    "Civil and church registers of Romania by county directorates.",
    "Записи актов и церковные книги Румынии по уездным управлениям.",
    "Write to the county directorate; many registers are also on FamilySearch ('Romania, Church Books').",
    "Пишите в уездное управление; многое есть и на FamilySearch («Romania, Church Books»).")
add("geneteka", "Geneteka", "https://geneteka.genealodzy.pl", "PL UA BY LT", (1600, 1950), "church vital", "free",
    "A volunteer index of millions of Polish parish and civil records, including former western provinces of the Russian Empire.",
    "Добровольный индекс миллионов польских метрик, включая бывшие западные губернии Российской империи.",
    "Search by surname across a province; the index links to scans on Metryki or Szukajwarchiwach where they exist.",
    "Ищите по фамилии по всему воеводству; индекс ведёт к сканам на Metryki или Szukajwarchiwach, если они есть.",
    "https://geneteka.genealodzy.pl/index.php?op=gt&lang=eng&search_lastname={surname}&search_name={given}")
add("szukajwarchiwach", "Szukajwarchiwach (Polish State Archives)", "https://www.szukajwarchiwach.gov.pl", "PL", (1600, 1990), "church vital census catalogs", "free",
    "Millions of scans from Polish state archives: parish and civil registers, population books.",
    "Миллионы сканов польских госархивов: метрики, акты гражданского состояния, книги населения.",
    "Search by town and record type, then browse the scans.",
    "Ищите по месту и виду документа, затем листайте сканы.")
add("epaveldas", "Epaveldas (Lithuania)", "https://www.epaveldas.lt", "LT", (1600, 1940), "church census", "free",
    "Digitised Lithuanian heritage including parish registers and revision lists.",
    "Оцифрованное наследие Литвы, включая метрические книги и ревизские сказки.",
    "Registers are in Latin, Polish and Russian: know the parish and the years.",
    "Книги на латыни, польском и русском: знайте приход и годы.")
add("raduraksti", "Raduraksti (Latvia)", "https://www.raduraksti.arhivi.lv", "LV", (1700, 1940), "church census revision", "free",
    "Latvian church books, revision lists and censuses as scans.",
    "Церковные книги, ревизии и переписи Латвии — сканами.",
    "Lutheran books are in German; Orthodox in Russian.",
    "Лютеранские книги на немецком, православные — на русском.")
add("ra_ee", "National Archives of Estonia", "https://www.ra.ee", "EE", (1700, 1990), "church census revision", "free",
    "Digitised church books, revision lists and other records of Estonia.",
    "Оцифрованные церковные книги, ревизии и другие документы Эстонии.",
    "Use the archive's information system to browse by parish.",
    "Листайте по приходам в информационной системе архива.")
# ---------- Ireland, UK, USA, Germany
add("nli_registers", "Catholic parish registers of Ireland (NLI)", "https://registers.nli.ie", "IE GB", (1740, 1880), "church", "free",
    "Microfilmed Catholic baptism and marriage registers, mostly up to 1880, by parish.",
    "Микрофильмы католических книг крещений и браков, в основном до 1880 г., по приходам.",
    "Browse by parish; for name indexes use irishgenealogy.ie and FamilySearch.",
    "Листайте по приходу; именные указатели — на irishgenealogy.ie и FamilySearch.")
add("irishgenealogy", "IrishGenealogy.ie", "https://www.irishgenealogy.ie", "IE", (1700, 1970), "church vital", "free",
    "Irish civil records of births, marriages and deaths with images, and some church registers.",
    "Записи гражданской регистрации Ирландии со снимками и часть церковных книг.",
    "Civil registration starts in 1864 (non-Catholic marriages in 1845).",
    "Гражданская регистрация начинается в 1864 г. (некатолические браки — в 1845 г.).")
add("census_ie", "Census of Ireland 1901 and 1911", "https://www.census.nationalarchives.ie", "IE", (1901, 1911), "census", "free",
    "Every household of Ireland in 1901 and 1911, searchable by name and townland.",
    "Все хозяйства Ирландии в 1901 и 1911 гг., поиск по имени и местности.",
    "Search by townland, not only by name: the whole household shows who lived together.",
    "Ищите по местности, а не только по имени: всё хозяйство показывает, кто жил вместе.")
add("freebmd", "FreeBMD", "https://www.freebmd.org.uk", "GB", (1837, 1992), "vital", "free",
    "Index of civil registration births, marriages and deaths in England and Wales.",
    "Указатель гражданской регистрации рождений, браков и смертей Англии и Уэльса.",
    "Gives the quarter, district, volume and page to order the certificate from the GRO.",
    "Даёт квартал, округ, том и страницу, чтобы заказать свидетельство в GRO.")
add("nara", "US National Archives (NARA)", "https://www.archives.gov/research/genealogy", "US", (1790, 1990), "census military emigration", "mixed",
    "Federal censuses, military service and pension files, naturalisation and immigration records.",
    "Федеральные переписи, военные дела и пенсии, натурализация и иммиграция.",
    "Census images are free on FamilySearch; NARA guides say which series hold what.",
    "Снимки переписей бесплатно есть на FamilySearch; путеводители NARA объясняют, что в каких сериях.")
add("ellis_island", "Statue of Liberty – Ellis Island passenger search", "https://heritage.statueofliberty.org", "US *", (1820, 1957), "emigration", "free_account",
    "Ship manifests of passengers arriving in New York.",
    "Судовые списки пассажиров, прибывших в Нью-Йорк.",
    "Names were written as heard: search by first name, age and town of origin with wildcards.",
    "Имена писали на слух: ищите по имени, возрасту и месту выезда, со звёздочками.")
add("chronicling_america", "Chronicling America", "https://chroniclingamerica.loc.gov", "US", (1770, 1963), "newspapers", "free",
    "Historic American newspapers with full-text search (Library of Congress).",
    "Исторические американские газеты с полнотекстовым поиском (Библиотека Конгресса).",
    "Obituaries and local news name relatives and places of origin.",
    "Некрологи и местная хроника называют родных и места происхождения.")
add("volksbund", "Volksbund grave search", "https://www.volksbund.de/erinnern-gedenken/graebersuche-online", "DE *", (1914, 1945), "graves military", "free",
    "German war graves of both world wars, including Soviet and other foreign dead buried in Germany.",
    "Военные захоронения обеих мировых войн в Германии, включая советских и других иностранцев.",
    "Search by surname and date of birth; check spelling variants.",
    "Ищите по фамилии и дате рождения; пробуйте варианты написания.")

# ---------- Western, Northern, Central and Southern Europe
add("icrc_pow_1914", "ICRC prisoners of the First World War", "https://grandeguerre.icrc.org", "* DE FR GB IT AT RU", (1914, 1918), "military", "free",
    "Index cards and lists of about two million prisoners of war of 1914–1918 kept by the Red Cross.",
    "Картотека и списки около двух миллионов военнопленных 1914–1918 гг., которые вёл Красный Крест.",
    "Search by surname; the cards point to lists with the camp, unit and home place.",
    "Ищите по фамилии; карточки ведут к спискам с лагерем, частью и местом жительства.")
add("cwgc", "Commonwealth War Graves Commission", "https://www.cwgc.org", "GB * IE", (1914, 1947), "military graves", "free",
    "The dead of the British Commonwealth forces in both world wars and their graves or memorials.",
    "Погибшие в войсках Британского Содружества в обеих мировых войнах и их могилы или мемориалы.",
    "Records often name parents or a widow and their address.",
    "В записях часто названы родители или вдова и их адрес.")
add("scotlandspeople", "ScotlandsPeople", "https://www.scotlandspeople.gov.uk", "GB", (1553, 1970), "church vital census", "paid",
    "Scottish parish registers, civil registration from 1855 and censuses, with images.",
    "Церковные книги Шотландии, гражданская регистрация с 1855 г. и переписи — со снимками.",
    "Searching is free; viewing images costs credits. Scottish certificates name both parents, including the mother's maiden name.",
    "Поиск бесплатный, просмотр снимков — за кредиты. В шотландских свидетельствах указаны оба родителя и девичья фамилия матери.")
add("archion", "Archion (Protestant church books, Germany)", "https://www.archion.de", "DE PL", (1550, 1950), "church", "paid",
    "Scans of Protestant parish registers from German regional churches, including former eastern provinces.",
    "Сканы евангелических метрических книг немецких земельных церквей, включая бывшие восточные провинции.",
    "No name index: find the parish first (GenWiki, old gazetteers). A pass is bought by the month.",
    "Именного указателя нет: сначала найдите приход (GenWiki, старые справочники мест). Доступ покупают помесячно.")
add("genwiki", "GenWiki and CompGen (Germany)", "https://wiki.genealogy.net", "DE PL", (1500, 1950), "places catalogs trees", "free",
    "German genealogy wiki: places with their parishes and registry offices, address books, family-history databases.",
    "Немецкая генеалогическая вики: места с приходами и загсами, адресные книги, базы родословных.",
    "Look up the place to learn which parish and Standesamt it belonged to, and where its books are now.",
    "По месту узнаете, к какому приходу и загсу (Standesamt) оно относилось и где сейчас его книги.")
add("francearchives", "FranceArchives and departmental archives", "https://francearchives.gouv.fr", "FR", (1550, 1920), "church vital census military", "free",
    "Portal to French archives; each departmental archive publishes parish and civil registers online for free.",
    "Портал архивов Франции; каждый департаментский архив бесплатно выкладывает церковные книги и акты гражданского состояния.",
    "Find the commune, then its departmental archive site; ten-year tables (tables décennales) speed up the search.",
    "Найдите коммуну, затем сайт архива её департамента; десятилетние указатели (tables décennales) ускоряют поиск.")
add("memoire_des_hommes", "Mémoire des hommes", "https://www.memoiredeshommes.sga.defense.gouv.fr", "FR", (1790, 1962), "military", "free",
    "French military records: soldiers who died in the First World War, service and war records.",
    "Военные документы Франции: погибшие в Первую мировую, послужные и военные записи.",
    "The death card gives the date and place of birth — the way back to the birth register.",
    "В карточке погибшего есть дата и место рождения — путь к метрике.")
add("antenati", "Antenati (Italy)", "https://antenati.cultura.gov.it", "IT", (1800, 1940), "vital", "free",
    "Scans of Italian civil registers from the state archives, with a growing name index.",
    "Сканы итальянских актов гражданского состояния из госархивов, с растущим именным указателем.",
    "Browse by state archive, town and year; registers have annual indexes at the end.",
    "Листайте по архиву, коммуне и году; в конце каждой книги — годовой указатель.")
add("pares", "PARES (Spanish archives)", "https://pares.cultura.gob.es", "ES MX AR CL * ", (1400, 1960), "catalogs emigration military", "free",
    "Spanish state archives, including the Archive of the Indies and records of emigration to the Americas.",
    "Государственные архивы Испании, включая Архив Индий и документы об эмиграции в Америку.",
    "Search the catalogue by name; passenger and emigration records help trace families to Latin America.",
    "Ищите в каталоге по имени; списки пассажиров и эмигрантов помогают проследить семьи в Латинской Америке.")
add("digitarq", "Digitarq (Portuguese archives)", "https://digitarq.arquivos.pt", "PT BR", (1500, 1960), "church vital emigration catalogs", "free",
    "Portuguese national and district archives: parish registers, passports and emigration records.",
    "Национальный и окружные архивы Португалии: метрические книги, паспорта, эмиграция.",
    "Passport registers of the district archives are the key to Portuguese emigrants to Brazil.",
    "Паспортные книги окружных архивов — ключ к португальским эмигрантам в Бразилию.")
add("openarchieven", "Open Archives (Netherlands, Belgium)", "https://www.openarchieven.nl", "NL BE", (1600, 1950), "church vital census", "free",
    "Hundreds of millions of indexed Dutch and Belgian records from many archives in one search.",
    "Сотни миллионов проиндексированных записей Нидерландов и Бельгии из многих архивов в одном поиске.",
    "Dutch civil records name the parents of bride and groom: build the family generation by generation.",
    "В голландских записях о браке названы родители жениха и невесты: стройте семью поколение за поколением.")
add("arch_be", "State Archives of Belgium — search", "https://search.arch.be", "BE", (1600, 1950), "church vital", "free",
    "Parish and civil registers of Belgium, indexed and as scans.",
    "Церковные книги и акты гражданского состояния Бельгии — указатели и сканы.",
    "Search persons by name; open the scan from the result.",
    "Ищите людей по имени; скан открывается из результата.")
add("riksarkivet", "Swedish National Archives (Riksarkivet)", "https://sok.riksarkivet.se", "SE FI", (1600, 1950), "church census", "free",
    "Swedish church books and household examination rolls (husförhörslängder), censuses and more, free online.",
    "Шведские церковные книги и «книги опроса прихожан» (husförhörslängder), переписи и другое — бесплатно.",
    "Household examination rolls follow a family year by year and give the parish of birth of each member.",
    "Книги опроса прихожан ведут семью год за годом и дают приход рождения каждого.")
add("digitalarkivet", "Digitalarkivet (Norway)", "https://www.digitalarkivet.no", "NO", (1600, 1950), "church census emigration", "free",
    "Norwegian church books, censuses and emigration lists, with transcriptions.",
    "Церковные книги, переписи и списки эмигрантов Норвегии с расшифровками.",
    "Farm names change with moves: follow the farm as well as the surname.",
    "Фамилии по названию хутора меняются при переездах: следите и за хутором, а не только за фамилией.")
add("danishfamilysearch", "Danish Family Search", "https://www.danishfamilysearch.com", "DK", (1600, 1950), "church census", "free",
    "Danish censuses and church books indexed by volunteers, linked to the scans of the Danish National Archives.",
    "Датские переписи и церковные книги, проиндексированные добровольцами, со ссылками на сканы Госархива Дании.",
    "Censuses every few years show the household; church books confirm births and marriages.",
    "Переписи каждые несколько лет показывают состав семьи; церковные книги подтверждают рождения и браки.")
add("hiski", "HisKi (Finland)", "https://hiski.genealogia.fi", "FI", (1600, 1950), "church", "free",
    "Transcribed Finnish parish registers of baptisms, marriages and burials.",
    "Расшифрованные финские книги крещений, браков и погребений.",
    "Search by parish and name; the originals are in the National Archives' digital archive.",
    "Ищите по приходу и имени; оригиналы — в цифровом архиве Национального архива.")
add("hungaricana", "Hungaricana", "https://hungaricana.hu", "HU SK RO RS HR", (1700, 1950), "directories newspapers catalogs", "free",
    "Hungarian cultural heritage portal: archival records, directories, newspapers and maps with full-text search.",
    "Портал культурного наследия Венгрии: архивные документы, справочники, газеты и карты с полнотекстовым поиском.",
    "Search names in Hungarian spelling, also for places that are now in Slovakia, Romania, Serbia or Croatia.",
    "Ищите имена в венгерском написании, в том числе для мест, которые теперь в Словакии, Румынии, Сербии и Хорватии.")

# ---------- Latin America
add("familysearch_latam", "FamilySearch — Latin American collections", "https://www.familysearch.org/search/catalog", "MX BR AR CL PE CO CU UY PY VE EC BO GT CR", (1550, 1990),
    "church vital census", "free_account",
    "The largest online body of Latin American parish and civil registers: Mexico, Brazil, Argentina, Chile, Peru and the rest.",
    "Крупнейшее собрание латиноамериканских метрик и актов гражданского состояния в сети: Мексика, Бразилия, Аргентина, Чили, Перу и другие.",
    "Search the catalogue by country → state or province → municipality; Catholic baptisms usually name grandparents and godparents.",
    "Ищите в каталоге: страна → штат или провинция → муниципалитет; в католических записях о крещении обычно названы деды и крёстные.")
add("agn_mexico", "General Archive of the Nation (Mexico)", "https://www.gob.mx/agn", "MX", (1520, 1990), "catalogs emigration", "request",
    "National archive of Mexico: colonial and national records, immigration registers of foreigners.",
    "Национальный архив Мексики: колониальные и государственные документы, регистрация иностранцев.",
    "Immigration registration cards of foreigners (1926–1951) carry photographs and places of origin.",
    "Регистрационные карточки иностранцев (1926–1951) — с фотографиями и местом происхождения.")
add("arquivo_nacional_br", "National Archives of Brazil (SIAN)", "https://sian.an.gov.br", "BR", (1800, 1990), "emigration catalogs", "free_account",
    "Brazilian national archive: immigration and naturalisation records, passenger lists of the port of Rio de Janeiro.",
    "Национальный архив Бразилии: иммиграция, натурализация, списки пассажиров порта Рио-де-Жанейро.",
    "Search the SIAN catalogue by name; for São Paulo look at the Museu da Imigração.",
    "Ищите в каталоге SIAN по имени; по Сан-Паулу — Museu da Imigração.")
add("museu_imigracao", "Museu da Imigração (São Paulo)", "https://museudaimigracao.org.br", "BR", (1882, 1978), "emigration", "free",
    "Records of the immigrants' hostel of São Paulo: arrivals, families, places of origin and destinations.",
    "Документы приюта иммигрантов Сан-Паулу: прибытие, семьи, места происхождения и назначения.",
    "Families arrived together: the entry gives every member and the plantation they were sent to.",
    "Семьи приезжали вместе: запись даёт всех членов семьи и фазенду, куда их направили.")
add("hemeroteca_br", "Hemeroteca Digital Brasileira", "https://bndigital.bn.gov.br/hemeroteca-digital", "BR PT", (1740, 2000), "newspapers", "free",
    "Brazilian historical newspapers of the National Library with full-text search.",
    "Исторические газеты Бразилии Национальной библиотеки с полнотекстовым поиском.",
    "Ship arrivals, notices and obituaries were printed in the papers; search by name and decade.",
    "В газетах печатали прибытие судов, объявления и некрологи; ищите по имени и десятилетию.")
add("cemla", "CEMLA — arrivals in Argentina", "https://cemla.com", "AR UY", (1882, 1960), "emigration", "paid",
    "Passenger arrivals in Buenos Aires compiled by the Centre for Latin American Migration Studies.",
    "Прибытия пассажиров в Буэнос-Айрес, собранные Центром латиноамериканских миграционных исследований.",
    "Spellings vary a lot: try Italian, Spanish, Russian and German forms of the name; a search certificate is paid.",
    "Написания сильно разнятся: пробуйте итальянскую, испанскую, русскую и немецкую формы; справка о поиске платная.")
add("agn_argentina", "General Archive of the Nation (Argentina)", "https://www.argentina.gob.ar/interior/archivo-general-de-la-nacion", "AR", (1580, 1990), "census catalogs", "request",
    "National archive of Argentina: colonial and national censuses, immigration and administrative records.",
    "Национальный архив Аргентины: колониальные и национальные переписи, иммиграция, административные документы.",
    "National censuses of 1869 and 1895 are also on FamilySearch.",
    "Национальные переписи 1869 и 1895 гг. есть и на FamilySearch.")
add("archivo_nacional_cl", "National Archive of Chile", "https://www.archivonacional.gob.cl", "CL", (1540, 1990), "catalogs vital", "request",
    "National archive of Chile: notarial, judicial and administrative records, civil registry copies.",
    "Национальный архив Чили: нотариальные, судебные и административные документы, копии регистрации.",
    "Notarial records (wills, sales of land) often name several generations.",
    "Нотариальные документы (завещания, купля земли) часто называют несколько поколений.")

out = Path(__file__).resolve().parent.parent / "src" / "genealogy_mcp" / "data" / "sources.json"
ids = [s["id"] for s in S]
assert len(ids) == len(set(ids)), "duplicate ids"
out.write_text(json.dumps(S, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(S), "sources →", out)
