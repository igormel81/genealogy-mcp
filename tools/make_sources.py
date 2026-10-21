"""Writes src/genealogy_mcp/data/sources.json. Edit the list here, then: python3 tools/make_sources.py

Every entry: id, name, url, countries (ISO codes, "*" = worldwide), years [from, to], records (kinds),
access (free | free_account | paid | request | mixed), about / about_ru (what it is), how / how_ru (how to search
it well, pitfalls), search (optional URL template: {q} {given} {surname} {year_from} {year_to} {place}).
"""
import json
from pathlib import Path

S = []


def add(id, name, url, countries, years, records, access, about, about_ru, how, how_ru, search=None):
    S.append({"id": id, "name": name, "url": url, "countries": countries.split(), "years": list(years) if years else [0, 9999],
              **({"coverage_known": False} if years is None else {}),
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
add("nashipredki", "NashiPredki (Наши предки)", "https://nashipredki.com", "RU UA BY", (1700, 1930), "church revision confession places trees", "mixed",
    "Volunteer indexes of parish registers, revision lists and confession lists, with pages for persons and villages that gather what has been indexed.",
    "Индексы метрических книг, ревизских сказок и исповедных ведомостей, сделанные добровольцами; страницы персон и сёл собирают то, что уже проиндексировано.",
    "Search the village page as well as the name: it shows which books and years are indexed (and so which are not). An index line is a pointer — open the scan and cite archive, fond, opis, delo and folio.",
    "Смотрите не только поиск по имени, но и страницу села: на ней видно, какие книги и годы проиндексированы (а значит, какие нет). Строка индекса — наводка: откройте скан и ссылайтесь на архив, фонд, опись, дело, лист.")
add("metricabook", "Archive of metric books of Russia (metricabook.ru)", "https://metricabook.ru", "RU", (1855, 1911), "church", "free",
    "Scans of parish registers arranged by region, district and church, mostly from the second half of the 19th century to the 1910s.",
    "Сканы метрических книг по регионам, уездам и церквям, в основном второй половины XIX — 1910-х годов.",
    "There is no name index: find the church of the village first (the parish, not the village, is the unit), then read the years page by page. Note the archive citation printed with the scan.",
    "Поиска по именам нет: сначала найдите церковь села (единица — приход, а не село), затем читайте годы постранично. Записывайте архивный шифр, указанный при скане.")
add("rodovod", "Rodovid (Родовід)", "https://ru.rodovid.org", "* RU UA BY", (1500, 2025), "trees", "free",
    "A free Russian-language shared family tree with pages per person and per surname.",
    "Бесплатное русскоязычное общее семейное древо со страницами персон и фамилий.",
    "Use it to find other researchers of the same family and their leads; many profiles cite no document — treat them as hints, never as proof.",
    "Помогает найти других исследователей того же рода и их наводки; у многих профилей нет ссылок на документы — это подсказки, а не доказательства.")
add("doroga_pamyati", "Road of Memory (Doroga Pamyati)", "https://1418museum.ru", "RU UA BY MD *", (1941, 1945), "military", "free",
    "The Russian Ministry of Defence's memorial database of participants of the Second World War: photographs and cards with data from the war databases, filled in by relatives.",
    "Мемориальная база Минобороны России об участниках Великой Отечественной войны: фотографии и карточки с данными из военных баз, их дополняют родственники.",
    "The cards repeat Pamyat Naroda and OBD Memorial data and add family photographs: a photo or a home village found here leads back to the original documents there.",
    "Карточки повторяют данные «Памяти народа» и ОБД «Мемориал» и добавляют семейные фото: найденные здесь снимок или родное село ведут обратно к подлинным документам там.")
add("moypolk", "Immortal Regiment (Bessmertny Polk)", "https://www.moypolk.ru", "RU UA BY MD *", (1941, 1945), "military", "free",
    "Stories and photographs of Second World War soldiers and home-front workers posted by their families.",
    "Истории и фотографии фронтовиков и тружеников тыла, которые публикуют их семьи.",
    "Written from family memory, not from documents: dates and units may be wrong. Check every fact in Pamyat Naroda and OBD Memorial; the author of a story may be a relative to contact.",
    "Написано по семейной памяти, а не по документам: даты и части могут быть неточны. Проверяйте каждый факт в «Памяти народа» и ОБД «Мемориал»; автор рассказа — возможно, родственник, с которым стоит связаться.")
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
add("genealogica_ro", "genealogica.ro", "https://genealogica.ro", "RO", (1800, 1945), "church vital census", "mixed",
    "An index of parish and civil registers and censuses of the Old Kingdom of Romania.",
    "Индекс метрических книг, актов гражданского состояния и переписей Старого королевства Румынии.",
    "The default search is fuzzy and by prefix: for one exact spelling set the search options to exact match (in the result URL numTypos=0&prefixSearch=false), narrow by county (judet) and by years (from/until, up to 1945). Searches are limited per hour — plan the name forms first (name_variants) and log what you ran.",
    "По умолчанию поиск нечёткий и по началу слова: для одного точного написания включите точное совпадение (в адресе результатов numTypos=0&prefixSearch=false), сузьте по уезду (judet) и годам (from/until, не позже 1945). Число поисков в час ограничено — заранее составьте формы имени (name_variants) и записывайте, что уже искали.")
add("bessarabia_genealogy", "Genealogy of Bessarabia (bessarabia.name)", "https://bessarabia.name", "MD UA", (1812, 1944), "catalogs places church", "free",
    "A private project with indexed parish registers and revision lists, family trees and a separate document collection. Indexing covers selected books, not all of Bessarabia.",
    "Частный проект: индексированные метрики и ревизские сказки, деревья и отдельная коллекция документов. Проиндексированы отдельные книги, а не вся Бессарабия.",
    "Start here to learn which uezd and parish a village belonged to and which fond holds its books; then read the books themselves (FamilySearch catalogue, National Archives of Moldova).",
    "Начинайте здесь, чтобы узнать уезд и приход села и фонд, где лежат его книги; затем читайте сами книги (каталог FamilySearch, Национальный архив Молдовы).")
add("deportari_md", "Deportations from Bessarabia (deportari.org)", "https://deportari.org", "MD UA", (1940, 1956), "deportation repression", "free",
    "Lists of people deported from Bessarabia and the Moldavian SSR in 1941–1951 (the waves of June 1941, July 1949 and April 1951), arranged by village.",
    "Списки депортированных из Бессарабии и Молдавской ССР в 1941–1951 годах (волны июня 1941, июля 1949 и апреля 1951), по сёлам.",
    "Browse the list of the village, not only the name: whole families were deported together, and names are in Russian and Romanian forms (name_variants). The personal file is in the National Archives of Moldova or the archive of the Information and Security Service.",
    "Смотрите список села, а не только поиск по имени: депортировали целыми семьями, а имена записаны в русском и румынском виде (name_variants). Личное дело — в Национальном архиве Молдовы или архиве Службы информации и безопасности.")
add("cartea_memoriei_md", "Cartea Memoriei (Moldova): catalogue of the victims of communist totalitarianism", "", "MD", (1937, 1991), "repression deportation", "request",
    "A printed catalogue in four volumes (Chișinău, 1999–2005, coordinated by Elena Postică) of people from Moldova deported, arrested or killed by the Soviet regime, grouped by place.",
    "Печатный каталог в четырёх томах (Кишинёв, 1999–2005, координатор Елена Постикэ) жителей Молдовы, депортированных, арестованных или погибших при советской власти, по местам.",
    "Look up the village: an entry gives the year, the kind of repression and often the place of exile. Libraries in Moldova and Romania hold it; JewishGen has an index of the Jewish victims from it.",
    "Ищите по селу: запись даёт год, вид репрессии и часто место ссылки. Есть в библиотеках Молдовы и Румынии; на JewishGen — указатель еврейских жертв по нему.")
add("dmitriev_1772", "Moldavian censuses of 1772–1774 (Dmitriev, «Молдавия в эпоху феодализма», vol. VII)", "", "MD RO UA", (1772, 1774), "census books", "request",
    "P. G. Dmitriev (comp.), «Молдавия в эпоху феодализма», vol. VII, in two parts (Kishinev: Shtiintsa, 1975): the Russian-administered censuses of the Principality of Moldavia of 1772–1773 and 1774, household by household with the heads of households by name, from the originals in RGADA (fond 293).",
    "П. Г. Дмитриев (сост.), «Молдавия в эпоху феодализма», т. VII, в двух частях (Кишинёв: Штиинца, 1975): переписи Молдавского княжества 1772–1773 и 1774 годов, проведённые русской администрацией, — подворно, с именами глав дворов, по подлинникам РГАДА (ф. 293).",
    "The earliest name list for most Moldavian and Bessarabian villages, but with gaps: the 1774 census of Codru ținut has not survived, and for Fălciu only the number of households is given. Villages appear under the ținut of the time; the head of household is often named by a given name and a nickname or father's name rather than a fixed surname.",
    "Самый ранний поимённый список для большинства сёл Молдавии и Бессарабии, но с пробелами: перепись 1774 года по Кодру не сохранилась, а по Фэлчиу дано только число дворов. Сёла — по тогдашним цинутам; глава двора часто назван по имени и прозвищу или имени отца, а не постоянной фамилией.")
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

# ---------- Germany and German-speaking lands
add("verlustlisten", "Casualty lists of WWI (Verlustlisten 1. Weltkrieg)", "https://des.genealogy.net", "DE AT PL", (1914, 1919), "military", "free",
    "Indexed Prussian, Bavarian, Saxon and Württemberg casualty lists of the First World War, about 8.5 million entries.",
    "Указатель прусских, баварских, саксонских и вюртембергских списков потерь Первой мировой, около 8,5 млн записей.",
    "Search by surname and place of birth: entries give origin and fate (killed, wounded, captured). Unit details were omitted from late 1916 until late 1918, so not every entry identifies a regiment.",
    "Ищите по фамилии и месту рождения: в записи — происхождение и судьба (убит, ранен, в плену). С конца 1916 до конца 1918 г. часть не указывали: не каждая запись даёт полк.")
add("gedbas", "GEDBAS (genealogy.net)", "https://gedbas.genealogy.net", "DE PL AT CH", (1500, 1950), "trees", "free",
    "Family trees uploaded by German genealogists, searchable by name and place.",
    "Родословные, загруженные немецкими генеалогами, поиск по имени и месту.",
    "Other people's trees: take them as leads and check every fact in the parish books.",
    "Чужие деревья: используйте как наводки и проверяйте каждый факт по церковным книгам.")
add("online_ofb", "Online local family books (Online-OFB)", "https://www.online-ofb.de", "DE PL FR", (1600, 1900), "church trees", "free",
    "Ortsfamilienbücher: all families of a parish reconstructed from its registers, place by place.",
    "Ortsfamilienbücher: все семьи прихода, восстановленные по его книгам, по населённым пунктам.",
    "If your village has an OFB, it often goes back to the 1600s; cite the parish register it names, not the book.",
    "Если для вашей деревни есть OFB, он часто уходит в XVII век; ссылайтесь на названную в нём метрику, а не на книгу.")
add("ddb", "German Digital Library (Deutsche Digitale Bibliothek)", "https://www.deutsche-digitale-bibliothek.de", "DE", (1490, 2000), "books newspapers directories catalogs", "free",
    "One search over German libraries, archives and museums: address books, newspapers, archive finding aids.",
    "Единый поиск по библиотекам, архивам и музеям Германии: адресные книги, газеты, описи архивов.",
    "Use the newspaper portal (Deutsches Zeitungsportal) for notices, and finding aids to locate files in state archives.",
    "Газетный портал (Deutsches Zeitungsportal) — для объявлений; описи — чтобы найти дела в земельных архивах.",
    "https://www.deutsche-digitale-bibliothek.de/searchresults?query={q}")
add("bundesarchiv", "Federal Archives of Germany (Bundesarchiv)", "https://www.bundesarchiv.de", "DE", (1495, 1990), "military catalogs", "request",
    "German federal records: Wehrmacht personnel (former WASt / Deutsche Dienststelle), GDR records, the 1939 minority census.",
    "Федеральный архив Германии: личные дела вермахта (бывшая WASt), документы ГДР, перепись меньшинств 1939 г.",
    "Wehrmacht soldiers and Soviet POWs registered by Germany: request from the department Deutsches Reich in Berlin-Tegel (responsible since September 2025; former PA/WASt holdings).",
    "Солдаты вермахта и советские военнопленные в немецком учёте: запрос в отдел Deutsches Reich в Берлине-Тегеле (с сентября 2025 г.; документы бывшего отдела PA/WASt).")
add("bbld", "Baltic Biographical Lexicon (BBLD)", "https://bbld.de", "EE LV LT", (1500, 2025), "nobility clergy directories", "free",
    "Biographies of Baltic Germans: nobility, clergy, scholars, officials of Estland, Livland and Courland.",
    "Биографии прибалтийских немцев: дворяне, пасторы, учёные, чиновники Эстляндии, Лифляндии и Курляндии.",
    "Each entry cites its sources — follow them to church books and university registers.",
    "Каждая статья ссылается на источники — по ним выходите на церковные книги и университетские матрикулы.")
add("odessa3", "Odessa3 — Black Sea Germans", "https://www.odessa3.org", "UA MD RU", (1795, 1940), "church census emigration", "free",
    "Transcribed records of German colonists in the Black Sea region and Bessarabia: church books, censuses, emigration lists.",
    "Расшифровки документов немецких колонистов Причерноморья и Бессарабии: церковные книги, переписи, списки эмигрантов.",
    "Browse by colony; many transcriptions come from the St Petersburg Lutheran consistory duplicates.",
    "Смотрите по колонии; многое расшифровано из дубликатов Санкт-Петербургской лютеранской консистории.")
# ---------- Jewish genealogy
add("jri_poland", "JRI-Poland (Jewish Records Indexing)", "https://www.jri-poland.org", "PL UA BY LT", (1808, 1940), "church vital", "free_account",
    "Index of Jewish births, marriages and deaths from Polish archives — over 6 million records.",
    "Указатель еврейских рождений, браков и смертей из польских архивов — более 6 млн записей.",
    "Search uses Beider–Morse phonetic matching; sign in to a free researcher account to see full results; the index gives the archive, year and act number to order the scan.",
    "Поиск использует фонетику Beider–Morse; для полных результатов нужен бесплатный аккаунт; указатель даёт архив, год и номер акта, чтобы заказать скан.")
add("gesher_galicia", "Gesher Galicia", "https://www.geshergalicia.org", "PL UA", (1772, 1941), "vital census maps", "mixed",
    "Jewish and general records of Galicia: vital records indexes, cadastral maps, school and tax lists.",
    "Документы Галиции, еврейские и общие: указатели метрик, кадастровые карты, школьные и налоговые списки.",
    "The All Galicia Database is free; some other content requires membership. Vital-record projects include 1940–1941. Cadastral maps show house numbers.",
    "All Galicia Database бесплатна; часть других материалов доступна членам общества. Есть проект метрик 1940–1941 гг. На кадастровых картах — номера домов.")
add("litvaksig", "LitvakSIG", "https://www.litvaksig.org", "LT BY LV", (1795, 1940), "revision census vital", "mixed",
    "Lithuanian Jewish records: revision lists, family lists, box tax, vital records, internal passports.",
    "Еврейские документы Литвы: ревизские сказки, посемейные списки, коробочный сбор, метрики, паспорта.",
    "Indexes appear on JewishGen; the newest translations are for donors first, then free.",
    "Указатели выходят на JewishGen; новейшие переводы сначала для жертвователей, потом бесплатно.")
add("stevemorse", "Steve Morse One-Step tools", "https://stevemorse.org", "US * RU PL", (1790, 1963), "emigration census vital", "free",
    "Search forms for Ellis Island, Castle Garden, US censuses (1790–1950) and other ports (Philadelphia manifests 1800–1963), plus calendar and alphabet converters. The forms are free; linked databases may require a paid subscription.",
    "Формы поиска по Эллис-Айленду, Касл-Гардену, переписям США (1790–1950), другим портам (Филадельфия 1800–1963), конвертеры календарей и алфавитов. Формы бесплатны; внешние базы могут требовать платную подписку.",
    "Use 'sounds like' (Daitch–Mokotoff) and search by town or ship when the name is mangled.",
    "Используйте «звучит как» (Daitch–Mokotoff) и ищите по городу или судну, если имя искажено.")
# ---------- British Isles
add("freecen", "FreeCEN", "https://www.freecen.org.uk", "GB", (1841, 1911), "census", "free",
    "Volunteer transcriptions of UK censuses 1841–1911 (coverage varies by county).",
    "Расшифровки переписей Великобритании 1841–1911 гг., сделанные добровольцами (охват по графствам разный).",
    "Check the coverage page first; fill gaps with FamilySearch indexes.",
    "Сначала проверьте страницу охвата; пробелы закрывайте указателями FamilySearch.")
add("freereg", "FreeREG", "https://www.freereg.org.uk", "GB", (1538, 1900), "church", "free",
    "Volunteer transcriptions of English, Welsh and Scottish parish registers: baptisms, marriages, burials.",
    "Расшифровки приходских книг Англии, Уэльса и Шотландии: крещения, браки, погребения.",
    "Before 1837 parish registers are the main source in England; check the original in the county record office.",
    "До 1837 г. церковные книги — главный источник в Англии; подлинник смотрите в архиве графства.")
add("tna_discovery", "The National Archives (UK) — Discovery", "https://discovery.nationalarchives.gov.uk", "GB IE", (1086, 2000), "military catalogs emigration", "mixed",
    "Catalogue of The National Archives and 2,500 other UK archives; many service records, wills and passenger lists online.",
    "Каталог Национального архива Великобритании и 2500 других архивов; многие послужные списки, завещания, списки пассажиров — в сети.",
    "Search the catalogue by name: WWI medal cards, army and navy records and pre-1858 wills are downloadable.",
    "Ищите по имени: наградные карточки Первой мировой, документы армии и флота, завещания до 1858 г. можно скачать.",
    "https://discovery.nationalarchives.gov.uk/results/r?_q={q}")
add("gro", "General Register Office (England and Wales)", "https://www.gro.gov.uk", "GB", (1837, 2025), "vital", "free_account",
    "Indexes of births (with mother's maiden name) and deaths (with age) from 1837; certificates and cheap PDF copies.",
    "Указатели рождений (с девичьей фамилией матери) и смертей (с возрастом) с 1837 г.; свидетельства и недорогие PDF-копии.",
    "Online indexes have gaps: births 1837–1934 and from 1984; deaths 1837–1957 and from 1984 (recent indexes end two years ago). Use FreeBMD or other indexes for gaps; certificate/PDF/image orders cost money.",
    "В онлайн-указателях есть пробелы: рождения 1837–1934 и с 1984 г., смерти 1837–1957 и с 1984 г. (новые данные — до двух лет назад). Пробелы ищите в FreeBMD и других указателях; свидетельства, PDF и снимки платные.")
add("welsh_newspapers", "Welsh Newspapers (National Library of Wales)", "https://newspapers.library.wales", "GB", (1804, 1919), "newspapers", "free",
    "Over a million pages of Welsh newspapers with full-text search.",
    "Более миллиона страниц валлийских газет с полнотекстовым поиском.",
    "Search a name in quotes with the town; notices of deaths and marriages are short.",
    "Ищите имя в кавычках вместе с городом; извещения о смертях и браках короткие.",
    "https://newspapers.library.wales/search?query={q}")
# ---------- Canada, Australia, New Zealand
add("lac", "Library and Archives Canada", "https://www.bac-lac.gc.ca", "CA", (1825, 1950), "census emigration military", "free",
    "Canadian censuses 1825–1931, passenger lists 1865–1935, CEF soldiers of WWI (full files), naturalisations.",
    "Переписи Канады 1825–1931, списки пассажиров 1865–1935, личные дела солдат CEF Первой мировой, натурализации.",
    "CEF personnel files are digitised in full; immigrants from the Russian Empire often appear as 'Galician', 'Austrian' or 'Russian'.",
    "Личные дела CEF оцифрованы полностью; выходцы из Российской империи часто записаны как «галичане», «австрийцы» или «русские».")
add("banq", "BAnQ — National Library and Archives of Quebec", "https://www.banq.qc.ca", "CA", (1621, 1950), "church vital newspapers catalogs", "free",
    "Quebec parish registers (civil copies), notarial records, newspapers and judicial archives.",
    "Церковные книги Квебека (гражданские копии), нотариальные акты, газеты и судебные архивы.",
    "Quebec Catholic registers are among the most complete in the world; marriages name both sets of parents.",
    "Католические книги Квебека — одни из самых полных в мире; записи о браке называют родителей обоих супругов.")
add("pier21", "Canadian Museum of Immigration at Pier 21", "https://pier21.ca", "CA", (1865, 1971), "emigration", "mixed",
    "Help with ship arrivals to Halifax and other Canadian ports; research guides and family-history service.",
    "Помощь по прибытию судов в Галифакс и другие порты Канады; руководства и служба семейной истории.",
    "Canadian arrival records for 1865–1935 are at LAC. The museum cannot access Canadian immigration records after 1935: request IRCC. Some later overseas departure lists are available. Research requests and record copies may incur fees.",
    "Канадские списки прибытия 1865–1935 гг. — в LAC. Музей не имеет доступа к канадским иммиграционным делам после 1935 г.: обращайтесь в IRCC. Есть отдельные поздние зарубежные списки отправления. За запросы и копии возможна плата.")
add("trove", "Trove (National Library of Australia)", "https://trove.nla.gov.au", "AU", (1803, 1995), "newspapers books directories", "free",
    "Millions of pages of Australian newspapers with full-text search, gazettes, books and directories.",
    "Миллионы страниц австралийских газет с полнотекстовым поиском, ведомости, книги, справочники.",
    "Most digitised newspapers end in 1954; exceptions include The Canberra Times through 1995. Search in quotes by state and decade; correct OCR text to help others.",
    "Большинство оцифрованных газет заканчивается 1954 г.; исключение — The Canberra Times до 1995 г. Ищите в кавычках по штату и десятилетию; исправляйте OCR.",
    "https://trove.nla.gov.au/search/category/newspapers?keyword={q}")
add("naa", "National Archives of Australia", "https://www.naa.gov.au", "AU", (1860, 2000), "military emigration", "free",
    "WWI and WWII service records (WWI digitised in full), immigration and naturalisation files, alien registration. Identifiable census forms before 2001 were destroyed after statistical processing.",
    "Послужные дела Первой и Второй мировых (Первая — оцифрована полностью), иммиграция, натурализация, учёт иностранцев. Именные переписные листы до 2001 г. уничтожались после статистической обработки.",
    "Many Russian-Empire migrants came via Harbin and Shanghai: search alien registration and naturalisation files.",
    "Многие выходцы из Российской империи приезжали через Харбин и Шанхай: ищите учёт иностранцев и натурализацию.")
add("paperspast", "Papers Past (New Zealand)", "https://paperspast.natlib.govt.nz", "NZ", (1839, 2010), "newspapers", "free",
    "New Zealand newspapers, magazines and parliamentary papers with full-text search.",
    "Газеты, журналы и парламентские документы Новой Зеландии с полнотекстовым поиском.",
    "Shipping columns list arriving passengers; search the ship's name as well as the person's.",
    "В морской хронике — списки прибывших; ищите и по названию судна, и по имени.",
    "https://paperspast.natlib.govt.nz/newspapers?query={q}")
add("nz_bdm", "New Zealand BDM historical records", "https://www.bdmhistoricalrecords.dia.govt.nz", "NZ", (1840, 2000), "vital", "free",
    "New Zealand historical indexes: births of living people at least 100 years ago; births of deceased people if born at least 80 years ago or dead at least 50; stillbirths at least 50; deaths at least 50 or born at least 80 years ago; marriages at least 75 years ago.",
    "Исторические указатели Новой Зеландии: рождения живых — не менее 100 лет назад; умерших — при рождении не менее 80 лет или смерти не менее 50 лет назад; мертворождения — 50 лет; смерти — 50 лет либо рождение не менее 80 лет назад; браки — 75 лет.",
    "Order printouts cheaply: they name parents, which certificates of other countries often omit.",
    "Распечатки заказываются недорого и называют родителей, чего часто нет в документах других стран.")
add("usgenweb", "USGenWeb", "https://usgenweb.org", "US", (1620, 1950), "places vital census graves", "free",
    "Volunteer county pages for every US state: transcribed records, cemetery lists, courthouse addresses.",
    "Добровольческие страницы округов всех штатов США: расшифровки, списки кладбищ, адреса судов.",
    "Find the county first: in the US most records (deeds, probate, marriages) are kept by the county.",
    "Сначала найдите округ: в США большинство документов (земля, наследство, браки) хранит округ.")
# ---------- Central Europe and the North
add("actapublica", "Acta Publica (Moravia, Czechia)", "https://www.actapublica.eu", "CZ", (1600, 1950), "church vital", "free_account",
    "Scanned parish and civil registers of the Moravian Land Archive in Brno and other Czech archives.",
    "Сканы приходских и гражданских книг Моравского земского архива в Брно и других архивов Чехии.",
    "Czech registers are not indexed: find the parish (Farnost) of the village first, then browse by year; other regional archives run their own viewers.",
    "Чешские книги не индексированы: найдите приход (farnost) деревни и листайте по годам; другие областные архивы имеют свои просмотрщики.")
add("narc_fi", "National Archives of Finland — Astia", "https://astia.narc.fi/uusiastia", "FI", (1600, 1950), "church census", "free",
    "Astia provides access to digitised Finnish church books (communion books, births, marriages, deaths) and other records; it replaced the former Digital Archive.",
    "Astia: оцифрованные церковные книги Финляндии (причастные книги, рождения, браки, смерти) и другие документы; сервис заменил прежний Digital Archive.",
    "Communion books (rippikirjat) follow families house by house like Russian confession lists; HisKi gives the index.",
    "Причастные книги (rippikirjat) идут по домам, как исповедные ведомости; указатель — в HisKi.")
add("bg_archives", "State Archives of Bulgaria", "https://archives.government.bg", "BG", (1800, 1990), "catalogs church vital", "mixed",
    "Bulgarian state archives: parish registers, civil registration, Ottoman-era documents, refugee files.",
    "Государственные архивы Болгарии: метрики, гражданская регистрация, документы османского времени, дела беженцев.",
    "Orthodox registers use the Julian calendar until 1916; many Bessarabian Bulgarians are found in Moldovan and Odesa archives.",
    "Православные книги — по юлианскому календарю до 1916 г.; бессарабских болгар ищите в архивах Молдовы и Одессы.")
add("metryki", "Metryki (genealodzy.pl) — scans", "https://metryki.genealodzy.pl", "PL UA LT BY", (1600, 1950), "church vital", "free",
    "Scans of parish and civil-religious registers from Polish and some Ukrainian and Lithuanian archives, linked from Geneteka.",
    "Сканы приходских и гражданско-церковных книг из польских и некоторых украинских и литовских архивов, связанные с Geneteka.",
    "Open the scan straight from a Geneteka hit; the act number leads to the page.",
    "Открывайте скан прямо из находки в Geneteka; номер акта ведёт к странице.")
add("poznan_project", "Poznań Project — marriages 1800–1899", "http://poznan-project.psnc.pl", "PL DE", (1800, 1899), "church vital", "free",
    "Index of nearly all marriages in the Grand Duchy of Posen in the 19th century, Catholic, Protestant and Jewish.",
    "Указатель почти всех браков Великого княжества Познанского в XIX веке — католических, протестантских, еврейских.",
    "A marriage entry gives ages and the parish — the way back to both births.",
    "Запись о браке даёт возраст и приход — путь назад к рождению обоих.")
add("georgia_archives", "National Archives of Georgia", "https://archive.gov.ge", "GE", (1800, 1990), "church vital catalogs", "request",
    "Parish registers of Orthodox, Armenian, Catholic and Lutheran churches of Georgia, Tiflis governorate records.",
    "Метрические книги православных, армянских, католических и лютеранских церквей Грузии, документы Тифлисской губернии.",
    "Request by church and year; German colonies of the Caucasus are in the Lutheran registers.",
    "Запрос по церкви и году; немецкие колонии Кавказа — в лютеранских книгах.")
add("kazakhstan_archives", "Central State Archive of Kazakhstan", "https://www.cga.kz", "KZ", (1700, 1991), "church vital catalogs deportation", "request",
    "Central State Archive in Almaty: records of imperial and Soviet Kazakhstan, including documents from the early 18th century.",
    "Центральный государственный архив в Алматы: документы дореволюционного и советского Казахстана, в том числе с начала XVIII века.",
    "Identify the province, parish and years in the fond guide; also check regional archives. For deportation and special-settlement files, ask which archive or Interior Ministry office holds the file.",
    "Найдите губернию/область, приход и годы в путеводителе фондов; проверьте и областные архивы. Для дел о депортации и спецпоселении уточняйте держателя дела в архиве или МВД.")
add("uzbekistan_archives", "National Archive of Uzbekistan / Uzarchive", "https://gov.uz/ru/archive", "UZ", (1850, 1991), "church vital catalogs deportation", "request",
    "Uzarchive agency and the National Archive of Uzbekistan (formerly the Central State Archive): a route to Turkestan and Soviet archival fonds.",
    "Агентство «Узархив» и Национальный архив Узбекистана (бывший Центральный государственный архив): поиск фондов Туркестана и советского периода.",
    "Use the agency's archive directory and services to identify the custodian, fond and years before requesting a file; not all records are at the national archive.",
    "По справочникам и услугам агентства сначала уточните держателя, фонд и годы, затем запрашивайте дело; не все документы находятся в национальном архиве.")
add("kyrgyzstan_archives", "Central State Archive of the Kyrgyz Republic", "https://www.archive.kg", "KG", (1850, 2015), "church vital catalogs deportation", "request",
    "Central State Archive in Bishkek; its published fond guide covers 1850–2015, including imperial and Soviet records.",
    "Центральный государственный архив в Бишкеке; опубликованный путеводитель фондов охватывает 1850–2015 гг., включая дореволюционные и советские документы.",
    "Start with the official Central State Archive fond guide; search the historical district and institution as well as the modern village name, and check regional archives.",
    "Начните с официального путеводителя ЦГА; ищите по историческому уезду и учреждению, а не только современному селу; проверяйте областные архивы.")
add("tajikistan_archives", "Main Archival Administration of Tajikistan", "https://archive.tj", "TJ", (1850, 1991), "church vital catalogs deportation", "request",
    "Official archival administration of Tajikistan: a route to central and regional state archives.",
    "Официальное Главное архивное управление Таджикистана: выход на центральный и областные государственные архивы.",
    "Ask the administration which archive holds records for the place, institution and years. Confirm availability and access before requesting parish, civil or special-settlement files.",
    "Уточните в управлении архив — держатель документов нужного места, учреждения и лет. Наличие и доступ к метрикам, актам и делам спецпоселенцев подтверждайте до заказа.")
add("turkmenistan_archives", "Main Archival Administration of Turkmenistan", "https://www.archive.gov.tm/ru", "TM", (1850, 1991), "church catalogs deportation", "request",
    "Official directory of the Central State Archive and regional archives of Turkmenistan. Civil-registration records are not deposited with this administration or its subordinate archives.",
    "Официальный справочник Центрального государственного и региональных архивов Туркменистана. Акты гражданского состояния в управление и подведомственные архивы не поступают.",
    "Identify the custodian through the official archive directory; ask about historical holdings and access. Request civil-registration records from the civil registry, not these archives.",
    "По официальному справочнику уточните держателя, состав исторических фондов и доступ. За актами гражданского состояния обращайтесь в ЗАГС, а не в эти архивы.")


# ---------- Direct catalogues and supporting sources used in practical research
# None means the full date span has not been established. [0, 9999] is a routing
# sentinel, not a claim about holdings; source_details displays "check the inventory".
ARCHIVE_SITES = [
    ("gato", "State Archive of Tula Region (ГАТО)", "https://gato.tularegion.ru", "RU", "church confession revision household catalogs", "Государственный архив Тульской области: сайт и справочный аппарат."),
    ("gaio", "State Archive of Ivanovo Region (ГАИО)", "https://af.ivarh.ru", "RU", "church confession revision catalogs", "Государственный архив Ивановской области: архивный фонд и справочный аппарат."),
    ("gako", "State Archive of Kostroma Region (ГАКО)", "https://kosarchive.ru", "RU", "church revision confession catalogs", "Государственный архив Костромской области: фонды, описи и публикации."),
    ("gavo_voronezh", "State Archive of Voronezh Region (ГАВО)", "https://gavo.arsvo.ru", "RU", "church confession revision catalogs", "Государственный архив Воронежской области: официальный сайт и каталоги."),
    ("ganiko", "Archive of Contemporary History of Kostroma Region (ГАНИКО)", "https://ganiko.org", "RU", "catalogs repression", "Государственный архив новейшей истории Костромской области: поиск фондов учреждений и организаций."),
    ("chekhov_archive", "Chekhov municipal archive (official municipal portal)", "https://agoch.ru", "RU", "household catalogs", "Архив муниципального округа Чехов: разделы и контакты архива на официальном портале муниципалитета."),
    ("niab_grodno", "National Historical Archives of Belarus in Grodno: inventories", "https://niab-grodno.by/science/", "BY PL", "church revision catalogs", "НИАБ в Гродно: электронные описи, сгруппированные по номерам фондов."),
    ("kyiv_city_archive", "State Archives of Kyiv City: fonds", "https://archive.kyivcity.gov.ua/funds", "UA", "catalogs", "Государственный архив города Киева: поиск фондов по названию, номеру и датам; в том числе фонды учебных заведений."),
    ("khmelnytsky_archive", "State Archives of Khmelnytskyi Region", "https://dahmo.gov.ua", "UA", "church catalogs", "Государственный архив Хмельницкой области: справочный аппарат и каталоги метрических книг."),
    ("gavo_volgograd", "State Archive of Volgograd Region: fonds", "https://gavo.volgograd.ru/fonds/", "RU", "church catalogs repression", "Государственный архив Волгоградской области: указатель фондов и описи."),
]
for sid, name, url, countries, kinds, about_ru in ARCHIVE_SITES:
    add(sid, name, url, countries, None, kinds, "mixed",
        "Direct archive or municipal portal: find the relevant fond and inventory; dates and online image access depend on the collection.", about_ru,
        "Search by historical parish, district or institution, then fond, inventory and file. A catalogue entry does not prove that images are online. Check access before a visit; do not send a request unless project policy and the owner allow it.",
        "Ищите по прежнему приходу, уезду или учреждению, затем по фонду, описи и делу. Наличие описи не означает наличия сканов. Проверяйте доступ; запросы — только если разрешают политика проекта и владелец.")

add("petrovy", "Petrovy: family and local history materials", "https://petrovy.su", "RU", None, "books revision places", "free",
    "A private family-history site with local-history material. Use relevant transcriptions as pointers to original records, not as a complete district index.",
    "Частный сайт семейной истории и краеведческих материалов. Подходящие расшифровки — наводки к оригиналам, а не полный указатель уезда.",
    "Browse the materials by village and topic; check the original archive reference and image before attaching a person.",
    "Просматривайте материалы по селу и теме; перед привязкой человека проверьте архивный шифр и оригинальную запись.")
add("soldat", "Soldat.ru: military reference works", "https://www.soldat.ru", "RU", None, "military directories", "free",
    "Military reference works, documents and search guidance; not a complete personal service-record database.",
    "Военные справочники, документы и методика поиска; это не полная база личных дел военнослужащих.",
    "Use the reference and documents sections to interpret units and abbreviations, then corroborate with the original military record.",
    "Справочники и документы помогают разобрать части и сокращения; биографические выводы подтверждайте первичным военным документом.")
add("pomnim", "Pomnim.online: burial database", "https://pomnim.online", "RU", None, "graves", "mixed",
    "Burial and cemetery search with separate paid services. Coverage depends on contributions and cemetery data.",
    "Поиск захоронений и кладбищ; отдельно предлагаются платные услуги. Полнота зависит от внесённых сведений.",
    "Search the surname and cemetery; verify the photograph, dates and identity. Do not order paid services automatically.",
    "Ищите по фамилии и кладбищу; проверяйте фото, даты и личность. Не заказывайте платные услуги автоматически.")
add("warheroes", "Heroes of the Country (Герои страны)", "https://warheroes.ru", "RU", None, "military books", "free",
    "Biographies and bibliographic references about decorated people; a secondary source, not proof of kinship.",
    "Биографии награждённых и библиографические ссылки; вторичный источник, не доказательство родства.",
    "Search by name and use cited books and award records to locate originals; distinguish namesakes.",
    "Ищите по имени, переходите к указанным книгам и наградным документам; различайте однофамильцев.")
add("ionb", "Ivanovo regional digital library", "https://elib.ionb.ru", "RU", None, "books directories newspapers", "mixed",
    "The regional digital library: local publications and reference books; access depends on the item.",
    "Электронная библиотека Ивановской области: краеведческие издания и справочники; доступ зависит от издания.",
    "Search the publication title, place and historical spelling; cite the edition and page, not just a search hit.",
    "Ищите по названию издания, месту и старому написанию; указывайте издание и страницу, а не только результат поиска.")
add("nbuv", "Vernadsky National Library of Ukraine: library portal", "https://irbis-nbuv.gov.ua", "UA", None, "books directories newspapers", "mixed",
    "Vernadsky Library / NAS library portal and catalogues. A bibliographic entry does not guarantee an online full text.",
    "Библиотечный портал и каталоги НБУВ/НАН Украины. Библиографическая запись не гарантирует доступ к полному тексту.",
    "Search author, title and place; follow the item link to establish image/text availability and cite the original page.",
    "Ищите по автору, заглавию и месту; по ссылке издания проверяйте доступ к тексту или сканам и цитируйте страницу оригинала.")
add("goskatalog", "State Catalogue of the Museum Fund of Russia", "https://goskatalog.ru", "RU", None, "catalogs books", "free",
    "Museum object catalogue: photographs, manuscripts, documents and other collection objects, not a comprehensive population register.",
    "Каталог музейных предметов: фотографии, рукописи, документы и другие предметы; не сплошной реестр населения.",
    "Search the name, place and object description; record the museum and inventory number. Check rights separately before reuse.",
    "Ищите по имени, месту и описанию предмета; запишите музей и инвентарный номер. Права на публикацию проверяйте отдельно.")
add("kounb", "Kostroma regional library: electronic local collection", "https://kounb.ru/index.php/knizhnye-pamyatniki/item/170-elektronnaya-kollektsiya-kraya", "RU", None, "books directories newspapers", "mixed",
    "The library's electronic local collection of Kostroma publications and book monuments.",
    "Электронная коллекция края Костромской областной библиотеки: местные издания и книжные памятники.",
    "Choose the period and title, then read the scan; OCR or a catalogue title alone does not establish a person's identity.",
    "Выберите период и заглавие, затем читайте скан; одно OCR-совпадение или название каталога не устанавливает личность.")
add("familio", "Familio: knowledge base and settlement reference works", "https://familio.org/knowledge-base", "RU UA BY MD", None, "places directories trees", "mixed",
    "Settlement reference works and family trees; basic reference access and optional paid features are separate.",
    "Справочники населённых мест и деревья; базовый доступ к справочникам и дополнительные платные возможности различаются.",
    "Use historical place entries to find parish and administrative names. User trees are leads: follow their documents.",
    "По историческим населённым пунктам уточняйте приход и административное деление. Чужие деревья — наводки: переходите к документам.")
add("genway", "Genway: user-contributed trees", "https://genway.ru", "RU UA BY", None, "trees", "mixed",
    "User-contributed genealogy service. Visibility and availability must be checked; a surname or tree owner is only a lead.",
    "Пользовательский генеалогический сервис. Доступность и видимость данных нужно проверять; фамилия или хранитель древа — только наводка.",
    "Check whether the service opens and what is visible without an account. Do not infer kinship from a surname match or investigate living people's current lives.",
    "Сначала проверьте доступность и что видно без входа. Не выводите родство из совпадения фамилии и не исследуйте нынешнюю жизнь живых людей.")
add("bessarabia_ru", "Bessarabia.ru: historical reference materials", "http://www.bessarabia.ru", "MD UA RO", None, "directories places books catalogs", "mixed",
    "Historical Bessarabian reference materials and archive guides; a different website from bessarabia.name.",
    "Исторические справочники Бессарабии и архивные путеводители; отдельный сайт, не bessarabia.name.",
    "Check availability and each publication's scope and date. Use institutional and settlement references to locate originals, not as a complete parish index.",
    "Проверяйте доступность, состав и дату каждого издания. Сведения об учреждениях и селениях помогают найти оригиналы, но не заменяют полный указатель метрик.")
add("familysearch_tree", "FamilySearch Family Tree", "https://www.familysearch.org/en/tree/find", "*", None, "trees", "free_account",
    "The collaborative family tree, distinct from the historical-record index and image catalogue.",
    "Общее древо пользователей, отдельное от индекса исторических записей и каталога сканов.",
    "Search the tree for leads; inspect attached sources and independently verify every relationship in the original record.",
    "Ищите в древе наводки; изучайте прикреплённые источники и независимо проверяйте каждую связь по оригинальной записи.")

# ---------- additional public resources encountered in recent research
add('hathitrust', 'HathiTrust Digital Library', 'https://www.hathitrust.org', '*', None, 'books directories newspapers', 'mixed',
    'Digitised research-library books and full-text discovery; reading and download rights vary by item.',
    'Оцифрованные библиотечные книги и полнотекстовый поиск; чтение и скачивание зависят от прав на издание.',
    'Search historical spellings and titles; distinguish a catalogue/full-text hit from an accessible page.',
    'Ищите старые написания и заглавия; различайте результат поиска и доступную страницу.')
add('google_books', 'Google Books', 'https://books.google.com', '*', None, 'books directories newspapers', 'mixed',
    'Book discovery with full views, previews or snippets depending on rights.',
    'Поиск книг с полным просмотром, фрагментами или сниппетами в зависимости от прав.',
    'Verify the edition and page in the scan. A snippet or API quota error is not a completed search of the book.',
    'Проверяйте издание и страницу по скану. Сниппет или ошибка квоты API не означает выполненный поиск по книге.')
add('gallica', 'Gallica — Bibliothèque nationale de France', 'https://gallica.bnf.fr', 'FR', None, 'books newspapers directories', 'free',
    'BnF digital library of books, periodicals and other heritage collections.',
    'Цифровая библиотека BnF: книги, периодика и другие исторические коллекции.',
    'Search name variants and dates; compare OCR with the page image and cite its persistent identifier.',
    'Ищите варианты имени и даты; сверяйте OCR со сканом и указывайте постоянный идентификатор страницы.')
add('limedia', 'Limédia — Lorraine digital collections and Kiosque', 'https://limedia.fr', 'FR', None, 'newspapers books directories', 'mixed',
    'Lorraine heritage collections; Kiosque provides free access to historical newspapers.',
    'Исторические коллекции Лотарингии; Kiosque даёт бесплатный доступ к старым газетам.',
    'Choose Kiosque for press, then title and date; access rules differ between Limédia services.',
    'Для газет выберите Kiosque, затем издание и дату; условия доступа у сервисов Limédia различаются.')
add('retronews', 'RetroNews — BnF historical press', 'https://www.retronews.fr', 'FR', None, 'newspapers', 'mixed',
    'Historical French press. BnF describes free archive consultation and subscription-based advanced features and editorial content.',
    'Историческая французская пресса. По данным BnF, архивы доступны бесплатно, расширенные функции и часть редакционных материалов — по подписке.',
    'Check title and issue dates; distinguish free archive pages from subscription-only search and editorial features.',
    'Уточняйте издание и дату номера; отличайте бесплатные архивные страницы от платных функций поиска и редакционных материалов.')
add('matchid', 'matchID — INSEE deceased-person files', 'https://deces.matchid.io', 'FR', None, 'vital', 'free',
    'Search of INSEE deceased-person files from 1970, including registered deaths in France and abroad.',
    'Поиск по файлам умерших INSEE с 1970 года, включая зарегистрированные смерти во Франции и за рубежом.',
    'Compare birth details and spelling variants. No match does not prove that a person did not die in France.',
    'Сверяйте сведения о рождении и варианты написания. Отсутствие совпадения не доказывает, что человек не умер во Франции.')
add('iverieli', 'Iverieli — National Parliamentary Library of Georgia', 'https://dspace.nplg.gov.ge', 'GE', None, 'books newspapers directories', 'mixed',
    'Digital collections of the National Parliamentary Library of Georgia.',
    'Цифровые коллекции Национальной парламентской библиотеки Грузии.',
    'Search titles and historical spellings; some collections are restricted to the library network. Inspect the page image.',
    'Ищите по заглавию и старому написанию; часть коллекций доступна только в сети библиотеки. Проверяйте скан страницы.')
add('polona', 'Polona — National Library of Poland', 'https://polona.pl', 'PL', None, 'books newspapers directories', 'mixed',
    'Digital books, periodicals and other collections of the National Library of Poland and partners.',
    'Оцифрованные книги, периодика и другие коллекции Национальной библиотеки Польши и партнёров.',
    'Check OCR against the scan, record the edition and page; item access may depend on rights.',
    'Сверяйте OCR со сканом, записывайте издание и страницу; доступ к предмету может зависеть от прав.')
add('spb_archives', 'Archives of Saint Petersburg', 'https://spbarchives.ru', 'RU', None, 'catalogs church vital directories', 'mixed',
    'Official portal of Saint Petersburg archives, fonds and archival reference services.',
    'Официальный портал архивов Санкт-Петербурга, фондов и архивных справочных сервисов.',
    'Identify the archive, fond, inventory and file. A catalogue entry does not guarantee free online images.',
    'Уточните архив, фонд, опись и дело. Каталожная запись не гарантирует бесплатные сканы онлайн.')
add('don_archives', 'Archives of the Don — Rostov region', 'https://donarch.ru', 'RU', None, 'catalogs church vital revision', 'mixed',
    'Official Rostov-region archival portal with fonds, register references and a virtual reading room.',
    'Официальный архивный портал Ростовской области: фонды, сведения о метриках и виртуальный читальный зал.',
    'Check the holding archive and inventory before opening scans; do not assume all Don records are digitised.',
    'Проверьте архив-держатель и опись перед просмотром; не считайте все документы Дона оцифрованными.')
add('dspl', 'Don State Public Library — digital library', 'https://elib.dspl.ru', 'RU', None, 'books newspapers directories', 'mixed',
    'Digital local-history books and periodicals of the Don State Public Library.',
    'Электронные краеведческие книги и периодика Донской государственной публичной библиотеки.',
    'Use the catalogue and its Vivaldi viewer; a book without searchable OCR still needs page-by-page inspection.',
    'Используйте каталог и связанный просмотрщик Vivaldi; книгу без поиска по OCR нужно просматривать постранично.')
add('pubmed', 'PubMed — biomedical bibliography', 'https://pubmed.ncbi.nlm.nih.gov', '*', None, 'books', 'free',
    'Biomedical bibliographic search, useful for historical physicians and authors; full texts are not always included.',
    'Библиографический поиск медицинских публикаций, полезный для исторических врачей и авторов; полные тексты есть не всегда.',
    'Disambiguate authors by dates, institution and coauthors. A namesake publication does not establish kinship.',
    'Различайте авторов по датам, учреждению и соавторам. Публикация однофамильца не устанавливает родство.')
add('cyberleninka', 'CyberLeninka — open scholarly articles', 'https://cyberleninka.ru', 'RU', None, 'books places', 'free',
    'Open-access scholarly articles, including local history and historical research.',
    'Научные статьи открытого доступа, в том числе по краеведению и истории.',
    'Use references to find originals; separate the author’s interpretation from a transcribed archival record.',
    'По ссылкам ищите оригиналы; отделяйте интерпретацию автора от выписки из архивного документа.')
add('rsl', 'Russian State Library — search catalogue', 'https://search.rsl.ru', 'RU', None, 'catalogs books directories newspapers', 'mixed',
    'RSL bibliographic catalogue; an entry may link to a digital copy with its own access conditions.',
    'Библиографический каталог РГБ; запись может вести к цифровой копии со своими условиями доступа.',
    'Search title, author and historical place; distinguish the shelfmark, catalogue description and full-text availability.',
    'Ищите по заглавию, автору и историческому месту; различайте шифр хранения, описание и доступ к полному тексту.')
add('wayback', 'Wayback Machine — archived web pages', 'https://web.archive.org', '*', None, 'catalogs books places', 'free',
    'Historical snapshots of websites, distinct from Internet Archive book full-text search.',
    'Исторические снимки сайтов, отдельные от полнотекстового поиска по книгам Internet Archive.',
    'Use the original URL and snapshot date. An archived page documents what was published then, not current availability.',
    'Указывайте исходный URL и дату снимка. Архивная страница показывает прежнюю публикацию, а не нынешнюю доступность.')
add('ukrfamily', 'UkrFamily — public archive references', 'https://ukrfamily.com.ua', 'UA', None, 'catalogs church revision', 'mixed',
    'Public archive inventories and genealogy reference pages alongside private research services.',
    'Публичные описи и генеалогические справочные страницы наряду с частными исследовательскими услугами.',
    'Verify archive, fond, opis and file against the official archive; viewing a public index does not authorise ordering services.',
    'Сверяйте архив, фонд, опис и справу с официальным архивом; просмотр индекса не разрешает заказ услуг.')
add('uk_wikisource', 'Ukrainian Wikisource', 'https://uk.wikisource.org', 'UA', None, 'books directories catalogs', 'free',
    'Volunteer transcriptions and digitised historical publications, sometimes linked to page scans.',
    'Волонтёрские расшифровки и исторические издания, иногда со связанными сканами страниц.',
    'Verify transcription against the scan and cite the original publication, volume and page.',
    'Сверяйте расшифровку со сканом, указывайте исходное издание, том и страницу.')
add('digibuc', 'DigiBuc — Bucharest Metropolitan Library', 'https://www.digibuc.ro', 'RO', None, 'newspapers books directories', 'mixed',
    'Bucharest Metropolitan Library digital collections; the portal redirects to its DigiTool service.',
    'Цифровые коллекции Столичной библиотеки Бухареста; портал перенаправляет в DigiTool.',
    'Check the title and issue, try Romanian diacritics and OCR variants. A timeout on the legacy portal is not a negative record search.',
    'Уточняйте издание и номер, пробуйте румынские диакритические знаки и варианты OCR. Тайм-аут старого портала не равен отрицательному поиску.')
add('bcu_cluj', 'Lucian Blaga Central University Library Cluj — digital library', 'https://dspace.bcucluj.ro', 'RO', None, 'books newspapers directories', 'mixed',
    'Digital books and periodicals of the Cluj university library.',
    'Электронные книги и периодика университетской библиотеки Клужа.',
    'Search titles and name variants; verify that the requested newspaper and year actually belong to this collection.',
    'Ищите заглавия и варианты имени; проверяйте, есть ли нужная газета и год именно в этой коллекции.')
add('moldavica', 'Moldavica — National Library of Moldova', 'https://moldavica.bnrm.md', 'MD', None, 'books newspapers directories', 'mixed',
    'National Library of Moldova digital heritage collections.',
    'Цифровые исторические коллекции Национальной библиотеки Молдовы.',
    'Inspect scanned issues if OCR is absent; label any locally generated OCR as a derivative, not the original text.',
    'При отсутствии OCR просматривайте сканы номеров; локальное распознавание помечайте как производный текст, а не оригинал.')
add('arcanum', 'Arcanum Digitheca', 'https://adt.arcanum.com', 'HU RO', None, 'newspapers books directories', 'mixed',
    'Digitised periodicals and books; access depends on the collection and subscription.',
    'Оцифрованные периодические издания и книги; доступ зависит от коллекции и подписки.',
    'Check the publication and access conditions. A blocked request or paywall is not evidence that a name is absent.',
    'Проверьте издание и условия доступа. Блокировка запроса или платный доступ не доказывает отсутствие имени.')
add('asp_moldova', 'Moldova ASP — civil-status services', 'https://www.asp.gov.md/ro/servicii/persoane-fizice/stare-civila', 'MD', None, 'vital', 'request',
    'Official civil-status service information of Moldova’s Public Services Agency; not a public person-search database.',
    'Официальные услуги гражданского состояния Агентства государственных услуг Молдовы; не публичная база поиска людей.',
    'Check eligibility and required documents. Record an owner task for restricted certificates; do not submit an application automatically.',
    'Проверьте право на получение и нужные документы. Для закрытых актов ставьте задачу владельцу; заявление автоматически не отправляйте.')
add('patronim', 'Patronim — genealogy website directory', 'https://patronim.ru', 'RU', None, 'catalogs', 'free',
    'Directory of genealogy and local-history websites, not an indexed person database.',
    'Каталог генеалогических и краеведческих сайтов, а не индекс людей.',
    'Use it to discover resources; verify each destination and do not treat directory search as a surname search in records.',
    'Используйте для поиска ресурсов; проверяйте каждый сайт и не считайте поиск по каталогу поиском фамилии в документах.')
add('famiry', 'Famiry — user family trees', 'https://famiry.ru', 'RU', None, 'trees', 'mixed',
    'Family-tree service with account-dependent access; public surname articles are not individual records.',
    'Сервис семейных деревьев с доступом через учётную запись; публичные статьи о фамилии не являются записями о человеке.',
    'Inspect attached documents after authorised login; a blocked tree is an incomplete check, not a no-hit result.',
    'После разрешённого входа изучайте документы; недоступное древо — незавершённая проверка, а не отсутствие совпадений.')
add('familyspace', 'FamilySpace — genealogy community and trees', 'https://familyspace.ru', 'RU', None, 'trees', 'mixed',
    'User-contributed genealogy service; availability and visibility require checking.',
    'Пользовательский генеалогический сервис; доступность и видимость данных нужно проверять.',
    'Use public material only as leads; account requirements or an unavailable site must be logged separately from no matches.',
    'Публичные материалы используйте только как наводки; требование входа и недоступность записывайте отдельно от отсутствия находок.')

for entry in S:
    if entry['id'] == 'khmelnytsky_archive':
        entry['availability_note'] = '2026-10-21: the former PDF URL /pdf/mbv8-b1.pdf returned a hosting suspension page. Recheck the official archive directory; this is not a completed record search.'
        entry['availability_note_ru'] = '21.10.2026: прежний PDF /pdf/mbv8-b1.pdf вернул заглушку хостинга. Перепроверьте адрес в официальном справочнике архивов; это не выполненный поиск документов.'
    if entry['id'] == 'wikipedia':
        entry['how'] += ' For images use https://commons.wikimedia.org and check the license on the individual file page.'
        entry['how_ru'] += ' Иллюстрации ищите на https://commons.wikimedia.org; лицензию проверяйте на странице конкретного файла.'

out = Path(__file__).resolve().parent.parent / "src" / "genealogy_mcp" / "data" / "sources.json"
ids = [s["id"] for s in S]
assert len(ids) == len(set(ids)), "duplicate ids"
out.write_text(json.dumps(S, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(S), "sources →", out)
