"""Drafts of requests to archives and registry offices. A draft only: the user reads, completes and sends it."""

KINDS = {
    "zags": ("Registry office (ZAGS): a copy of a birth/marriage/death record", "ЗАГС: повторное свидетельство или архивная справка"),
    "state_archive": ("State (regional) archive: genealogical search in parish registers, revision lists, etc.", "Госархив: генеалогический поиск по метрикам, ревизиям и др."),
    "military": ("Military archive (TsAMO, RGVA, RGVIA): service and losses", "Военный архив (ЦАМО, РГВА, РГВИА): служба и потери"),
    "repression": ("FSB / MVD / SBU archive: investigation or deportation file", "Архив ФСБ / МВД / СБУ: следственное дело или дело о выселении"),
    "generic_en": ("Any archive, in English", "Любой архив, по-английски"),
    "generic_es": ("Any archive, in Spanish (Latin America, Spain)", "Любой архив, по-испански"),
    "generic_pt": ("Any archive, in Portuguese (Brazil, Portugal)", "Любой архив, по-португальски"),
}


def _v(x, placeholder):
    return str(x).strip() if x not in (None, "") else f"[{placeholder}]"


def draft(kind, requester="", requester_address="", relation="", person="", born="", birth_place="", died="", death_place="",
          parents="", spouse="", what="", years="", place="", details="", archive=""):
    """Returns {"subject", "body", "attach", "notes"}."""
    kind = kind if kind in KINDS else "generic_en"
    p = _v(person, "ФИО" if kind in ("zags", "state_archive", "military", "repression") else "full name")
    if kind == "zags":
        subject = "Заявление о выдаче повторного свидетельства / архивной справки"
        body = f"""В {_v(archive, "отдел ЗАГС … (по месту регистрации) / архив ЗАГС области")}
от {_v(requester, "ваши ФИО")}, {_v(requester_address, "почтовый адрес, телефон, e-mail")}

ЗАЯВЛЕНИЕ

Прошу выдать {_v(what, "повторное свидетельство о рождении / архивную справку о рождении (браке, смерти)")} в отношении
{p}, {_v(born, "дата рождения")} г. р., место рождения: {_v(birth_place, "место")}.
Родители: {_v(parents, "ФИО родителей, если известны")}.
{("Дата и место смерти: " + died + (", " + death_place if death_place else "") + ".") if died else ""}
Предполагаемые годы и место регистрации: {_v(years, "годы")}, {_v(place, "населённый пункт, район")}.

Я прихожусь {p}: {_v(relation, "кем (внук/внучка …)")}. Родство подтверждают прилагаемые документы.
{details}

Прилагаю: копию паспорта; копии свидетельств о рождении (браке), подтверждающих родство по цепочке.

{_v(requester, "ФИО")}, дата, подпись"""
        attach = ["копия паспорта", "свидетельства о рождении/браке, подтверждающие родство по цепочке", "для умерших — свидетельство о смерти"]
        notes = ["Повторное свидетельство на умершего родственника выдают только наследникам и при подтверждении родства; "
                 "архивная справка — шире. Записи старше 100 лет обычно переданы в госархив — тогда пишите туда.",
                 "Через Госуслуги можно подать запрос в ЗАГС о повторном документе."]
    elif kind == "state_archive":
        subject = "Запрос генеалогического характера"
        body = f"""В {_v(archive, "Государственный архив … области")}
от {_v(requester, "ваши ФИО")}, {_v(requester_address, "почтовый адрес, e-mail, телефон")}

Прошу провести поиск и выдать архивную справку (копии документов) о {_v(what, "рождении / браке / составе семьи по ревизским сказкам …")}
в отношении {p}, {_v(born, "год рождения или период")}, {_v(birth_place, "губерния, уезд, волость, село / приход")}.

Известные сведения: родители — {_v(parents, "ФИО")}; супруг(а) — {_v(spouse, "ФИО")}; сословие и занятие — {_v(details, "крестьянин / мещанин …")}.
Прошу просмотреть: метрические книги церкви {_v(place, "название церкви, село")} за {_v(years, "годы")} гг.;
при наличии — исповедные ведомости и ревизские сказки за те же годы.

Я прихожусь {p}: {_v(relation, "правнук / правнучка …")}. Цель — составление родословной. Оплату по прейскуранту архива
гарантирую; прошу сообщить предварительную стоимость.

{_v(requester, "ФИО")}, дата"""
        attach = ["копия паспорта (если архив требует)"]
        notes = ["Сначала проверьте путеводитель архива (guides.rusarchives.ru) и сайт: многие архивы принимают запросы онлайн и называют "
                 "стоимость. Для документов старше 75 лет родство обычно доказывать не нужно.",
                 "Чем точнее приход и годы, тем дешевле и быстрее поиск: назовите церковь, если знаете."]
    elif kind == "military":
        subject = "Запрос о прохождении службы / судьбе военнослужащего"
        body = f"""В {_v(archive, "Центральный архив Министерства обороны РФ (ЦАМО), 142100, г. Подольск, ул. Кирова, 74")}
от {_v(requester, "ваши ФИО")}, {_v(requester_address, "почтовый адрес")}

Прошу сообщить сведения о прохождении военной службы {_v(what, "и судьбе (место гибели, захоронения) / награждениях")}
{p}, {_v(born, "год рождения")} г. р., уроженца {_v(birth_place, "место рождения")}, призванного {_v(details, "кем (… РВК) и когда")}.
Известные сведения: {_v(years, "годы службы, часть, звание, номер полевой почты из писем")}.

Я прихожусь ему {_v(relation, "внуком / внучкой …")}. Прилагаю копии документов о родстве.

{_v(requester, "ФИО")}, дата, подпись"""
        attach = ["копии документов о родстве", "копии писем с фронта, справок, извещений (если есть)"]
        notes = ["Сначала найдите все записи в «Памяти народа» и ОБД «Мемориал»: они дают номер части, а с ним архив ответит точнее.",
                 "Первая мировая — РГВИА (Москва); РККА 1918–1940 — РГВА."]
    elif kind == "repression":
        subject = "Заявление об ознакомлении с архивным уголовным делом"
        body = f"""В {_v(archive, "Управление ФСБ России по … области / Информационный центр МВД / архив СБУ")}
от {_v(requester, "ваши ФИО")}, {_v(requester_address, "почтовый адрес")}

Прошу ознакомить меня с архивным уголовным делом (делом о выселении) в отношении моего родственника —
{p}, {_v(born, "год рождения")} г. р., уроженца {_v(birth_place, "место")}, {_v(details, "арестован … / выселен … (по данным базы «Открытый список» / «Жертвы политического террора»)")},
и выдать копии документов, включая фотографии, и справку о реабилитации.

Я прихожусь ему {_v(relation, "внуком / правнучкой …")}; родство подтверждают прилагаемые документы.

{_v(requester, "ФИО")}, дата, подпись"""
        attach = ["копия паспорта", "цепочка свидетельств о рождении/браке от заявителя до репрессированного", "свидетельство о смерти (если есть)"]
        notes = ["Дела реабилитированных выдают родственникам; без родства — через 75 лет после создания дела.",
                 "Номер дела и архив часто указаны в «Открытом списке» и базе «Мемориала» — укажите их."]
    elif kind == "generic_es":
        subject = "Solicitud de búsqueda genealógica"
        body = f"""A: {_v(archive, "Archivo / Registro Civil / Parroquia …")}

Estimados señores:

Me dirijo a ustedes para solicitar {_v(what, "una copia (o transcripción) del acta de bautismo / nacimiento / matrimonio / defunción")}
de {p}, nacido(a) {_v(born, "fecha o año aproximado")} en {_v(birth_place, "lugar")}.
Padres: {_v(parents, "nombres")}. Cónyuge: {_v(spouse, "nombre")}.
Años y lugar a revisar: {_v(years, "años")}, {_v(place, "parroquia / municipio")}. {details}

Soy {_v(relation, "bisnieto(a)")} de la persona mencionada; la información es para una investigación genealógica familiar.
Les agradecería que me indicaran el costo y la forma de pago.

Atentamente,
{_v(requester, "nombre")}
{_v(requester_address, "dirección, correo electrónico")}"""
        attach = ["copia de documento de identidad (si lo piden)"]
        notes = ["Before writing, check FamilySearch: most Latin American parish and civil registers are filmed and free to view."]
    elif kind == "generic_pt":
        subject = "Pedido de pesquisa genealógica"
        body = f"""Para: {_v(archive, "Arquivo / Cartório de Registro Civil / Paróquia …")}

Prezados senhores,

Venho solicitar {_v(what, "uma certidão de inteiro teor (ou cópia) do registro de batismo / nascimento / casamento / óbito")}
de {p}, nascido(a) em {_v(born, "data ou ano aproximado")}, em {_v(birth_place, "local")}.
Pais: {_v(parents, "nomes")}. Cônjuge: {_v(spouse, "nome")}.
Anos e local a pesquisar: {_v(years, "anos")}, {_v(place, "paróquia / município")}. {details}

Sou {_v(relation, "bisneto(a)")} da pessoa mencionada; a pesquisa é para fins genealógicos familiares.
Agradeço se puderem informar o custo e a forma de pagamento.

Atenciosamente,
{_v(requester, "nome")}
{_v(requester_address, "endereço, e-mail")}"""
        attach = ["cópia de documento de identidade (se exigido)"]
        notes = ["In Brazil a «certidão de inteiro teor» copies the whole record, including the parents and grandparents."]
    else:
        subject = "Genealogical research request"
        body = f"""To: {_v(archive, "Archive / Registry office / Parish …")}

Dear Sir or Madam,

I am researching my family history and would be grateful for {_v(what, "a copy of the birth (baptism) / marriage / death record")}
of {p}, born {_v(born, "date or approximate year")} in {_v(birth_place, "place")}.
Parents: {_v(parents, "names")}. Spouse: {_v(spouse, "name")}.
Years and place to search: {_v(years, "years")}, {_v(place, "parish / town")}. {details}

I am {_v(relation, "the great-grandson / great-granddaughter")} of this person. Please let me know the fee and how to pay.

Yours faithfully,
{_v(requester, "name")}
{_v(requester_address, "address, e-mail")}"""
        attach = ["a copy of an ID (if required)", "documents proving the relationship (for records under privacy rules)"]
        notes = ["Most archives publish a request form and fees on their website — use the form when there is one."]
    body = "\n".join(line.rstrip() for line in body.splitlines())
    return {"kind": kind, "subject": subject, "body": body, "attach": attach, "notes": notes,
            "warning": "A draft: check every [bracket], add what you know, and send it yourself."}
